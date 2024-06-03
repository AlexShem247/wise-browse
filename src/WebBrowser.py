import textwrap
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QTextEdit
from src.Assistant import Assistant, Model

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
        webLayout.addWidget(self.webView)

        # Configure Microphone button
        microBtn = self.findChild(QPushButton, "microBtn")
        microBtn.setIcon(QIcon(self.MICROPHONE_IMG.__str__()))
        microBtn.setIconSize(QSize(*self.MICROPHONE_SIZE))
        microBtn.clicked.connect(self.onMicroBtnClicked)

        # Configure Enter button
        self.enterBtn = self.findChild(QPushButton, "enterQueryBtn")
        self.enterBtn.clicked.connect(self.enterQuery)
        self.enterBtn.hide()

        # Configure Textedit
        self.queryInput = self.findChild(QTextEdit, "AI_InputEdit")
        self.queryInput.textChanged.connect(self.toggleEnterBtn)
        self.keyPressEater = QueryInputKeyEaster(self)
        self.queryInput.installEventFilter(self.keyPressEater)

        internetIcon = self.findChild(QLabel, "inputInternetIcon")
        pixmap = QPixmap(self.INTERNET_IMG.__str__())
        pixmap = pixmap.scaled(QSize(*self.INTERNET_SIZE), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        internetIcon.setPixmap(pixmap)

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
        self.webView.grab().save("screenshot.jpeg", b'JPEG')
        if inputText.replace("\n", ""):
            print(f"Entering query: '{inputText}'")
            result = Assistant().singleRequest(inputText, Model.dummy) # dummy to not use up tokens
            # result = Assistant().singleRequest(inputText, Model.budget) # only plaint text as input
            # result = Assistant().singleImageRequest(inputText, Model.full, "screenshot.jpeg") # with image
            self.queryInput.clear()
            self.queryInput.setText(result)
        else:
            self.queryInput.insertPlainText("\n")
        self.database.addFAQ(inputText)
