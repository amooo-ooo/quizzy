from pathlib import Path
from functools import partial
from datetime import datetime
import random
import json
import sys
import os
import requests
from src.main import login, signUp, createQuiz
import html
from threading import Thread
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFontDatabase, QCursor
from PyQt5.QtWidgets import (
    QScrollArea,
    QSpinBox,
    QLineEdit,
    QApplication,
    QMessageBox,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedLayout,
    QWidget,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QComboBox
)


class Window(QMainWindow):
    """Main Window"""
    with open(Path(Path(__file__).parent, "opentdb.json"), "r") as f:
        OPENTDB_API = json.loads(f.read())

    def __init__(self, api: str = "http://127.0.0.1:5000") -> None:
        super().__init__()
        self.screen_size = QApplication.primaryScreen().size()
        self.path = "Home"
        self.api = api

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the User Interface"""
        self.window_name = "Quizzy"
        self.setWindowTitle(f"Quizzy - {self.path}")

        icons_dir_path = Path(Path(__file__).parent, "icons")
        self.setWindowIcon(QIcon(str(Path(icons_dir_path, "home.png"))))

        fonts = ["Aspekta-400.otf", "Aspekta-500.otf"]
        for font in fonts:
            fontpath = str(Path(Path(__file__).parent, "fonts", font))
            QFontDatabase.addApplicationFont(fontpath)

        self.stacked_layout = (
            QStackedLayout()
        )  # Create a stacked layout to manage pages
        #self.stacked_layout.addWidget(self._create_main_page())
        self.stacked_layout.addWidget(self._create_login_page())

        central_widget = QWidget()
        central_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(central_widget)

        stylepath = Path(Path(__file__).parent, "styles", "body.css")
        with open(stylepath, "r") as f:
            self.css = f.read()
            central_widget.setStyleSheet(self.css)


    def _init_generate_quizzes_page(self) -> QWidget:
        main = QWidget()
        self.setWindowTitle("Quizzy - Generate Quiz")
        main.setObjectName("generate-quizzes-page")
    
        frame = QHBoxLayout()
        main_layout = QVBoxLayout()

        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(0)

        heading = QLabel("Generate Quiz")
        heading.setObjectName("heading")
        #ui_layout.addWidget(heading)

        input_text = QLabel("Name*")
        input_text.setObjectName("input-text")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("General Knowledge Quiz")
        self.name_input.setObjectName("input-field")

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.name_input)

        input_text = QLabel("Topic*")
        input_text.setObjectName("input-text")

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("input-field")
        self.dropdown.addItems(list(Window.OPENTDB_API["categories"]))

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.dropdown)

        input_text = QLabel("Difficulty*")
        input_text.setObjectName("input-text")

        self.difficulty = QComboBox()
        self.difficulty.setObjectName("input-field")
        self.difficulty.addItems(list(Window.OPENTDB_API["difficulty"]))

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.difficulty)

        input_text = QLabel("Number of Questions*")
        input_text.setObjectName("input-text")

        self.spinbox = QSpinBox()
        self.spinbox.setObjectName("input-field")
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(50)
        self.spinbox.setValue(10)

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.spinbox)

        ui_layout.addStretch(2)
        ui_layout.addWidget(self._quiz_type_widget())


        ui_layout.addStretch(2)
        signup = QPushButton("Generate Quiz")
        signup.setCursor(QCursor(Qt.PointingHandCursor))
        signup.setObjectName("input-field")
        signup.clicked.connect(self._generate_quiz)
        ui_layout.addWidget(signup)
        main.setLayout(ui_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(heading, alignment=Qt.AlignCenter)
        main_layout.addWidget(main)
        main_layout.addStretch(1)

        frame.addStretch(1)
        frame.addLayout(main_layout)
        frame.addStretch(1)

        container = QWidget()
        container.setLayout(frame)
        return container
    
    def _init_infinite_quizzes_page(self) -> QWidget:
        main = QWidget()
        self.setWindowTitle("Quizzy - Infinite Quiz")
        main.setObjectName("generate-quizzes-page")
    
        frame = QHBoxLayout()
        main_layout = QVBoxLayout()

        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(0)

        heading = QLabel("Infinite Quiz")
        heading.setObjectName("heading")
        #ui_layout.addWidget(heading)

        input_text = QLabel("Topic*")
        input_text.setObjectName("input-text")

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("input-field")
        self.dropdown.addItems(list(Window.OPENTDB_API["categories"]))

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.dropdown)

        input_text = QLabel("Difficulty*")
        input_text.setObjectName("input-text")

        self.difficulty = QComboBox()
        self.difficulty.setObjectName("input-field")
        self.difficulty.addItems(list(Window.OPENTDB_API["difficulty"]))

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.difficulty)

        input_text = QLabel("Lives*")
        input_text.setObjectName("input-text")

        self.spinbox = QSpinBox()
        self.spinbox.setObjectName("input-field")
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(50)
        self.spinbox.setValue(5)

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.spinbox)


        ui_layout.addStretch(2)
        ui_layout.addWidget(self._quiz_type_widget())


        ui_layout.addStretch(2)
        signup = QPushButton("Start Session")
        signup.setCursor(QCursor(Qt.PointingHandCursor))
        signup.setObjectName("input-field")
        signup.clicked.connect(self._start_infinite_quiz)
        ui_layout.addWidget(signup)
        main.setLayout(ui_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(heading, alignment=Qt.AlignCenter)
        main_layout.addWidget(main)
        main_layout.addStretch(1)

        frame.addStretch(1)
        frame.addLayout(main_layout)
        frame.addStretch(1)

        container = QWidget()
        container.setLayout(frame)
        return container
    
    def _start_infinite_quiz(self, expand: bool = False):
        self.setWindowTitle("Quizzy - Infinite Quiz")

        try:

            params = {
                "amount": 10,
                "category": Window.OPENTDB_API["categories"][self.dropdown.currentText()],
                "difficulty": Window.OPENTDB_API["difficulty"][self.difficulty.currentText()],
                "type": Window.OPENTDB_API["type"][[i for i in self.quiz_type if self.quiz_type[i] == "active"][0]]
            }

            url = "https://opentdb.com/api.php"
            response = requests.get(url, params=params)
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}

            if not expand:
                url = f"{self.api}/start_infinite_quiz"
                self.live_session = {"questions": response.json()["results"]} | {"lives": self.spinbox.value()}
                session = self.live_session
            else:
                url = f"{self.api}/expand_infinite_quiz"
                session = {"questions": response.json()["results"]}

            response = requests.post(url, data=json.dumps(session), headers=headers)

            if "status" in response.json():
                if not expand:
                    self.main_layout.addWidget(self._infinite_quiz_page())
                    self.main_layout.setCurrentIndex(2)
                else:
                    self.live_session["questions"].append(session["questions"])
            else:
                raise requests.exceptions.ConnectionError(response.json()["error"])

        except requests.exceptions.ConnectionError as e: 
            QMessageBox.warning(
                self, "Generate Quiz", 
                f"An error occured while starting session: {e}")
            self._back_to_main()

    def _infinite_quiz_page(self) -> QWidget:
        page = QWidget()
        main_layout = QGridLayout()
        self.quiz_main = QStackedLayout()

        self.score = 0
    
        self.quiz_main.addWidget(self._infinite_question_ui())
        main_layout.addLayout(self.quiz_main, 2, 2)
        page.setLayout(main_layout)
        return page
    
    def _infinite_question_ui(self) -> QWidget:
        question_ui = QWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._question_ui_nav(infinite=True))

        question = self.live_session["questions"][0]

        main_layout.addWidget(QQuestions(question["question"], css="quiz.css"))

        options_layout = QGridLayout()
        options_layout.setHorizontalSpacing(0)
        options_layout.setVerticalSpacing(0)

        options = question["incorrect_answers"] + [question["correct_answer"]]
        random.shuffle(options)

        positions = (
            [(0, 0), (1, 0), (1, 1), (0, 1)]
            if question["type"] == "multiple"
            else [(0, 0), (1, 0)]
        )

        for index, pos in enumerate(positions):
            option = options[index]
            button = QQuestions(option, css="questions.css")
            #button.setStyleSheet(f"border: 1px solid {colours[index]};")
            button.clicked.connect(
                partial(
                    self._infinite_question_option_clicked, option, question["correct_answer"]
                )
            )
            options_layout.addWidget(button, pos[0], pos[1])

        questions_box = QHBoxLayout()

        questions_box.addLayout(options_layout)

        main_layout.addLayout(questions_box)
        question_ui.setLayout(main_layout)

        return question_ui
        
    def _infinite_question_option_clicked(self, selected: str, correct_answer: str):
        if self.api_key:
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}
            data = {'selected': selected }
            response = requests.post(f'{self.api}/answer_infinite_quiz', data=json.dumps(data), headers=headers)

            if "status" in response.json():
                status = response.json()["status"]
                self.live_session["lives"] = response.json()["lives"]
            else:
                raise requests.exceptions.ConnectionError(response.json()["error"])
            
            if "correct" in status.lower():
                self.user_score += 1
                self.points_display.setText(f"{self.user_score} points")
                
        del self.live_session["questions"][0]
        if 5 >= len(self.live_session["questions"]):
            thread = Thread(target=self._start_infinite_quiz, args=(True,))
            thread.start()

        if selected == correct_answer:
            QMessageBox.information(
                self, "Right Answer", "Congratulations! Your answer is correct."
            )
            self.score += 1
        else:
            QMessageBox.warning(self, "Wrong Answer", "Oops! Your answer is incorrect.")

        first_widget = self.quiz_main.widget(0)
        self.quiz_main.removeWidget(first_widget)
        first_widget.deleteLater()

        if self.live_session["lives"] <= 0:
            self.quiz_main.addWidget(self._quiz_summary(infinite=True))
        else:
            self.quiz_main.addWidget(
                self._infinite_question_ui()
            )

    def switch_quiz_type(self, index: int) -> None:
        self.quiz_type = {item: "active" if index == i else "inactive" 
                          for i, item in enumerate(list(Window.OPENTDB_API["type"]))}
       
        for i, item in enumerate(self.quiz_type):
            widget = self.quiz_type_layout.itemAt(i).widget()
            if widget is not None:
                widget.setStyleSheet(self.modes[self.quiz_type[item]])
    
    def _quiz_type_widget(self) -> QWidget:
        self.quiz_type = {item: "active" if index == 0 else "inactive" 
                          for index, item in enumerate(list(Window.OPENTDB_API["type"]))}

        self.modes = {
            "active": "background-color: #000000; color: #FFFFFF;",
            "inactive": "background-color: transparent; color: #000000;"
        }

        container = QWidget()
        container.setContentsMargins(18, 0, 18, 0)
        container.setObjectName("select-type")

        self.quiz_type_layout = QHBoxLayout()
        self.quiz_type_layout.setSpacing(0)
        self.quiz_type_layout.setContentsMargins(0, 0, 0, 0)

        for i, item in enumerate(self.quiz_type):
            button = QPushButton(item)
            button.setObjectName("select-type-button")
            button.setStyleSheet(self.modes[self.quiz_type[item]])
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.clicked.connect(partial(self.switch_quiz_type, i))
            self.quiz_type_layout.addWidget(button)

        container.setLayout(self.quiz_type_layout)
        container.setStyleSheet(self.css)
        return container
    
    def _generate_quiz(self) -> None:
        try:
            createQuiz(self.user.path, 
                       self.spinbox.value(), 
                       self.dropdown.currentText(),
                       self.difficulty.currentText(),
                       [i for i in self.quiz_type if self.quiz_type[i] == "active"][0],
                       self.name_input.text())
            
            QMessageBox.information(
                self, "Generate Quiz", 
                f"{self.name_input.text()} successfully created!"
            )
        except requests.exceptions.ConnectionError as e: 
            QMessageBox.warning(
                self, "Generate Quiz", 
                f"An error occured while generating {self.name_input.text()}: {e}")

        self._back_to_main()

    def _create_login_page(self) -> QWidget:
        main = QWidget()
        self.setWindowTitle("Quizzy - Log In")
        main.setObjectName("login-page")

        frame = QHBoxLayout()
        main_layout = QVBoxLayout()

        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(0)

        heading = QLabel("Log in")
        heading.setObjectName("heading")
        #ui_layout.addWidget(heading)

        input_text = QLabel("Name*")
        input_text.setObjectName("input-text")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        self.name_input.setObjectName("input-field")

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.name_input)

        input_text = QLabel("Password*")
        input_text.setObjectName("input-text")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setObjectName("input-field")

        ui_layout.addStretch(1)
        ui_layout.addWidget(input_text)
        ui_layout.addWidget(self.password_input)

        ui_layout.addStretch(2)
        login = QPushButton("Continue with name")
        login.setCursor(QCursor(Qt.PointingHandCursor))
        login.setObjectName("input-field")
        login.clicked.connect(self._login)
        ui_layout.addWidget(login)

        signup = QPushButton("Don't have an account? Sign up")
        signup.clicked.connect(partial(self._switch_to, self._create_signup_page))
        signup.setCursor(QCursor(Qt.PointingHandCursor))
        signup.setObjectName("link")
        ui_layout.addWidget(signup)
        ui_layout.addStretch(1)
            
        main.setLayout(ui_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(heading, alignment=Qt.AlignCenter)
        main_layout.addWidget(main)
        main_layout.addStretch(1)

        frame.addStretch(1)
        frame.addLayout(main_layout)
        frame.addStretch(1)

        container = QWidget()
        container.setLayout(frame)
        return container
    
    def _switch_to(self, function) -> None:
        self.stacked_layout.addWidget(function())
        first_widget = self.stacked_layout.itemAt(0).widget()
        self.stacked_layout.removeWidget(first_widget)
        first_widget.deleteLater()
    
    def _login(self) -> None:
        password = self.password_input.text()
        name = self.name_input.text()
        if not password or not name:
            print("Missing fields")
            return None
        
        user = login(name, password)
        self.api_key = user["api_key"]
        self.user = user["profile"]
        if self.api_key:
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}
            response = requests.get(f'{self.api}/get_score', headers=headers)
            self.user_score = response.json()["score"]

        self.stacked_layout.addWidget(self._create_main_page())
        first_widget = self.stacked_layout.itemAt(0).widget()
        self.stacked_layout.removeWidget(first_widget)
        first_widget.deleteLater()

    def _create_signup_page(self) -> QWidget:
            main = QWidget()
            self.setWindowTitle("Quizzy - Sign Up")
            main.setObjectName("signin-page")

            frame = QHBoxLayout()
            main_layout = QVBoxLayout()

            ui_layout = QVBoxLayout()
            ui_layout.setSpacing(0)

            heading = QLabel("Sign up")
            heading.setObjectName("heading")
            #ui_layout.addWidget(heading)

            input_text = QLabel("Name*")
            input_text.setObjectName("input-text")

            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("John Doe")
            self.name_input.setObjectName("input-field")

            ui_layout.addStretch(1)
            ui_layout.addWidget(input_text)
            ui_layout.addWidget(self.name_input)

            input_text = QLabel("Create a password*")
            input_text.setObjectName("input-text")

            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("Password")
            self.password_input.setObjectName("input-field")

            ui_layout.addStretch(1)
            ui_layout.addWidget(input_text)
            ui_layout.addWidget(self.password_input)

            input_text = QLabel("Select your house*")
            input_text.setObjectName("input-text")

            self.dropdown = QComboBox()
            self.dropdown.setObjectName("input-field")
            self.dropdown.addItems(['Ngata', 'Rutherford', 'Britten', 'Blake', "Cooper", "Sheppard"])

            ui_layout.addStretch(1)
            ui_layout.addWidget(input_text)
            ui_layout.addWidget(self.dropdown)

            ui_layout.addStretch(2)
            signup = QPushButton("Continue with name")
            signup.setCursor(QCursor(Qt.PointingHandCursor))
            signup.setObjectName("input-field")
            signup.clicked.connect(self._sign_up)
            ui_layout.addWidget(signup)

            login = QPushButton("Already have an account? Log in")
            login.setCursor(QCursor(Qt.PointingHandCursor))
            login.setObjectName("link")
            login.clicked.connect(partial(self._switch_to, self._create_login_page))
            ui_layout.addWidget(login)
            ui_layout.addStretch(1)
                
            main.setLayout(ui_layout)

            main_layout.addStretch(1)
            main_layout.addWidget(heading, alignment=Qt.AlignCenter)
            main_layout.addWidget(main)
            main_layout.addStretch(1)

            frame.addStretch(1)
            frame.addLayout(main_layout)
            frame.addStretch(1)

            container = QWidget()
            container.setLayout(frame)
            return container

    def _sign_up(self) -> None:
        password = self.password_input.text()
        name = self.name_input.text()
        team = self.dropdown.currentText()
        if not password or not name:
            print("Missing fields")
            return None
        
        user = signUp(name, password, team)
        self.api_key = user["api_key"]
        self.user = user["profile"]
        if self.api_key:
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}
            response = requests.get(f'{self.api}/get_score', headers=headers)
            self.user_score = response.json()["score"]

        self.stacked_layout.addWidget(self._create_main_page())
        first_widget = self.stacked_layout.itemAt(0).widget()
        self.stacked_layout.removeWidget(first_widget)
        first_widget.deleteLater()

    def _create_main_page(self) -> QWidget:
        """Create the main page of the application"""
        self.main_page = QWidget()
        self.setWindowTitle("Quizzy - Home")

        self.main_page.setObjectName("body")
        main_layout = QVBoxLayout()

        tempnav = self._create_navbar()
        main_layout.addWidget(tempnav)

        # main_layout.addWidget(self._greet_user())
        self.main_layout = QStackedLayout()
        self.main_layout.addWidget(self._init_homepage())
        main_layout.addLayout(self.main_layout)
        self.main_page.setLayout(main_layout)

        return self.main_page
    
    def _menu_clicked(self, function) -> None:
        element = function()
        self.main_layout.addWidget(element)
        self.main_layout.setCurrentIndex(1)

    def _init_homepage(self) -> QWidget:
        main = QWidget()

        main_layout = QHBoxLayout()
        section_layout = QVBoxLayout()

        section_layout.addStretch(1)
        heading = QLabel(f"Welcome back, {self.user.name}!")
        heading.setObjectName("heading")

        section_layout.addWidget(heading, alignment=Qt.AlignCenter)

        menu_layout = QGridLayout()
        nav = {"Quiz Me!": {"onclick": self._init_quizzespage,
                            "description": "Challenge yourself to a quiz from your local files."}, 
               "Generate Quizzes!": {"onclick": self._init_generate_quizzes_page,
                                     "description":"Quickly and easily generate quizzes to play."}, 
               "Leaderboards": {"onclick": self._init_leaderboards,
                                "description": "Check out which house has the most points."}, 
               "Infinity Mode": {"onclick": self._init_infinite_quizzes_page,
                                 "description":"Play quizzes infinitely without limit."}}
        
        stylepath = Path(Path(__file__).parent, "styles", "card.css")
        with open(stylepath, "r") as f:
            style = f.read()
    
        for index, content in enumerate(nav):
            button = QCard(content, description=nav[content]["description"], css=style)
            button.setObjectName("QCard")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.clicked.connect(partial(self._menu_clicked, nav[content]["onclick"]))

            x, y = divmod(index, 2)
            menu_layout.addWidget(button, x, y)
    
        menu_layout.setSpacing(0)

        section_layout.addLayout(menu_layout)
        section_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(section_layout)
        main_layout.addStretch(1)

        main.setLayout(main_layout)
        return main
    
    def _init_quizzespage(self) -> QWidget:
        main = QWidget()
        self.setWindowTitle("Quizzy - Local Quizzes")
        
        main_layout = QHBoxLayout()
        section_layout = QVBoxLayout()

        heading = QLabel("Quizzes")
        heading.setObjectName("heading")

        label = QLabel("Local")
        label.setObjectName("heading")

        section_layout.addStretch(1)
        section_layout.addWidget(heading, alignment=Qt.AlignCenter)
        section_layout.addWidget(label, alignment=Qt.AlignLeft)
        section_layout.addWidget(self._local_quiz_pack())
        section_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(section_layout)
        main_layout.addStretch(1)

        main.setLayout(main_layout)
        return main
    
    def _leaderboards_ui(self) -> QWidget:
        main = QWidget()
        self.setWindowTitle("Quizzy - Leaderboard")
        main.setObjectName("leaderboard")
        layout = QVBoxLayout()

        if not self.api_key:
            layout.addWidget(QLabel("Offline"))
            main.setLayout(layout)
            return main
        
        headers = {"X-API-Key": self.api_key}
        response = requests.get(f'{self.api}/render_leaderboard', headers=headers)
        data = response.json()["data"]

        # sort the data
        data = dict(sorted(data.items(), key=lambda item: item[1]['points'], reverse=True))

        stylepath = Path(Path(__file__).parent, "styles", "leaderboard.css")
        with open(stylepath, "r") as f:
            style = f.read()

        for i in data: 
            layout.addWidget(QLeaderboardItem(i.capitalize(), data[i]["points"], data[i]["colour"]))
        main.setLayout(layout)
        main.setObjectName("leaderboard-container")
        main.setStyleSheet(style)
        return main

    def _init_leaderboards(self) -> QWidget:
        main = QWidget()
        
        main_layout = QHBoxLayout()
        section_layout = QVBoxLayout()

        heading = QLabel("Leaderboard")
        heading.setObjectName("heading")

        section_layout.addStretch(1)
        section_layout.addWidget(heading, alignment=Qt.AlignCenter)

        section_layout.addWidget(self._leaderboards_ui())
        section_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(section_layout)
        main_layout.addStretch(1)

        main.setLayout(main_layout)
        return main
    
    def _create_navbar(self) -> QWidget:
        navbar = QWidget()
        navbar.setObjectName("navbar")

        layout = QHBoxLayout()


        # Load the image with QPixmap
        logo_button = QPushButton()
        logo_button.setCursor(QCursor(Qt.PointingHandCursor))
        logo_button.setIcon(QIcon(str(Path(Path(__file__).parent, "home.png"))))
        logo_button.setIconSize(QSize(36, 36))
        logo_button.setObjectName("logo")
        logo_button.clicked.connect(self._back_to_main)
        layout.addWidget(logo_button)

        layout.addStretch(4)

        if self.api_key:
            self.points_display = QLabel(f"{self.user_score} points")
            self.points_display.setObjectName("navbar-points")
            layout.addWidget(self.points_display)

        logout = QPushButton("LOG OUT")
        logout.setCursor(QCursor(Qt.PointingHandCursor))
        logout.clicked.connect(self.close)
        layout.addWidget(logout)

        # Load the image with QPixmap
        logo_button = QPushButton()
        logo_button.setCursor(QCursor(Qt.PointingHandCursor))
        logo_button.setIcon(QIcon(str(Path(Path(__file__).parent, "settings.png"))))
        logo_button.setIconSize(QSize(36, 36))
        logo_button.setObjectName("logo")
        logo_button.clicked.connect(self._back_to_main)
        layout.addWidget(logo_button)

        stylepath = Path(Path(__file__).parent, "styles", "navbar.css")
        with open(stylepath, "r") as f:
            self.setStyleSheet(f.read())

        navbar.setLayout(layout)
        return navbar

    def _local_quiz_pack(self) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setObjectName("quiz-display")
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        stylepath = Path(Path(__file__).parent, "styles", "body.css")
        with open(stylepath, "r") as f:
            self.setStyleSheet(f.read())
    
        section = QHBoxLayout()
        section.setSpacing(0)

        quizzes = [
            file.rstrip(".json") for file in os.listdir(Path(self.user.path, "local"))
        ]
        for i in quizzes:
            card = QCover(title=i, user=self.user)
            card.setCursor(QCursor(Qt.PointingHandCursor))
            card.clicked.connect(partial(self._card_clicked, i))
            section.addWidget(card)

        # Create a QWidget, set its layout to section
        section_widget = QWidget()
        section_widget.setObjectName("cards-scroll")
        section_widget.setLayout(section)
        section_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the scroll area's widget to the QWidget
        scroll_area.setWidget(section_widget)

        return scroll_area
    
    def _quiz_recents(self):
        main_layout = QVBoxLayout()

        with open(Path(self.user.path, "recents.json"), "r") as f:
            history = list(reversed(json.loads(f.read())["history"]))
        
        for i in history:
            main_layout.addWidget(self._quiz_recent(i))

        return main_layout
    
    def _quiz_recent(self, history: dict) -> QWidget:
        item = QWidget()
        item_layout = QHBoxLayout()

        item_contents = QLabel(history["title"].upper())
        item_layout.addWidget(item_contents)  

        item_contents = QLabel(f"{history['score'][0]}/{history['score'][1]}")
        item_layout.addWidget(item_contents) 

        item_contents = QLabel(history["timestamp"])
        item_layout.addWidget(item_contents)   

        item.setLayout(item_layout)
        item.setObjectName("recents-item")
        return item

    def _quiz_page(self, title: str) -> QWidget:
        page = QWidget()
        main_layout = QGridLayout()
        self.quiz_main = QStackedLayout()

        with open(Path(self.user.path, "local", title + ".json"), "r") as f:
            quiz_data = json.loads(f.read())
        random.shuffle(quiz_data["results"])
    
        if self.api_key:
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}
            data = { 'quiz_name': title, 'quiz': quiz_data }
            response = requests.post(f'{self.api}/start_quiz', data=json.dumps(data), headers=headers)
            status = response.json()["status"]

        questions = quiz_data["results"]

        self.score = 0
        self.question_index = 0
        self.active_quiz = questions
        self.active_title = title

        self.quiz_main.addWidget(self._question_ui(questions[0]))

        main_layout.addLayout(self.quiz_main, 2, 2)
        page.setLayout(main_layout)
        return page

    def _quiz_summary(self, infinite: bool = False) -> QWidget:
        summary_ui = QWidget()

        main_layout = QVBoxLayout()

        if not infinite:
            score = QLabel(f"You scored {self.score}/{len(self.active_quiz)}.")
        else:
            score = QLabel(f"You scored {self.score}.")
        main_layout.addWidget(score)

        back = QPushButton(f"Back")
        back.setCursor(QCursor(Qt.PointingHandCursor))
        back.clicked.connect(self._back_to_main)
        main_layout.addWidget(back)

        summary_ui.setLayout(main_layout)
        return summary_ui

    def _back_to_main(self):
        self.setWindowTitle("Quizzy - Home")
        for _ in range(self.main_layout.count() - 1, 0, -1):
            widget = self.main_layout.widget(_)
            self.main_layout.removeWidget(widget)
        
        self.setWindowTitle(f"Quizzy - {self.path}")

        # with open(Path(self.user.path, "recents.json"), "r+") as f:
        #     # Read the contents of the file
        #     content = json.loads(f.read())

        #     new_recent = {"title": self.active_title,
        #                   "timestamp": datetime.now().strftime("%I:%M %p %d/%m/%Y"),
        #                   "score": (self.score, len(self.active_quiz))}
            
        #     content["history"].append(new_recent)
        #     #self.recents.insertWidget(0, self._quiz_recent(new_recent))

        #     if len(content["history"]) >= content["max"]:
        #         del content["history"][0]

        #         #item = self.recents.takeAt(4) 
        #         #widget = item.widget()
        #         #if widget is not None:
        #             #widget.deleteLater()
            
        #     # Write the updated content back to the file
        #     f.seek(0)
        #     f.write(json.dumps(content))
        #     f.truncate()

        #     # update main page

    def _question_ui_nav(self, infinite: bool = False) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()

        back = QPushButton("BACK")
        back.setCursor(QCursor(Qt.PointingHandCursor))
        back.clicked.connect(self._question_ui_back)

        layout.addWidget(back)
        layout.addStretch()
        if not infinite:
            layout.addWidget(QLabel(f"{self.score}/{len(self.active_quiz)}"))
        else:
            layout.addWidget(QLabel(f"Score: {self.score} Lives: {self.live_session['lives']}"))

        widget.setLayout(layout)
        return widget
    
    def _question_ui_back(self) -> None:
        first_widget = self.main_layout.widget(2)
        self.main_layout.removeWidget(first_widget)
        first_widget.deleteLater()

        self._back_to_main()

    def _question_ui(self, question: dict) -> QWidget:
        question_ui = QWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._question_ui_nav())

        main_layout.addWidget(QQuestions(question["question"], css="quiz.css"))

        options_layout = QGridLayout()
        options_layout.setHorizontalSpacing(0)
        options_layout.setVerticalSpacing(0)

        options = question["incorrect_answers"] + [question["correct_answer"]]
        random.shuffle(options)

        positions = (
            [(0, 0), (1, 0), (1, 1), (0, 1)]
            if question["type"] == "multiple"
            else [(0, 0), (1, 0)]
        )

        for index, pos in enumerate(positions):
            option = options[index]
            button = QQuestions(option, css="questions.css")
            #button.setStyleSheet(f"border: 1px solid {colours[index]};")
            button.clicked.connect(
                partial(
                    self._question_option_clicked, option, question["correct_answer"]
                )
            )
            options_layout.addWidget(button, pos[0], pos[1])

        questions_box = QHBoxLayout()

        questions_box.addLayout(options_layout)

        main_layout.addLayout(questions_box)
        question_ui.setLayout(main_layout)

        return question_ui

    def _question_option_clicked(self, selected: str, correct_answer: str):
        if self.api_key:
            headers = {"X-API-Key": self.api_key, 'Content-Type': 'application/json'}
            data = { 'quiz_name': self.active_title, 'selected': selected }
            response = requests.post(f'{self.api}/answer_quiz', data=json.dumps(data), headers=headers)
            status = response.json()["status"]
            if "correct" in status.lower():
                self.user_score += 1
                self.points_display.setText(f"{self.user_score} points")
                
        
        if selected == correct_answer:
            QMessageBox.information(
                self, "Right Answer", "Congratulations! Your answer is correct."
            )
            self.score += 1
        else:
            QMessageBox.warning(self, "Wrong Answer", "Oops! Your answer is incorrect.")

        first_widget = self.quiz_main.widget(0)
        self.quiz_main.removeWidget(first_widget)
        first_widget.deleteLater()

        self.question_index += 1
        if self.question_index >= len(self.active_quiz):
            self.quiz_main.addWidget(self._quiz_summary())
        else:
            self.quiz_main.addWidget(
                self._question_ui(self.active_quiz[self.question_index])
            )

    def _card_clicked(self, title: str):
        self.setWindowTitle(f"Quizzy - {title.upper()}")
        self.main_layout.addWidget(self._quiz_page(title))
        self.main_layout.setCurrentIndex(2)


class QCover(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, user: dict, parent=None, css: str = "card.css"):
        super().__init__(parent)

        card_layout = QVBoxLayout()
        self.title = title
        self.user = user

        card_layout.addWidget(self._format())
        self.setObjectName("card")

        stylepath = Path(Path(__file__).parent, "styles", css)
        with open(stylepath, "r") as f:
            self.setStyleSheet(f.read())

        # self.setFixedSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.setGraphicsEffect(self._shadow())
        self.setLayout(card_layout)

    def _decor(self):
        return QLabel()
    
    def _title(self):
        label = QLabel(html.unescape(self.title.upper()))
        label.setObjectName("card-title")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignBottom)
        return label
    
    def _desc(self):
        with open(Path(self.user.path, "local", self.title + ".json"), "r") as f:
            category = json.loads(f.read())["category"].upper()
        label = QLabel(html.unescape(category))
        label.setObjectName("card-desc")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        return label
    
    def _stats(self):
        return QLabel()

    def _format(self) -> QWidget:
        frame = QWidget()
        frame.setObjectName("card-frame")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        format = [self._decor, self._title, self._desc, self._stats]
        layout = QGridLayout()

        for index, function in enumerate(format):
            x, y = divmod(index, 2)
            layout.addWidget(function(), y, x)

        layout.setSpacing(0)

        frame.setLayout(layout)
        return frame

    def _shadow(self):
        # Apply a QGraphicsDropShadowEffect for a box-shadow-like effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 38))  # RGBA: (0, 0, 0, 0.15 * 255)

        return shadow

    def mousePressEvent(self, event):
        """Override mouse press event to emit clicked signal"""
        self.clicked.emit()
        super().mousePressEvent(event)

class QQuestions(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, parent=None, css: str = "questions.css", user: dict = None):
        super().__init__(parent)

        card_layout = QVBoxLayout()
        self.title = title
        self.setObjectName("card")

        label = QLabel(html.unescape(title))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label)

        stylepath = Path(Path(__file__).parent, "styles", css)
        with open(stylepath, "r") as f:
            self.setStyleSheet(f.read())

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(card_layout)

    def mousePressEvent(self, event):
        """Override mouse press event to emit clicked signal"""
        self.clicked.emit()
        super().mousePressEvent(event)

class QLeaderboardItem(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, points: int | None = None, colour: str | None = None, parent=None, css: str = ""):
        super().__init__(parent)

        main_widget = QWidget()
        
        card_layout = QHBoxLayout()
        card_layout.setSpacing(0)
        self.title = title  

        colour_widget = QWidget()
        colour_widget.setObjectName("colour-widget")
        colour_widget.setStyleSheet(f"background-color: {colour}")
        card_layout.addWidget(colour_widget)

        title_label = QLabel(title)
        title_label.setObjectName("title")
        card_layout.addWidget(title_label)

        card_layout.addStretch(1)

        points_label = QLabel(str(points))
        points_label.setObjectName("points")
        card_layout.addWidget(points_label)

        main_widget.setLayout(card_layout)
        main_widget.setObjectName("leaderboard-icon")

        self.setStyleSheet(css)
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        actual = QVBoxLayout()
        actual.addWidget(main_widget)
        self.setLayout(actual)

    def mousePressEvent(self, event):
        """Override mouse press event to emit clicked signal"""
        self.clicked.emit()
        super().mousePressEvent(event)

class QCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, description: str | None = None, icon: Path | None = None, parent=None, css: str = ""):
        super().__init__(parent)

        main_widget = QWidget()
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(0)
        self.title = title  

        card_layout.addStretch(1)

        title_label = QLabel(html.unescape(title))
        title_label.setObjectName("title")
        card_layout.addWidget(title_label, alignment=Qt.AlignBottom)

        if description: 
            desc_label = QLabel(html.unescape(description))
            desc_label.setWordWrap(True)
            desc_label.setObjectName("description")
            card_layout.addWidget(desc_label, alignment=Qt.AlignTop)

        if icon:
            icon_layout = QHBoxLayout()
            icon_layout.addLayout(card_layout)

            # Create a QLabel with a QPixmap
            icon = QLabel()
            pixmap = QPixmap('image.png')  # Replace 'image.png' with the path to your image
            icon.setPixmap(pixmap)

            # Add the QLabel to the layout
            icon_layout.addWidget(icon)
            main_widget.setLayout(icon)
        else:
            main_widget.setLayout(card_layout)

        card_layout.addStretch(1)
        main_widget.setObjectName("QCard")

        self.setStyleSheet(css)
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        actual = QVBoxLayout()
        actual.addWidget(main_widget)
        self.setLayout(actual)

    def mousePressEvent(self, event):
        """Override mouse press event to emit clicked signal"""
        self.clicked.emit()
        super().mousePressEvent(event)


def main() -> None:
    """Main function"""
    app = QApplication(sys.argv)
    window = Window()
    window.showMaximized()
    sys.exit(app.exec())