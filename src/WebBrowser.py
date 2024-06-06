import os
import tempfile
import textwrap
from pathlib import Path
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpacerItem, QSizePolicy, \
    QMessageBox, QFrame, QLineEdit, QStackedWidget, QWidget, QToolTip

from src.URLUtils import getDomainName
from src.FAQDatabase import FAQDatabase
from src.EventFilters import QueryInputKeyEaster, ButtonHoverHandler, SearchInputKeyEater
from src.Assistant import Assistant, Model
from src.Favourites import Favourites


class WebBrowser(QMainWindow):
    UI_FILE = Path("assets/UI/MainPage.ui")
    WINDOW_TITLE = "Wise Browse"
    PLACEHOLDER_TEXT = "Ask me anything..."
    HOME_PAGE = QUrl("https://www.google.com")
    currentWebpage = None

    MICROPHONE_IMG = Path("assets/img/microphone.png")
    INTERNET_IMG = Path("assets/img/internet.png")
    HOME_IMG = Path("assets/img/home.png")
    ACTION_LOG_IMG = Path("assets/img/clipboard.png")
    SETTINGS_IMG = Path("assets/img/settings.png")
    STAR_EMPTY_IMG = Path("assets/img/star_empty.png")
    STAR_FILLED_IMG = Path("assets/img/star_filled.png")

    STOP_IMG = Path("assets/img/stop.png")

    SEARCH_IMG = Path("assets/img/search.png")
    HOME_HEART_IMG = Path("assets/img/heart.png")
    HOME_HISTORY_IMG = Path("assets/img/history.png")
    HOME_SETTINGS_IMG = Path("assets/img/setting.png")
    REDO_IMG = Path("assets/img/redo.png")
    REFRESH_IMG = Path("assets/img/refresh.png")
    UNDO_IMG = Path("assets/img/undo.png")
    HEART_NO_FILL_IMG = Path("assets/img/heartNoFill.png")
    HEART_FILL_IMG = Path("assets/img/heartFill.png")
    
    LEFT_ARROW_IMG = Path("assets/img/leftArrow.png")
    RIGHT_ARROW_IMG = Path("assets/img/rightArrow.png")
    
    INTERNET_SIZE = (30, 30)
    MICROPHONE_SIZE = (20, 20)
    STAR_SIZE = (15, 15)
    HOME_BUTTONS_SIZE = (60, 60)
    LOGO_SIZE = (40, 40)
    TOOLBAR_ICON_SIZE = (20, 20)
    ARROW_SIZE = (50,50)

    TEXT_WIDTH = 30
    FONT_SIZE = 11
    NO_STARS = 5
    MAX_QUESTIONS = 8
    TEXT_DELAY_MS = 20

    window = None
    buttonStyle = None

    FAQLayout: QVBoxLayout
    FAQBtnLayout: QVBoxLayout
    enterBtn: QPushButton
    backBtn: QPushButton
    queryInput: QTextEdit
    FAQLabel: QLabel
    helpfulLabel: QLabel
    microphoneBtn: QPushButton
    starBtns = []

    homeFrame: QFrame
    webSearchInput: QTextEdit
    homeFavouritesBtn = QPushButton
    homeActionLogBtn = QPushButton
    homeSettingsBtn = QPushButton
    
    likedLeftArrow = QPushButton
    mostUsedLeftArrow = QPushButton

    AI_MODEL_TYPE = Model.dummy
    _, screenshotPath = tempfile.mkstemp()
    aiAssistant = Assistant(AI_MODEL_TYPE, screenshotPath)

    database = FAQDatabase(aiAssistant)
    domain = None
    currentQs = []

    INPUT_INFO = ("Inputting Information", "Someone write something here.")
    GENERAL_INFO = (WINDOW_TITLE, "Someone write something here.")

    isRecording = False
    MICROPHONE_TIME_DELAY = 1000
    INPUT_TIME_DELAY = 500
    currentNoDots = 0
    NO_DOTS = 3

    previousWebpages = []
    nextWebpages = []
    switchingPages = False
    
    favourites = Favourites()
    
    pages: QStackedWidget
    homePage: QWidget
    favouritesPage: QWidget
    actionLogPage: QWidget
    settingsPage: QWidget
    web: QWidget
    
    def __init__(self):
        super().__init__()
        uic.loadUi(self.UI_FILE, self)
        
        self.setWindowTitle(self.WINDOW_TITLE)
        self.initLowerBar()
        self.initUpperSearchBar()
        self.initAISideBar()
        self.initWeb()
        
        self.initPages()
        self.initHomePage()
        self.initFavouritesPage()
        # self.initActionLogPage()
        # self.initSettingsPage()
        


    def initLowerBar(self):
        self.findAndSetIcon(QPushButton, "menuInternetBtn", self.INTERNET_IMG, self.LOGO_SIZE, lambda: self.createAPopup(*self.GENERAL_INFO))
        self.findAndSetIcon(QPushButton, "homeBtn", self.HOME_IMG, self.MICROPHONE_SIZE, self.onHomeBtnClicked)
        self.findAndSetIcon(QPushButton, "actionLogBtn", self.ACTION_LOG_IMG, self.MICROPHONE_SIZE, self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "settingsBtn", self.SETTINGS_IMG, self.MICROPHONE_SIZE, self.onSettingsBtnClicked)        
        
    def initUpperSearchBar(self):
        self.previousPageBtn = self.findAndSetIcon(QPushButton, "previousPageBtn", self.UNDO_IMG, self.TOOLBAR_ICON_SIZE, self.previousPage)
        self.previousPageBtn.setEnabled(False)
        self.nextPageBtn = self.findAndSetIcon(QPushButton, "nextPageBtn", self.REDO_IMG, self.TOOLBAR_ICON_SIZE, self.nextPage)
        self.nextPageBtn.setEnabled(False)
        self.findAndSetIcon(QPushButton, "refreshBtn", self.REFRESH_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.webView.load(self.currentWebpage))
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.favouritePage(self.currentWebpage))
        self.urlEdit = self.findChild(QLineEdit, "urlEdit")
        self.urlEdit.installEventFilter(SearchInputKeyEater(self))
        
    def initAISideBar(self):
        self.buttonStyle = self.findChild(QPushButton, "sampleQuestionBtn").styleSheet()
        self.FAQLayout = self.findChild(QVBoxLayout, "FAQLayout")
        self.FAQBtnLayout = self.findChild(QVBoxLayout, "FAQBtnLayout")
        self.clearLayout(self.FAQBtnLayout)
        
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
        self.microphoneBtn = self.findAndSetIcon(QPushButton, "microBtn", self.MICROPHONE_IMG, self.MICROPHONE_SIZE, self.onMicroBtnClicked)
        self.findAndSetIcon(QPushButton, "inputInternetBtn", self.INTERNET_IMG, self.INTERNET_SIZE, lambda: self.createAPopup(*self.INPUT_INFO))
        
        # Configure stars
        for i in range(1, self.NO_STARS + 1):
            btn = self.findAndSetIcon(
                QPushButton, f"starBtn{i}", self.STAR_FILLED_IMG, self.STAR_SIZE, partial(self.starBtnPressed, i)
            )
            btn.installEventFilter(ButtonHoverHandler(self))
            self.starBtns.append(btn)

        # Find Labels
        self.FAQLabel = self.findChild(QLabel, "FAQLabel")
        self.helpfulLabel = self.findChild(QLabel, "helpfulLabel")

        # Configure Microphone
        self.microphoneTimer = QTimer()
        self.microphoneTimer.timeout.connect(self.toggleMicrophoneVisibility)
        self.inputTimer = QTimer()
        self.inputTimer.timeout.connect(self.toggleInputText)

        self.showRating(False)
        
    def initWeb(self):
        # Add WebView
        webLayout = self.findChild(QVBoxLayout, "google")
        self.webView = QWebEngineView()
        self.webView.urlChanged.connect(self.onUrlChanged)
        self.webView.load(self.HOME_PAGE)
        self.webView.setStyleSheet("background-color: white")
        webLayout.addWidget(self.webView)
        
    def initPages(self):
        self.pages = self.findChild(QStackedWidget, "pages")
        self.homePage = self.findChild(QWidget, "homePage")
        self.favouritesPage = self.findChild(QWidget, "favouritesPage")
        self.actionLogPage = self.findChild(QWidget, "actionLogPage")
        self.settingsPage = self.findChild(QWidget, "settingsPage")
        self.web = self.findChild(QWidget, "web")
        self.pages.setCurrentWidget(self.homePage)
    
    def initHomePage(self):
        self.homeFrame = self.findChild(QFrame, "homeFrame")
        self.webSearchInput = self.findChild(QTextEdit, "webSearchTxt")
        self.webSearchInput.textChanged.connect(self.toggleEnterBtn)
        self.searchKeyPressEater = SearchInputKeyEater(self)
        self.webSearchInput.installEventFilter(self.searchKeyPressEater)
        self.findAndSetIcon(QPushButton, "homeFavouritesBtn", self.HOME_HEART_IMG, self.HOME_BUTTONS_SIZE, self.onFavouritesBtnClicked)
        self.findAndSetIcon(QPushButton, "homeActionLogBtn", self.HOME_HISTORY_IMG, self.HOME_BUTTONS_SIZE, self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "homeSettingsBtn", self.HOME_SETTINGS_IMG, self.HOME_BUTTONS_SIZE, self.onSettingsBtnClicked)
        self.findAndSetIcon(QLabel, "searchIcon", self.SEARCH_IMG, self.INTERNET_SIZE)
        
    def initFavouritesPage(self):
        self.likedLeftArrow = self.findAndSetIcon(QPushButton, "likedLeftArrow", self.LEFT_ARROW_IMG, self.ARROW_SIZE, lambda: self.favourites.clickLikedLeftArrow(self))
        self.likedLeftArrow.hide()
        self.findAndSetIcon(QPushButton, "likedRightArrow", self.RIGHT_ARROW_IMG, self.ARROW_SIZE, lambda: self.favourites.clickLikedRightArrow(self))
        self.mostUsedLeftArrow = self.findAndSetIcon(QPushButton, "mostVisitedLeftArrow", self.LEFT_ARROW_IMG, self.ARROW_SIZE, lambda: self.favourites.clickMostUsedLeftArrow(self))
        self.mostUsedLeftArrow.hide()
        self.findAndSetIcon(QPushButton, "mostVisitedRightArrow", self.RIGHT_ARROW_IMG, self.ARROW_SIZE, lambda: self.favourites.clickMostUsedRightArrow(self))        
        




    def toggleMicrophoneVisibility(self):
        if self.microphoneBtn.icon().isNull():
            self.microphoneBtn.setIcon(QIcon(self.STOP_IMG.__str__()))
            self.microphoneBtn.setIconSize(QSize(*self.MICROPHONE_SIZE))
            self.microphoneTimer.start(self.MICROPHONE_TIME_DELAY)
        else:
            self.microphoneBtn.setIcon(QIcon())
            self.microphoneTimer.start(self.MICROPHONE_TIME_DELAY // 2)

    def toggleInputText(self):
        self.currentNoDots = (self.currentNoDots + 1) % (self.NO_DOTS + 1)
        self.queryInput.setPlaceholderText("Recording" + "." * self.currentNoDots)

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
    
    def clearIcon(self, QType, name):
        icon = self.findChild(QType, name)
        icon.setIcon(QIcon())
        try:
            icon.clicked.disconnect()
        except TypeError:
            pass
        return icon

    def nextPage(self):
        self.switchingPages = True
        self.previousWebpages.append(self.previousWebpages.pop())
        self.previousPageBtn.setEnabled(True)
        self.nextPageBtn.setEnabled(len(self.nextWebpages) > 1)
        self.webView.load(self.nextWebpages.pop())

    def previousPage(self):
        self.switchingPages = True
        self.nextWebpages.append(self.previousWebpages.pop())
        self.nextPageBtn.setEnabled(True)
        self.previousPageBtn.setEnabled(len(self.previousWebpages) > 1)
        self.webView.load(self.previousWebpages[-1])
    
    def favouritePage(self, url):
        self.favourites.addLikedSite(url)
        self.clearIcon(QPushButton, "favSiteBtn")
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_FILL_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.unfavouritePage(self.currentWebpage))
        
    def unfavouritePage(self, url):
        self.favourites.removeLikedSite(url)
        self.clearIcon(QPushButton, "favSiteBtn")
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.favouritePage(self.currentWebpage))
        
    

    def onUrlChanged(self, url):
        changedDomain = getDomainName(url.toString().lower())
        self.currentWebpage = url
        if not self.previousWebpages or self.previousWebpages[-1] != url:
            self.previousWebpages.append(url)

        if len(self.previousWebpages) > 1:
            self.previousPageBtn.setEnabled(True)

        self.urlEdit.setText(url.toString())
        self.urlEdit.setCursorPosition(0)
        if changedDomain != self.domain:
            # Website has changed
            self.domain = changedDomain
            self.displayFAQs(changedDomain)
            self.showRating(False)
            self.backBtn.hide()

        if not self.switchingPages:
            self.nextWebpages = []
            self.nextPageBtn.setEnabled(False)
        self.switchingPages = False
        
        self.favourites.incrementSiteUses(url)
        self.clearIcon(QPushButton, "favSiteBtn")
        if (self.favourites.isLikedSite(url)):
            self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_FILL_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.unfavouritePage(self.currentWebpage))
        else:
            self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE, lambda: self.favouritePage(self.currentWebpage))

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

    def addInputText(self, word):
        self.queryInput.setText(self.queryInput.toPlainText() + word + " ")
        self.inputTimer.stop()

    def onMicroBtnClicked(self):
        if self.isRecording:
            path = self.MICROPHONE_IMG
            print("Stop Recording")
            self.microphoneTimer.stop()
            self.inputTimer.stop()
            self.queryInput.setPlaceholderText(self.PLACEHOLDER_TEXT)
        else:
            path = self.STOP_IMG
            self.microphoneTimer.start(self.MICROPHONE_TIME_DELAY)
            self.inputTimer.start(self.INPUT_TIME_DELAY)
            self.queryInput.setPlaceholderText("Recording")
            print("Start Recording")

        self.microphoneBtn.setIcon(QIcon(path.__str__()))
        self.microphoneBtn.setIconSize(QSize(*self.MICROPHONE_SIZE))
        self.isRecording = not self.isRecording

    def onHomeBtnClicked(self):
        self.pages.setCurrentWidget(self.homePage)
        print("Home button clicked")
        self.webView.load(self.HOME_PAGE)

    def onSettingsBtnClicked(self):
        self.pages.setCurrentWidget(self.settingsPage)
        print("Settings button clicked")

    def onActionLogBtnClicked(self):
        self.pages.setCurrentWidget(self.actionLogPage)
        print("Action Log button clicked")

    def onFavouritesBtnClicked(self):
        self.pages.setCurrentWidget(self.favouritesPage)
        self.favourites.displayFavourites(self)
        print("Favourites button clicked")
        
    def search(self):
        inputText = self.webSearchInput.toPlainText()
        if inputText.replace("\n", ""):
            self.webView.load(QUrl("https://www.google.co.uk/search?q=" + inputText))
            self.pages.setCurrentWidget(self.web)
            print(f"Searching Web: '{inputText}'")
        else:
            self.queryInput.insertPlainText("\n")
    
    def gotoURL(self, url):
        print(url)
        self.webView.load(QUrl(url))
        self.pages.setCurrentWidget(self.web)
        print(f"Go to: '{url}'")


    def toggleEnterBtn(self):
        if self.queryInput.toPlainText().strip():
            self.enterBtn.show()
        else:
            self.enterBtn.hide()

    def enterQuery(self):
        if self.isRecording:
            self.onMicroBtnClicked()
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
        textEdit.moveCursor(textEdit.textCursor().Start)
        textEdit.setReadOnly(True)

        font = textEdit.font()
        font.setPointSize(self.FONT_SIZE)
        textEdit.setFont(font)

        self.FAQBtnLayout.addWidget(textEdit)
        self.slowlyTypeText(textEdit, text)

    def slowlyTypeText(self, textEdit, text):
        index = 0

        def insertCharacter():
            nonlocal index
            if index < len(text):
                textEdit.insertPlainText(text[index])
                index += 1
            else:
                timer.stop()

        timer = QTimer()
        timer.timeout.connect(insertCharacter)
        timer.start(self.TEXT_DELAY_MS)
    
    def closeEvent(self, event):
        self.favourites.writeFavourites()
