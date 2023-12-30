import random
from pathlib import Path
from hashlib import sha256
import requests
import json
import os


with open(Path(Path(__file__).parent, "opentdb.json"), "r") as f:
    OPENTDB_API = json.loads(f.read())

DEFAULT_DIR = Path(__file__).parent
PROFILES_DIR = Path(DEFAULT_DIR, "profiles")


class Profile:
    """Profile class"""
    def __init__(
        self, name: str, password: str, path: Path = None, exist: bool = False
    ):
        self.name = name
        self.password = sha256(password.encode("utf-8")).hexdigest()

        if not exist:
            self.setup_dir()
        else:
            self.path = path

    def setup_dir(self) -> Path:
        """Setup directory if user is new"""
        profile = {"name": self.name, "password": self.password}

        self.path = Path(PROFILES_DIR, self.name)

        # make user info file
        os.makedirs(Path(self.path))
        with open(Path(self.path, "user.json"), "w") as f:
            f.write(json.dumps(profile))

        # copy default sample quiz
        os.makedirs(Path(self.path, "local"))
        with open(Path(self.path, "local",
                       "default.json"), "w") as profile_quiz:
            with open(Path(DEFAULT_DIR, "default.json"), "r") as default_quiz:
                profile_quiz.write(default_quiz.read())


def signUp(
    name: str, password: str, team: str, api: str = "http://127.0.0.1:5000"
) -> (dict, str) or (None, str):
    """Sign up a new user"""
    headers = {"Content-Type": "application/json"}
    data = {"name": name, "password": password, "team": team}

    try:
        # try signing up as  anew user
        response = requests.post(
            f"{api}/signup", data=json.dumps(data), headers=headers
        )
        api_key = response.json()["api_key"]
        online = True
    except requests.exceptions.ConnectionError as e:
        # fail to connect to API
        online = False
        error = e

    if not online:
        return (
            None,
            ("Unable to connect to back-end API " +
             f"to create an account! Error: {error}"),
        )

    if os.path.exists(Path(PROFILES_DIR, str(name))):
        return (None, "User already exists!")

    return (
        {"profile": Profile(name, password),
         "api_key": api_key if online else None},
        "Successfully Signed Up!",
    )


def login(name: str, password: str) -> (dict, str) or (None, str):
    headers = {"Content-Type": "application/json"}
    data = {"name": name, "password": password}
    api = "http://127.0.0.1:5000"
    try:
        response = requests.post(f"{api}/login",
                                 data=json.dumps(data), headers=headers)
        api_key = response.json()["api_key"]
        online = True
    except requests.exceptions.ConnectionError:
        print("Offline Mode")
        online = False

    if os.path.exists(Path(PROFILES_DIR, str(name))):
        with open(Path(PROFILES_DIR, str(name), "user.json"), "r") as info:
            profile = json.loads(info.read())
            passhash = sha256(password.encode("utf-8")).hexdigest()
            correct = (
                profile["password"] == passhash
            )

            if correct:
                return (
                    {
                        "profile": Profile(
                            name,
                            password,
                            path=Path(PROFILES_DIR, str(name)),
                            exist=True,
                        ),
                        "api_key": api_key if online else None,
                    },
                    "Succesfully logged in!",
                )
            else:
                return (None, "Password is incorrect!")
    else:
        return (None, "User does not exist!")


def createQuiz(
    path: Path,
    amount: int = 10,
    category: str = "General Knowledge",
    difficulty: int = 0,
    type: int = 0,
    name: str = "".join(
        ["abcdefghijklmnopqrztuvwxyz"[random.randint(0, 25)] for _ in range(6)]
    ),
) -> None:
    params = {
        "amount": amount,
        "category": OPENTDB_API["categories"][category],
        "difficulty": OPENTDB_API["difficulty"][difficulty],
        "type": OPENTDB_API["type"][type],
    }

    url = "https://opentdb.com/api.php"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        with open(Path(path, "local", name + ".json"), "w") as f:
            js = response.json()
            f.write(
                json.dumps(js | {"category":
                                 js["results"][0]["category"]}).replace(
                    "Entertainment: ", ""
                )
            )
            print("New Quiz pack created successfully!")
    else:
        print(f"Failed to fetch API. Status code: {response.status_code}")
