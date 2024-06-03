import textwrap
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QTextEdit

from src import URLUtils
from src.FAQDatabase import FAQDatabase
from src.QueryInputKeyEater import QueryInputKeyEaster


class WebBrowser(QMainWindow):
    UI_FILE = Path("assets/UI/MainPage.ui")
    WINDOW_TITLE = "Web Browser"
    HOME_PAGE = QUrl("https://www.google.com")

    MICROPHONE_IMG = Path("assets/img/microphone.png")
    MICROPHONE_SIZE = (20, 20)
    BUTTON_TEXT_WIDTH = 30

    INTERNET_IMG = Path("assets/img/internet.png")
    INTERNET_SIZE = (30, 30)

    window = None
    buttonStyle = None
    FAQLayout: QVBoxLayout = None
    enterBtn: QPushButton
    queryInput: QTextEdit

    database = FAQDatabase()

    def __init__(self):
        super().__init__()
        uic.loadUi(self.UI_FILE, self)

        # Configure Window
        self.setWindowTitle(self.WINDOW_TITLE)
        self.buttonStyle = self.findChild(QPushButton, "sampleQuestionBtn").styleSheet()
        self.FAQLayout = self.findChild(QVBoxLayout, "FAQBtnLayout")
        self.clearLayout(self.FAQLayout)

        # Add WebView
        webLayout = self.findChild(QVBoxLayout, "webLayout")

        self.webView = QWebEngineView()
        self.webView.urlChanged.connect(self.onUrlChanged)
        self.webView.load(self.HOME_PAGE)
        self.webView.setStyleSheet("background-color: white")
        webLayout.addWidget(self.webView)

        # Configure Enter button
        self.enterBtn = self.findChild(QPushButton, "enterQueryBtn")
        self.enterBtn.clicked.connect(self.enterQuery)
        self.enterBtn.hide()

        # Configure Textedit
        self.queryInput = self.findChild(QTextEdit, "AI_InputEdit")
        self.queryInput.textChanged.connect(self.toggleEnterBtn)
        self.keyPressEater = QueryInputKeyEaster(self)
        self.queryInput.installEventFilter(self.keyPressEater)

        # Set icons and buttons
        self.setIcon(QPushButton, "microBtn", self.MICROPHONE_IMG, self.MICROPHONE_SIZE,
                     self.onMicroBtnClicked)
        self.setIcon(QLabel, "inputInternetIcon", self.INTERNET_IMG, self.INTERNET_SIZE)
        self.setIcon(QLabel, "menuInternetIcon", self.INTERNET_IMG, self.INTERNET_SIZE)

    def setIcon(self, QType, name, path, size, action=None):
        icon = self.findChild(QType, name)

        if action:
            icon.setIcon(QIcon(path.__str__()))
            icon.setIconSize(QSize(*size))
            icon.clicked.connect(action)
        else:
            pixmap = QPixmap(path.__str__())
            pixmap = pixmap.scaled(QSize(*size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon.setPixmap(pixmap)

    def onUrlChanged(self, url):
        domain = URLUtils.getDomainName(url.toString().lower())
        print(f"URL changed: {url.toString()}")
        self.displayFAQs(domain)

    @staticmethod
    def clearLayout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def displayFAQs(self, domain):
        self.clearLayout(self.FAQLayout)
        qs = self.database.getFAQ(domain)
        for q in qs:
            btn = QPushButton(textwrap.fill(q, self.BUTTON_TEXT_WIDTH))
            btn.setStyleSheet(self.buttonStyle)
            self.FAQLayout.addWidget(btn)

    @staticmethod
    def onMicroBtnClicked():
        print("Microphone button clicked")

    def toggleEnterBtn(self):
        if self.queryInput.toPlainText().strip():
            self.enterBtn.show()
        else:
            self.enterBtn.hide()

    def enterQuery(self):
        inputText = self.queryInput.toPlainText()
        if inputText.replace("\n", ""):
            print(f"Entering query: '{inputText}'")
        else:
            self.queryInput.insertPlainText("\n")
