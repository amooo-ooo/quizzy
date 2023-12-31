from pathlib import Path
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_DIR = Path(__file__).parent
PROFILES_DIR = Path(DEFAULT_DIR, "profiles")


def signUp(client: dict) -> (str, True | False):
    """Sign up user online"""
    if os.path.exists(Path(PROFILES_DIR, str(client["name"]) + ".json")):
        return "User already exists", False

    client["password"] = generate_password_hash(client["password"])

    # add user profile on the server
    with open(Path(PROFILES_DIR, client["name"] + ".json"), "w") as f:
        f.write(json.dumps(client))

    # append their valid key to other api keys
    with open(Path(DEFAULT_DIR, "valid_api_keys.json"), "r+") as f:
        keys = json.loads(f.read()) | {client["api_key"]: client["name"]}

        f.seek(0)
        f.write(json.dumps(keys))
        f.truncate()

    return "Sign up successful", client["api_key"]


def login(name: str, password: str) -> (str, str | None):
    """Log in user"""
    # check if user exist
    if os.path.exists(Path(PROFILES_DIR, str(name) + ".json")):
        with open(Path(PROFILES_DIR, str(name) + ".json"), "r") as info:
            profile = json.loads(info.read())
            correct = check_password_hash(profile["password"], password)

            # check if password correct
            if correct:
                return "Succesfully logged in", profile["api_key"]
            else:
                return "Password is incorrect", None
    else:
        return "User does not exist!", None
