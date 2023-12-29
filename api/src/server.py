import random
from pathlib import Path
import requests
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_DIR = Path(__file__).parent
PROFILES_DIR = Path(DEFAULT_DIR, "profiles")

def signUp(client: dict) -> (str, True | False):
    if os.path.exists(Path(PROFILES_DIR, str(client["name"]) + ".json")):
            return "User already exists", False

    client["password"] = generate_password_hash(client["password"])
    # setup user profile and local quizzes dir
    with open(Path(PROFILES_DIR, client["name"] + ".json"), "w") as f:
        f.write(json.dumps(client))

    with open(Path(DEFAULT_DIR, "valid_api_keys.json"), "r+") as f: 
        keys = json.loads(f.read()) | {client["api_key"]: client["name"]}

        f.seek(0)
        f.write(json.dumps(keys))
        f.truncate()
    
    return "Sign up successful", client["api_key"]

def login(name: str, password: str) -> (str, str | None):
    if os.path.exists(Path(PROFILES_DIR, str(name) + ".json")):
        with open(Path(PROFILES_DIR, str(name) + ".json"), "r") as info:
            profile = json.loads(info.read())
            correct = check_password_hash(profile['password'], password)
            
            if correct:
                return "Succesfully logged in", profile["api_key"]
            else:
                return "Password is incorrect", None
    else:
        return "User does not exist!", None

def createQuiz(
    path: Path, amount: int = 10, category: str = "General Knowledge", difficulty: int = 0, type: int = 0, 
    name: str = ''.join(['abcdefghijklmnopqrztuvwxyz'[random.randint(0, 25)] for _ in range(6)]),
) -> None:
    
    params = {
        "amount": amount,
        "category": OPENTDB_API["categories"][category],
        "difficulty": OPENTDB_API["difficulty"][difficulty],
        "type": OPENTDB_API["type"][type]
    }

    url = "https://opentdb.com/api.php"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        with open(Path(path, "local", name + ".json"), "w") as f:
            f.write(json.dumps(response.json()))
            print("New Quiz pack created successfully!")
    else:
        print(f"Failed to fetch API. Status code: {response.status_code}")
