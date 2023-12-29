import os
from flask import Flask, request, jsonify
from flask_oauthlib.provider import OAuth2Provider
from flask_talisman import Talisman
from flask_cors import CORS
import uuid
from pathlib import Path
import json
import src.server as auth

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
CORS(app)

API_KEYS_DIR = Path(Path(__file__).parent, "src", "valid_api_keys.json")
with open(API_KEYS_DIR, "r") as f:
    VALID_KEYS = json.loads(f.read())

oauth = OAuth2Provider(app)  # Instantiate OAuth2Provider

talisman = Talisman(
    app, content_security_policy={"default-src": "'self'"}, force_https=True
)


# API key authentication middleware
def api_key_auth():
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in VALID_KEYS:
        return jsonify({"error": "Unauthorized"}), 401

# Endpoint to dynamically register a new client
@app.route("/signup", methods=["POST"])
def register_client():
    data = request.get_json()
    expected = ["name", "password", "team"]
    if not (list(data) == expected):
        return jsonify({"error": "Invalid request, missing expected parameter"}), 400
    
    teams = ['ngata', 'rutherford', 'britten', 'blake', "cooper", "sheppard"]
    if data["team"].lower() in teams:
        team = {"team": data["team"].lower() }
    else:
        return jsonify({"error": "Invalid request, unexpected team"}), 400

    api_key = str(uuid.uuid4())
    new_client = data | {"api_key": api_key, "active_quizzes": {}, "points": 0} | team
    message, access = auth.signUp(new_client)
    if not access:
        return jsonify({"error": message}), 400
    
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
    # print(request.__dict__)
    data = request.get_json()
    expected = ["name", "password"]
    if not (list(data) == expected):
        return jsonify({"error": "Invalid request, missing expected parameter"}), 400

    message, access = auth.login(data["name"], data["password"])
    if not access:
        print(message)
        return jsonify({"error": message}), 400
    
    with open(Path(auth.PROFILES_DIR, data["name"] + ".json"), "r") as f:
        api_key = json.loads(f.read())["api_key"]
    return jsonify({"api_key": api_key}), 201

@app.route("/get_score", methods=["GET"])
def get_score():
    api_key_auth()
    with open(Path(auth.PROFILES_DIR, VALID_KEYS[request.headers.get("X-API-Key")] + ".json"), "r") as f:
        return jsonify({"score": json.loads(f.read())["points"]}), 201

@app.route("/render_quiz", methods=["GET"])
def render_quiz():
    api_key_auth()
    data = request.get_json()
    expected = ["quiz_name"]
    if not (list(data) == expected):
        return jsonify({"error": "Invalid request, missing expected parameter"}), 400

    user = VALID_KEYS[request.headers.get("X-API-Key")]
    with open(Path(auth.PROFILES_DIR, user + ".json"), "r") as f:
        route = json.loads(f.read())
        question = route[data["quiz_name"]]["results"][route["index"]]

        options = question["incorrect_answers"] + question["correct_answer"]
        del question["incorrect_answers"]
        del question["correct_answers"]

    return jsonify(data=question | options), 200

@app.route("/render_leaderboard", methods=["GET"])
def render_leaderboard():
    api_key_auth()
    with open(Path(auth.DEFAULT_DIR, "teams.json"), "r") as f:
        leaderboard = json.loads(f.read())
    return jsonify(data=leaderboard), 200

@app.route("/start_quiz", methods=["POST", "OPTIONS"])
def start_quiz():

    if request.method == "OPTIONS":
        # Handle OPTIONS request
        response = jsonify({"status": 200})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    api_key_auth()
    data = request.get_json()
    expected = ["quiz_name", "quiz"]
    if not (list(data) == expected):
        return jsonify({"error": "Invalid request, missing expected parameter"}), 400
    
    user = VALID_KEYS[request.headers.get("X-API-Key")]
    with open(Path(auth.PROFILES_DIR, user + ".json"), "r+") as f:
        route = json.loads(f.read())
        route["active_quizzes"][data["quiz_name"]] = data["quiz"] | {"index": 0}
        if len(route["active_quizzes"]) > 5:
            del route["active_quizzes"][0]

        f.seek(0)
        f.write(json.dumps(route))
        f.truncate()
    
    return jsonify({"status": "Competitive mode quiz successfully added"}), 200

@app.route("/answer_quiz", methods=["POST", "OPTIONS"])
def answer_quiz():
    if request.method == "OPTIONS":
        # Handle OPTIONS request
        response = jsonify({"status": "success"})
        response.headers.add("Allow", "POST")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    # Handle actual POST request
    api_key_auth()
    data = request.get_json()
    expected = ["quiz_name", "selected"]
    if not (list(data) == expected):
        return jsonify({"error": "Invalid request, missing expected parameter"}), 400

    user = VALID_KEYS[request.headers.get("X-API-Key")]
    with open(Path(auth.PROFILES_DIR, user + ".json"), "r+") as f:
        route = json.loads(f.read())
        question = route["active_quizzes"][data["quiz_name"]]

        #if question["index"]-1 == len(question["results"]):

        print(question["results"][question["index"]]["correct_answer"])
        print(data["selected"])
        if question["results"][question["index"]]["correct_answer"] == data["selected"]:
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

            return jsonify({"status":"Correct Answer"}), 200
        
        route["active_quizzes"][data["quiz_name"]]["index"] += 1

        f.seek(0)
        f.write(json.dumps(route))
        f.truncate()
    return jsonify({"status":"Wrong Answer"}), 200



if __name__ == "__main__":
    app.run(debug=True)  # , ssl_context='adhoc')
