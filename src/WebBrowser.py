import os
import re
import tempfile
import textwrap
from pathlib import Path
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QSize, QUrl, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpacerItem, QSizePolicy, \
    QMessageBox, QFrame, QLineEdit, QStackedWidget, QWidget, QToolTip, QHBoxLayout

from src.URLUtils import getDomainName, isUrl
from src.FAQDatabase import FAQDatabase
from src.EventFilters import QueryInputKeyEaster, ButtonHoverHandler, SearchInputKeyEater
from src.Assistant import Assistant, Model
from src.Favourites import Favourites
from src.FeedbackPopup import FeedbackPopup
from src.SearchHistory import SearchHistory

import threading
import speech_recognition as sr


def formatHtml(text):
    # Regular expression to find lines starting with ###
    pattern = re.compile(r'^(###\s*)(.*)', re.MULTILINE)

    # Replace the pattern with the HTML <h2> tag
    text = pattern.sub(r'<h2>\2</h2>', text)

    # Regular expression to find text enclosed in **
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    # Replace the pattern with the HTML <b> tag
    text = bold_pattern.sub(r'<b>\1</b>', text)

    text = text.replace("\n\n", "\n")
    text = text.replace("\n", "<br>")

    return text


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
    ARROW_SIZE = (50, 50)
    MAIN_LOGO_SIZE = (100, 100)

    TEXT_WIDTH = 30
    FONT_SIZE = 11
    NO_STARS = 5
    MAX_QUESTIONS = 8
    TEXT_DELAY_MS = 0

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

    AI_MODEL_TYPE = Model.full
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

    searchHistory = SearchHistory()

    manualSearch = False

    pages: QStackedWidget
    homePage: QWidget
    favouritesPage: QWidget
    actionLogPage: QWidget
    settingsPage: QWidget
    web: QWidget
    webView: QWebEngineView

    previousPageBtn = None
    nextPageBtn = None
    urlEdit = None
    keyPressEater = None
    microphoneTimer = None
    inputTimer = None
    thinkingTimer = None
    searchKeyPressEater = None
    popUp = None

    update_text_signal = pyqtSignal(str)
    AudioError = False
    recordingNotStopped = False

    previousWebpages = []
    switchingPages = False

    update_result = pyqtSignal(str)

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
        self.initActionLogPage()
        # self.initSettingsPage()

    def initLowerBar(self):
        self.findAndSetIcon(QPushButton, "menuInternetBtn", self.INTERNET_IMG, self.LOGO_SIZE,
                            lambda: self.createAPopup(*self.GENERAL_INFO))
        self.findAndSetIcon(QPushButton, "homeBtn", self.HOME_IMG, self.MICROPHONE_SIZE, self.onHomeBtnClicked)
        self.findAndSetIcon(QPushButton, "actionLogBtn", self.ACTION_LOG_IMG, self.MICROPHONE_SIZE,
                            self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "settingsBtn", self.SETTINGS_IMG, self.MICROPHONE_SIZE,
                            self.onSettingsBtnClicked)

    def initUpperSearchBar(self):
        self.previousPageBtn = self.findAndSetIcon(QPushButton, "previousPageBtn", self.UNDO_IMG,
                                                   self.TOOLBAR_ICON_SIZE, self.previousPage)
        self.previousPageBtn.setEnabled(False)
        self.nextPageBtn = self.findAndSetIcon(QPushButton, "nextPageBtn", self.REDO_IMG, self.TOOLBAR_ICON_SIZE,
                                               self.nextPage)
        self.nextPageBtn.setEnabled(False)

        self.findAndSetIcon(QPushButton, "refreshBtn", self.REFRESH_IMG, self.TOOLBAR_ICON_SIZE,
                            lambda: self.webView.load(self.currentWebpage))
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE,
                            lambda: self.favouritePage(self.currentWebpage))

        self.urlEdit = self.findChild(QLineEdit, "urlEdit")
        self.urlEdit.returnPressed.connect(self.doManualSearch)

    def doManualSearch(self):
        url = isUrl(self.urlEdit.text())

        self.urlEdit.setText(url)
        self.manualSearch = True
        self.webView.load(QUrl(url))

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
        self.microphoneBtn = self.findAndSetIcon(QPushButton, "microBtn", self.MICROPHONE_IMG, self.MICROPHONE_SIZE,
                                                 self.onMicroBtnClicked)
        self.findAndSetIcon(QPushButton, "inputInternetBtn", self.INTERNET_IMG, self.INTERNET_SIZE,
                            lambda: self.createAPopup(*self.INPUT_INFO))

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
        self.thinkingTimer = QTimer()
        self.thinkingTimer.timeout.connect(self.toggleEnterBtnText)

        self.showRating(False)

        self.update_text_signal.connect(self.addInputText)

    def toggleEnterBtnText(self):
        self.currentNoDots = (self.currentNoDots + 1) % (self.NO_DOTS + 1)
        self.enterBtn.setText("The AI is thinking" + "." * self.currentNoDots)

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
        self.findAndSetIcon(QPushButton, "homeFavouritesBtn", self.HOME_HEART_IMG, self.HOME_BUTTONS_SIZE,
                            self.onFavouritesBtnClicked)
        self.findAndSetIcon(QPushButton, "homeActionLogBtn", self.HOME_HISTORY_IMG, self.HOME_BUTTONS_SIZE,
                            self.onActionLogBtnClicked)
        self.findAndSetIcon(QPushButton, "homeSettingsBtn", self.HOME_SETTINGS_IMG, self.HOME_BUTTONS_SIZE,
                            self.onSettingsBtnClicked)
        self.findAndSetIcon(QLabel, "searchIcon", self.SEARCH_IMG, self.INTERNET_SIZE)

    def initFavouritesPage(self):
        self.likedLeftArrow = self.findAndSetIcon(QPushButton, "likedLeftArrow", self.LEFT_ARROW_IMG, self.ARROW_SIZE,
                                                  lambda: self.favourites.clickLikedLeftArrow(self))
        self.likedLeftArrow.hide()
        self.findAndSetIcon(QPushButton, "likedRightArrow", self.RIGHT_ARROW_IMG, self.ARROW_SIZE,
                            lambda: self.favourites.clickLikedRightArrow(self))
        self.mostUsedLeftArrow = self.findAndSetIcon(QPushButton, "mostVisitedLeftArrow", self.LEFT_ARROW_IMG,
                                                     self.ARROW_SIZE,
                                                     lambda: self.favourites.clickMostUsedLeftArrow(self))
        self.mostUsedLeftArrow.hide()
        self.findAndSetIcon(QPushButton, "mostVisitedRightArrow", self.RIGHT_ARROW_IMG, self.ARROW_SIZE,
                            lambda: self.favourites.clickMostUsedRightArrow(self))

        self.findAndSetIcon(QLabel, "browserLogoIcon", self.INTERNET_IMG, self.MAIN_LOGO_SIZE)

    def initActionLogPage(self):
        self.visitedLeftArrow = self.findAndSetIcon(QPushButton, "visitedLeftArrow", self.LEFT_ARROW_IMG,
                                                    self.ARROW_SIZE,
                                                    lambda: self.searchHistory.clickVisitedLeftArrow(self))
        self.visitedLeftArrow.hide()
        self.visitedRightArrow = self.findAndSetIcon(QPushButton, "visitedRightArrow", self.RIGHT_ARROW_IMG, self.ARROW_SIZE, lambda: self.searchHistory.clickVisitedRightArrow(self))
        self.visitedRightArrow.hide()
        self.visitedLeftArrow_2 = self.findAndSetIcon(QPushButton, "visitedLeftArrow_2", self.LEFT_ARROW_IMG, self.ARROW_SIZE, lambda: self.searchHistory.clickVisitedLeftArrow_2(self))
        self.visitedLeftArrow_2.hide()
        self.visitedRightArrow_2 = self.findAndSetIcon(QPushButton, "visitedRightArrow_2", self.RIGHT_ARROW_IMG, self.ARROW_SIZE, lambda: self.searchHistory.clickVisitedRightArrow_2(self))
        self.visitedRightArrow_2.hide()
        self.visitedLeftArrow_3 = self.findAndSetIcon(QPushButton, "visitedLeftArrow_3", self.LEFT_ARROW_IMG, self.ARROW_SIZE, lambda: self.searchHistory.clickVisitedLeftArrow_3(self))
        self.visitedLeftArrow_3.hide()
        self.visitedRightArrow_3 = self.findAndSetIcon(QPushButton, "visitedRightArrow_3", self.RIGHT_ARROW_IMG, self.ARROW_SIZE, lambda: self.searchHistory.clickVisitedRightArrow_3(self))
        self.visitedRightArrow_3.hide()

        self.historydate_1 = self.findChild(QLineEdit, "historydate_1")
        self.historydate_2 = self.findChild(QLineEdit, "historydate_2")
        self.historydate_3 = self.findChild(QLineEdit, "historydate_3")



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
        self.displayFAQs(self.domain, True)
        self.FAQLayout.insertStretch(3)

    def showRating(self, show):
        self.helpfulLabel.setVisible(show)
        for btn in self.starBtns:
            btn.setVisible(show)

    def starBtnPressed(self, val):
        self.popUp = FeedbackPopup(val, self.NO_STARS)
        self.popUp.show()

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
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_FILL_IMG, self.TOOLBAR_ICON_SIZE,
                            lambda: self.unfavouritePage(self.currentWebpage))

    def unfavouritePage(self, url):
        self.favourites.removeLikedSite(url)
        self.clearIcon(QPushButton, "favSiteBtn")
        self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE,
                            lambda: self.favouritePage(self.currentWebpage))

    def onUrlChanged(self, url):
        if (url.toString() != "https://www.google.com/"):
            self.searchHistory.Set_1.add(url.toString())
        changedDomain = getDomainName(url.toString().lower())
        self.currentWebpage = url
        if not self.previousWebpages or self.previousWebpages[-1] != url:
            self.previousWebpages.append(url)

        if len(self.previousWebpages) > 1:
            self.previousPageBtn.setEnabled(True)

        if not self.manualSearch:
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
            self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_FILL_IMG, self.TOOLBAR_ICON_SIZE,
                                lambda: self.unfavouritePage(self.currentWebpage))
        else:
            self.findAndSetIcon(QPushButton, "favSiteBtn", self.HEART_NO_FILL_IMG, self.TOOLBAR_ICON_SIZE,
                                lambda: self.favouritePage(self.currentWebpage))

        self.manualSearch = False

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
            btn = QPushButton(textwrap.fill(q["question"], self.TEXT_WIDTH))
            times_text = "time" if q["uses"] == 1 else "times"
            btn.setToolTip(f"This question was asked {q['uses']} {times_text}.")
            btn.setStyleSheet(self.buttonStyle)
            btn.clicked.connect(partial(self.insertQuestion, q["question"]))
            self.FAQBtnLayout.addWidget(btn)

    def insertQuestion(self, question):
        self.queryInput.clear()
        self.queryInput.insertPlainText(question)

    def addInputText(self, text):
        print(text)
        self.queryInput.clear()
        self.queryInput.insertPlainText(text)
        if (self.AudioError or self.recordingNotStopped):
            print("Inside if")
            path = self.MICROPHONE_IMG
            self.microphoneBtn.setIcon(QIcon(path.__str__()))
            self.microphoneBtn.setIconSize(QSize(*self.MICROPHONE_SIZE))
            self.isRecording = not self.isRecording
            self.microphoneTimer.stop()
            # self.inputTimer.stop()
        self.AudioError = False
        self.recordingNotStopped = False

    def onMicroBtnClicked(self):
        if self.isRecording:
            path = self.MICROPHONE_IMG
            print("Stop Recording")
            self.microphoneTimer.stop()
            # self.inputTimer.stop()
            # self.queryInput.setPlaceholderText(self.PLACEHOLDER_TEXT)
        else:
            path = self.STOP_IMG
            self.microphoneTimer.start(self.MICROPHONE_TIME_DELAY)
            # self.inputTimer.start(self.INPUT_TIME_DELAY)
            # self.queryInput.setPlaceholderText("Recording")
            print("Start Recording")

        self.microphoneBtn.setIcon(QIcon(path.__str__()))
        self.microphoneBtn.setIconSize(QSize(*self.MICROPHONE_SIZE))
        self.isRecording = not self.isRecording

        if self.isRecording:
            print("yeah")
            threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        self.recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_text_signal.emit("Recording audio...")
            if self.isRecording:
                try:
                    print("Starting voice recognition...")
                    audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    print("Recognizer stopped listening...")
                    self.update_text_signal.emit("Converting audio to text...")
                    text = self.recognizer.recognize_google(audio_data)
                    print("Google translation is done...")
                    if self.isRecording:
                        self.recordingNotStopped = True
                    self.update_text_signal.emit(text)
                except sr.UnknownValueError:
                    self.AudioError = True
                    self.update_text_signal.emit("Could not understand the audio. Please try again.")
                    # break
                except sr.RequestError as e:
                    self.update_text_signal.emit("Could not request results. Please try again.")
                    self.onMicroBtnClicked()
                except sr.WaitTimeoutError:
                    pass

    def onHomeBtnClicked(self):
        self.pages.setCurrentWidget(self.homePage)
        print("Home button clicked")
        self.webView.load(self.HOME_PAGE)

    def onSettingsBtnClicked(self):
        self.pages.setCurrentWidget(self.settingsPage)
        print("Settings button clicked")

    def onActionLogBtnClicked(self):
        self.pages.setCurrentWidget(self.activityLogPage)
        print("Action Log button clicked")
        print(self.searchHistory.Set_1)
        print(self.searchHistory.Set_2)
        print(self.searchHistory.Set_3)
        self.searchHistory.displayVisited(self)


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

    def runAIRequest(self, inputText):
        result = self.aiAssistant.singleRequest(inputText)
        self.update_result.emit(result)  # Emit signal with the result

        question = self.aiAssistant.validateQuestion(inputText, self.currentWebpage)
        if question:
            print("Question formatted: " + question)
            self.database.addFAQ(question, self.domain)

    def enterQuery(self):
        if self.isRecording:
            self.onMicroBtnClicked()
        inputText = self.queryInput.toPlainText()

        if inputText.replace("\n", ""):
            self.webView.grab().save(self.screenshotPath, b'JPEG')
            self.queryInput.setEnabled(False)
            self.enterBtn.setEnabled(False)
            self.enterBtn.setText("The AI is thinking" + "." * self.currentNoDots)
            self.thinkingTimer.start(self.MICROPHONE_TIME_DELAY)
            thread = threading.Thread(target=self.runAIRequest, args=(inputText,))
            thread.start()
            # Connect the signal to the slot for updating the UI
            self.update_result.connect(self.showText)
        else:
            self.queryInput.insertPlainText("\n")

    @pyqtSlot(str)
    def showText(self, text):
        self.showRating(True)
        self.deleteSpacer(1)
        self.backBtn.show()
        self.queryInput.setEnabled(True)
        self.enterBtn.setEnabled(True)
        self.enterBtn.setText("ASK QUESTION")
        self.thinkingTimer.stop()

        self.clearLayout(self.FAQBtnLayout)
        self.FAQLabel.hide()
        textEdit = QTextEdit()
        textEdit.moveCursor(textEdit.textCursor().Start)
        textEdit.setReadOnly(True)

        font = textEdit.font()
        font.setPointSize(self.FONT_SIZE)
        textEdit.setFont(font)

        self.FAQBtnLayout.addWidget(textEdit)
        if self.TEXT_DELAY_MS == 0:
            textEdit.setHtml(formatHtml(text))
        else:
            self.slowlyTypeText(textEdit, text)

    def slowlyTypeText(self, textEdit, text):
        index = 0

        def insertCharacter():
            nonlocal index
            if index < len(text):
                textEdit.insertPlainText(text[index])
                print(text[index])
                index += 1
            else:
                timer.stop()

        timer = QTimer()
        timer.timeout.connect(insertCharacter)
        timer.start(self.TEXT_DELAY_MS)

    def closeEvent(self, event):
        self.favourites.writeFavourites()
