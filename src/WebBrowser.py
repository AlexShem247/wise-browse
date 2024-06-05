import os
import tempfile
import textwrap
from pathlib import Path
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpacerItem, QSizePolicy, \
    QMessageBox, QFrame

from src.URLUtils import getDomainName
from src.FAQDatabase import FAQDatabase
from src.EventFilters import QueryInputKeyEaster, ButtonHoverHandler, SearchInputKeyEater
from src.Assistant import Assistant, Model


class WebBrowser(QMainWindow):
    UI_FILE = Path("assets/UI/MainPage.ui")
    WINDOW_TITLE = "Wise Browse"
    HOME_PAGE = QUrl("https://www.google.com")

    MICROPHONE_IMG = Path("assets/img/microphone.png")
    INTERNET_IMG = Path("assets/img/internet.png")
    HOME_IMG = Path("assets/img/home.png")
    ACTION_LOG_IMG = Path("assets/img/clipboard.png")
    SETTINGS_IMG = Path("assets/img/settings.png")
    STAR_EMPTY_IMG = Path("assets/img/star_empty.png")
    STAR_FILLED_IMG = Path("assets/img/star_filled.png")
    SEARCH_IMG = Path("assets/img/search.png")
    HOME_HEART_IMG = Path("assets/img/heart.png")
    HOME_HISTORY_IMG = Path("assets/img/history.png")
    HOME_SETTINGS_IMG = Path("assets/img/setting.png")

    INTERNET_SIZE = (30, 30)
    MICROPHONE_SIZE = (20, 20)
    STAR_SIZE = (15, 15)
    HOME_BUTTONS_SIZE = (60,60)

    TEXT_WIDTH = 30
    FONT_SIZE = 11
    NO_STARS = 5
    MAX_QUESTIONS = 8

    window = None
    buttonStyle = None

    FAQLayout: QVBoxLayout
    FAQBtnLayout: QVBoxLayout
    enterBtn: QPushButton
    backBtn: QPushButton
    queryInput: QTextEdit
    FAQLabel: QLabel
    helpfulLabel: QLabel
    starBtns = []
        
    homeFrame: QFrame
    webSearchInput: QTextEdit
    homeFavouritesBtn = QPushButton
    homeActionLogBtn = QPushButton
    homeSettingsBtn = QPushButton

    AI_MODEL_TYPE = Model.full
    _, screenshotPath = tempfile.mkstemp()
    aiAssistant = Assistant(AI_MODEL_TYPE, screenshotPath)

    database = FAQDatabase(aiAssistant)
    domain = None
    currentQs = []

    INPUT_INFO = ("Inputting Information", "Someone write something here.")
    GENERAL_INFO = (WINDOW_TITLE, "Someone write something here.")

    def __init__(self):
        super().__init__()
        uic.loadUi(self.UI_FILE, self)

        # Configure Window
        self.setWindowTitle(self.WINDOW_TITLE)
        self.buttonStyle = self.findChild(QPushButton, "sampleQuestionBtn").styleSheet()
        self.FAQLayout = self.findChild(QVBoxLayout, "FAQLayout")
        self.FAQBtnLayout = self.findChild(QVBoxLayout, "FAQBtnLayout")
        self.clearLayout(self.FAQBtnLayout)

        # Add WebView
        webLayout = self.findChild(QVBoxLayout, "webLayout")
        self.webView = QWebEngineView()
        self.webView.urlChanged.connect(self.onUrlChanged)
        self.webView.load(self.HOME_PAGE)
        self.webView.setStyleSheet("background-color: white")
        webLayout.addWidget(self.webView)
        self.webView.hide()
        
        # Add Home view
        self.homeFrame = self.findChild(QFrame, "homeFrame")
        self.webSearchInput = self.findChild(QTextEdit, "webSearchTxt")
        self.webSearchInput.textChanged.connect(self.toggleEnterBtn)
        self.searchKeyPressEater = SearchInputKeyEater(self)
        self.webSearchInput.installEventFilter(self.searchKeyPressEater)
        self.findAndSetIcon(QPushButton, "homeFavouritesBtn", self.HOME_HEART_IMG, self.HOME_BUTTONS_SIZE, self.onFavouritesBtnClicked)
        self.findAndSetIcon(QPushButton, "homeActionLogBtn", self.HOME_HISTORY_IMG, self.HOME_BUTTONS_SIZE, self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "homeSettingsBtn", self.HOME_SETTINGS_IMG, self.HOME_BUTTONS_SIZE, self.onSettingsBtnClicked)
        self.findAndSetIcon(QLabel, "searchIcon", self.SEARCH_IMG, self.INTERNET_SIZE)

        # Configure Enter button
        self.enterBtn = self.findChild(QPushButton, "enterQueryBtn")
        self.enterBtn.clicked.connect(self.enterQuery)
        self.enterBtn.hide()
        self.backBtn = self.findChild(QPushButton, "backBtn")
        self.backBtn.clicked.connect(self.goBack)
        self.backBtn.hide()

        # Configure Textedit
        self.queryInput = self.findChild(QTextEdit, "AI_InputEdit")
        self.queryInput.textChanged.connect(self.toggleEnterBtn)
        self.keyPressEater = QueryInputKeyEaster(self)
        self.queryInput.installEventFilter(self.keyPressEater)

        # Set icons and buttons
        self.findAndSetIcon(QPushButton, "microBtn", self.MICROPHONE_IMG, self.MICROPHONE_SIZE,
                            self.onMicroBtnClicked)
        self.findAndSetIcon(QPushButton, "inputInternetBtn", self.INTERNET_IMG, self.INTERNET_SIZE,
                            lambda: self.createAPopup(*self.INPUT_INFO))
        self.findAndSetIcon(QPushButton, "menuInternetBtn", self.INTERNET_IMG, (40, 40),
                            lambda: self.createAPopup(*self.GENERAL_INFO))

        self.findAndSetIcon(QPushButton, "homeBtn", self.HOME_IMG, self.MICROPHONE_SIZE,
                            self.onHomeBtnClicked)
        self.findAndSetIcon(QPushButton, "actionLogBtn", self.ACTION_LOG_IMG, self.MICROPHONE_SIZE,
                            self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "settingsBtn", self.SETTINGS_IMG, self.MICROPHONE_SIZE,
                            self.onSettingsBtnClicked)

        for i in range(1, self.NO_STARS + 1):
            btn = self.findAndSetIcon(
                QPushButton, f"starBtn{i}", self.STAR_FILLED_IMG, self.STAR_SIZE, partial(self.starBtnPressed, i)
            )
            btn.installEventFilter(ButtonHoverHandler(self))
            self.starBtns.append(btn)

        # Find Labels
        self.FAQLabel = self.findChild(QLabel, "FAQLabel")
        self.helpfulLabel = self.findChild(QLabel, "helpfulLabel")

        self.showRating(False)

    @staticmethod
    def createAPopup(title, body):
        msg = QMessageBox()
        msg.setText(body)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def deleteSpacer(self, no):
        count = 0
        for i in range(self.FAQLayout.count()):
            item = self.FAQLayout.itemAt(i)
            if isinstance(item, QSpacerItem):
                if count == no:
                    self.FAQLayout.takeAt(i)
                    del item
                    break
                count += 1

    def goBack(self):
        self.queryInput.clear()
        self.displayFAQs(self.domain, False)
        self.FAQLayout.insertStretch(3)

    def showRating(self, show):
        self.helpfulLabel.setVisible(show)
        for btn in self.starBtns:
            btn.setVisible(show)

    def starBtnPressed(self, val):
        print(f"Rated {val}/{self.NO_STARS}")

    def onHovered(self, val):
        for i, btn in enumerate(self.starBtns):
            if i < val:
                # Set filled
                btn.setIcon(QIcon(self.STAR_FILLED_IMG.__str__()))
            else:
                # Set empty
                btn.setIcon(QIcon(self.STAR_EMPTY_IMG.__str__()))

    def findAndSetIcon(self, QType, name, path, size, action=None):
        icon = self.findChild(QType, name)

        if action:
            icon.setIcon(QIcon(path.__str__()))
            icon.setIconSize(QSize(*size))
            icon.clicked.connect(action)
        else:
            pixmap = QPixmap(path.__str__())
            pixmap = pixmap.scaled(QSize(*size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon.setPixmap(pixmap)

        return icon

    def onUrlChanged(self, url):
        changedDomain = getDomainName(url.toString().lower())
        if changedDomain != self.domain:
            # Website has changed
            self.domain = changedDomain
            self.displayFAQs(changedDomain)
            self.showRating(False)
            self.backBtn.hide()

    @staticmethod
    def clearLayout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def displayFAQs(self, domain, fetch=True):
        self.clearLayout(self.FAQBtnLayout)
        self.backBtn.hide()
        self.showRating(False)
        self.FAQLabel.show()
        if fetch:
            self.currentQs = self.database.getFAQ(domain)[:self.MAX_QUESTIONS]
        for q in self.currentQs:
            btn = QPushButton(textwrap.fill(q, self.TEXT_WIDTH))
            btn.setStyleSheet(self.buttonStyle)
            btn.clicked.connect(partial(self.insertQuestion, q))
            self.FAQBtnLayout.addWidget(btn)

    def insertQuestion(self, question):
        self.queryInput.clear()
        self.queryInput.insertPlainText(question)

    @staticmethod
    def onMicroBtnClicked():
        print("Microphone button clicked")

    def onHomeBtnClicked(self):
        self.webView.load(self.HOME_PAGE)

    @staticmethod
    def onSettingsBtnClicked():
        print("Settings button clicked")

    @staticmethod
    def onActionLogBtnClicked():
        print("Action Log button clicked")
    
    @staticmethod
    def onFavouritesBtnClicked():
        print("Favourites button clicked")
    
    @staticmethod
    def onActionLogBtnClicked():
        print("Action Log button clicked")

    def toggleEnterBtn(self):
        if self.queryInput.toPlainText().strip():
            self.enterBtn.show()
        else:
            self.enterBtn.hide()

    def enterQuery(self):
        inputText = self.queryInput.toPlainText()
        if inputText.replace("\n", ""):
            self.webView.grab().save(self.screenshotPath, b'JPEG')
            result = self.aiAssistant.singleRequest(inputText)
            self.showText(result)
            self.showRating(True)
            self.deleteSpacer(1)
            self.backBtn.show()
        else:
            self.queryInput.insertPlainText("\n")
        self.database.addFAQ(inputText, self.domain)

    def showText(self, text):
        self.clearLayout(self.FAQBtnLayout)
        self.FAQLabel.hide()
        textEdit = QTextEdit()
        textEdit.insertPlainText(text)
        textEdit.moveCursor(textEdit.textCursor().Start)
        textEdit.setReadOnly(True)

        font = textEdit.font()
        font.setPointSize(self.FONT_SIZE)
        textEdit.setFont(font)

        self.FAQBtnLayout.addWidget(textEdit)
        
    def search(self):
        inputText = self.webSearchInput.toPlainText()
        if inputText.replace("\n", ""):
            print(f"Searching Web: '{inputText}'")
            self.webView.load(QUrl("https://www.google.co.uk/search?q=" + inputText))
            self.homeFrame.hide()
            self.webView.show()
        else:
            self.queryInput.insertPlainText("\n")
