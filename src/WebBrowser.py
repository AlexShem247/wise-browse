import textwrap
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel

from src import URLUtils
from src.FAQDatabase import FAQDatabase


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
    FAQLayout: QVBoxLayout = None
    buttonStyle = None

    database = FAQDatabase()

    def __init__(self):
        super().__init__()
        uic.loadUi(self.UI_FILE, self)

        # Configure Window
        self.setWindowTitle(self.WINDOW_TITLE)

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

        self.FAQLayout = self.findChild(QVBoxLayout, "FAQLayout")
        self.buttonStyle = self.findChild(QPushButton, "sampleQuestionBtn").styleSheet()

        internetIcon = self.findChild(QLabel, "internetIcon")
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
