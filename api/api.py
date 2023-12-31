import os
from flask import Flask, request, jsonify
from flask_oauthlib.provider import OAuth2Provider
from flask_talisman import Talisman
from flask_cors import CORS
import uuid
from pathlib import Path
import json
import src.server as auth
import sys
import argparse

# set up flask API
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
# enables CORS
CORS(app)

# use argeparse for file logs
parser = argparse.ArgumentParser()
parser.add_argument(
    "--logfile",
    type=bool,
    default=False,
    help="Instead of printing logs onto the terminal, log into file.",
)
args = parser.parse_args()

if args.logfile:
    log_file = open("log.txt", "wt")
    sys.stdout = sys.stderr = log_file

    @app.teardown_appcontext
    def close_log_file(error):
        log_file.close()

# load valid API keys
API_KEYS_DIR = Path(Path(__file__).parent, "src", "valid_api_keys.json")
with open(API_KEYS_DIR, "r") as f:
    VALID_KEYS = json.loads(f.read())

infinite_sessions = {}
oauth = OAuth2Provider(app)

talisman = Talisman(
    app, content_security_policy={"default-src": "'self'"}, force_https=True
)


def api_key_auth():
    """Authenticate User"""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in VALID_KEYS:
        return jsonify({"error": "Unauthorized"}), 401


@app.route("/signup", methods=["POST"])
def register_client():
    """User account sign up"""
    data = request.get_json()

    # check for all params
    expected = ["name", "password", "team"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    # check team selected is valid
    teams = ["ngata", "rutherford", "britten", "blake", "cooper", "sheppard"]
    if data["team"].lower() in teams:
        team = {"team": data["team"].lower()}
    else:
        return jsonify({"error": "Invalid request, unexpected team"}), 400

    # generate random API Key
    api_key = str(uuid.uuid4())
    new_client = data | {"api_key": api_key,
                         "active_quizzes": {}, "points": 0} | team
    message, access = auth.signUp(new_client)
    if not access:
        return jsonify({"error": message}), 400

    # save API key and user
    with open(API_KEYS_DIR, "r+") as f:
        route = json.loads(f.read()) | {api_key: data["name"]}
        f.seek(0)
        f.write(json.dumps(route))
        f.truncate()

    global VALID_KEYS
    VALID_KEYS |= {api_key: data["name"]}
    return jsonify({"api_key": api_key}), 201


@app.route("/login", methods=["POST"])
def login_client():
    """Log in client"""
    data = request.get_json()

    # check expected params
    expected = ["name", "password"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    # check password is correct
    message, access = auth.login(data["name"], data["password"])
    if not access:
        print(message)
        return jsonify({"error": message}), 400

    # if given access, load user info
    with open(Path(auth.PROFILES_DIR, data["name"] + ".json"), "r") as f:
        api_key = json.loads(f.read())["api_key"]
    return jsonify({"api_key": api_key}), 201


@app.route("/get_score", methods=["GET"])
def get_score():
    """Give score"""
    api_key_auth()
    with open(
        Path(auth.PROFILES_DIR,
             VALID_KEYS[request.headers.get("X-API-Key")] + ".json"),
        "r",
    ) as f:
        return jsonify({"score": json.loads(f.read())["points"]}), 201


@app.route("/render_leaderboard", methods=["GET"])
def render_leaderboard():
    """Get Leaderboard"""
    api_key_auth()
    with open(Path(auth.DEFAULT_DIR, "teams.json"), "r") as f:
        leaderboard = json.loads(f.read())
    return jsonify(data=leaderboard), 200


@app.route("/start_infinite_quiz", methods=["POST", "OPTIONS"])
def start_infinite_quiz():
    """Start infinite quiz session"""
    if request.method == "OPTIONS":
        response = jsonify({"status": 200})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()

    # expected params
    expected = ["questions", "lives"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    global infinite_sessions
    infinite_sessions[request.headers.get("X-API-Key")] = data
    return jsonify({"status": "Infinite Quiz Ready"}), 200


@app.route("/expand_infinite_quiz", methods=["POST", "OPTIONS"])
def expand_infinite_quiz():
    """Expand the user's infinite quiz session"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()
    expected = ["questions"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    global infinite_sessions
    api_key = request.headers.get("X-API-Key")
    # append the live session
    infinite_sessions[api_key]["questions"].append(data)
    return jsonify({"status": "Quiz Appended"}), 200


@app.route("/answer_infinite_quiz", methods=["POST", "OPTIONS"])
def answer_infinite_quiz():
    """Answer an infinite gamemode question"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()
    expected = ["selected"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    api_key = request.headers.get("X-API-Key")
    global infinite_sessions
    question = infinite_sessions[api_key]["questions"][0]
    user = VALID_KEYS[api_key]

    # delete question
    del infinite_sessions[api_key]["questions"][0]

    # check if correct
    if question["correct_answer"] == data["selected"]:
        # if correct add score to user and their house team
        with open(Path(auth.PROFILES_DIR, user + ".json"), "r+") as teams:
            user_info = json.loads(teams.read())
            user_info["points"] += 1

            teams.seek(0)
            teams.write(json.dumps(user_info))
            teams.truncate()

        with open(Path(auth.DEFAULT_DIR, "teams.json"), "r+") as teams:
            team = json.loads(teams.read())
            team[user_info["team"]]["points"] += 1

            teams.seek(0)
            teams.write(json.dumps(team))
            teams.truncate()

        return (
            jsonify(
                {
                    "status": "Correct Answer",
                    "lives": infinite_sessions[api_key]["lives"],
                }
            ),
            200,
        )

    # if question is wrong, lose 1 life
    infinite_sessions[api_key]["lives"] -= 1
    return (
        jsonify(
            {"status": "Wrong Answer",
             "lives": infinite_sessions[api_key]["lives"]}
        ),
        200,
    )


@app.route("/start_quiz", methods=["POST", "OPTIONS"])
def start_quiz():
    """Start traditional quiz"""
    if request.method == "OPTIONS":
        response = jsonify({"status": 200})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()
    expected = ["quiz_name", "quiz"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    # save quiz session to a file
    user = VALID_KEYS[request.headers.get("X-API-Key")]
    with open(Path(auth.PROFILES_DIR, user + ".json"), "r+") as f:
        route = json.loads(f.read())
        route["active_quizzes"][data["quiz_name"]] = (data["quiz"]
                                                      | {"index": 0})
        if len(route["active_quizzes"]) > 5:
            del route["active_quizzes"][0]

        f.seek(0)
        f.write(json.dumps(route))
        f.truncate()

    return jsonify({"status": "Competitive mode quiz successfully added"}), 200


@app.route("/answer_quiz", methods=["POST", "OPTIONS"])
def answer_quiz():
    """Answer quiz in traditional game mode"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()
    expected = ["quiz_name", "selected"]
    if not (list(data) == expected):
        return jsonify({"error":
                        "Invalid request, missing expected parameter"}), 400

    # open up quiz
    user = VALID_KEYS[request.headers.get("X-API-Key")]
    with open(Path(auth.PROFILES_DIR, user + ".json"), "r+") as f:
        route = json.loads(f.read())
        question = route["active_quizzes"][data["quiz_name"]]

        # check if correct
        correct = question["results"][question["index"]]["correct_answer"]
        if (correct == data["selected"]):
            # if correct add a point to user and their house team
            route["points"] += 1
            with open(Path(auth.DEFAULT_DIR, "teams.json"), "r+") as teams:
                team = json.loads(teams.read())
                team[route["team"]]["points"] += 1

                teams.seek(0)
                teams.write(json.dumps(team))
                teams.truncate()

            route["active_quizzes"][data["quiz_name"]]["index"] += 1
            f.seek(0)
            f.write(json.dumps(route))
            f.truncate()

            return jsonify({"status": "Correct Answer"}), 200

        route["active_quizzes"][data["quiz_name"]]["index"] += 1

        f.seek(0)
        f.write(json.dumps(route))
        f.truncate()

    # otherwise return wrong answer
    return jsonify({"status": "Wrong Answer"}), 200


if __name__ == "__main__":
    app.run()
