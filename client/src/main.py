import random
from pathlib import Path
from hashlib import sha256
import requests
import json
import os

#from lib.profile import Profile, login, signUp

with open(Path(Path(__file__).parent, "opentdb.json"), "r") as f:
    OPENTDB_API = json.loads(f.read())

DEFAULT_DIR = Path(__file__).parent
PROFILES_DIR = Path(DEFAULT_DIR, "profiles")

class Profile:
    def __init__(self, name: str, password: str, path: Path = None, exist: bool = False):
        self.name = name
        self.password = sha256(password.encode('utf-8')).hexdigest()

        if not exist:
            self.setup_dir()
        else:
            self.path = path

    def setup_dir(self) -> Path:
        profile = {"name": self.name,
                   "password": self.password}
        
        # setup user profile and local quizzes dir
        self.path = Path(PROFILES_DIR, self.name)

        os.makedirs(Path(self.path))
        with open(Path(self.path, "user.json"), "w") as f:
            f.write(json.dumps(profile))
        
        os.makedirs(Path(self.path, "local"))
        with open(Path(self.path, "local", "default.json"), "w") as profile_quiz:
            with open(Path(DEFAULT_DIR, "default.json"), "r") as default_quiz:
                profile_quiz.write(default_quiz.read())

        with open(Path(self.path, "recents.json"), "w") as user_recents:
            with open(Path(DEFAULT_DIR, "recents.json"), "r") as default_recents:
                user_recents.write(default_recents.read())

def signUp(name: str, password: str, team: str, api: str = "http://127.0.0.1:5000") -> (dict, str) or (None, str):
    headers = {'Content-Type': 'application/json'}
    data = { 'name': name, 'password': password, 'team': team }
    
    try:
        response = requests.post(f'{api}/signup', data=json.dumps(data), headers=headers)
        api_key = response.json()["api_key"]
        online = True
    except requests.exceptions.ConnectionError as e:
        online = False
        error = e

    if not online:
        return (None, f"Unable to connect to back-end API to create an account! Error: {error}")

    if os.path.exists(Path(PROFILES_DIR, str(name))):
        return (None, "User already exists!")

    return ({"profile": Profile(name, password), "api_key": api_key if online else None}, "Successfully Signed Up!")

def login(name: str, password: str) -> (dict, str) or (None, str):
        headers = {'Content-Type': 'application/json'}
        data = { 'name': name, 'password': password }
        api = "http://127.0.0.1:5000" # local host
        try:
            response = requests.post(f'{api}/login', data=json.dumps(data), headers=headers)
            api_key = response.json()["api_key"]
            online = True
        except requests.exceptions.ConnectionError:
            print("Offline Mode")
            online = False

        if os.path.exists(Path(PROFILES_DIR, str(name))):
            with open(Path(PROFILES_DIR, str(name), "user.json"), "r") as info:
                profile = json.loads(info.read())
                correct = profile['password'] == sha256(password.encode('utf-8')).hexdigest()
                
                if correct:
                    return ({"profile": Profile(name, password, 
                                            path=Path(PROFILES_DIR, str(name)), exist=True), 
                            "api_key": api_key if online else None}, "Succesfully logged in!")
                else:
                    return (None, "Password is incorrect!")
        else:
            return (None, "User does not exist!")


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
            js = response.json()
            f.write(json.dumps(js | {"category": js["results"][0]["category"]}).replace("Entertainment: ", ""))
            print("New Quiz pack created successfully!")
    else:
        print(f"Failed to fetch API. Status code: {response.status_code}")


def quiz(user):
    print("\n".join(os.listdir(Path(user.path, "local"))))
    file: str = input("select: ") or os.listdir(Path(user.path, "local"))[0]

    with open(Path(user.path, "local", file), "r") as f:
        quizzes = json.loads(f.read())["results"]

    shuffled = random.sample(quizzes, len(quizzes))
    points = 0
    while bool(shuffled):
        question = shuffled[0]['question']
        options = shuffled[0]["incorrect_answers"] + [shuffled[0]["correct_answer"]]
        random.shuffle(options)

        prompt: str = input(f"\n{question}\nOptions: {', '.join(options)}.\nGuess: ") or "pass"

        if prompt.lower() == shuffled[0]["correct_answer"].lower():
            print("Nice work!")
            points += 1
        else:
            print(f"Ruh roh raggy! The answer was {shuffled[0]['correct_answer']}")
        shuffled.pop(0)

    print(f"You got {points}/{len(quizzes)} correct!")


# def main() -> None:
    # menu = 0
    # while not (menu == 1 or menu == 2):
    #     try:
    #         menu: int = int(input("1. Login\n2. Sign Up\n\nSelect action: "))
    #     except ValueError:
    #         print("Please enter an integer value!")

    # user = None
    # while user is None:
    #     name: str = input("Name: ")
    #     password: str = input("Password: ")

    #     user = login(name, password) if menu == 1 else signUp(name, password)