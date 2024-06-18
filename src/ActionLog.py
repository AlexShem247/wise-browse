from enum import Enum
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QSizePolicy

class ActionLogType(Enum):
    ACTION = 1
    SITE = 2

class ActionLog:
    actionLogList = []
    base = 0


    def addAction(self, actionText):
        print("ACTION: " + actionText)
        self.actionLogList.append((ActionLogType.ACTION, actionText))
    
    def addSite(self, siteText):
        print("SITE  : " + siteText)
        self.actionLogList.append((ActionLogType.SITE, siteText))
        
    def displayActionLog(self, webBrowser):
        if ((self.base + 11) >= len(self.actionLogList)): 
            webBrowser.downArrow.hide()
        else:
            webBrowser.downArrow.show()

        if (self.base > 0): 
            webBrowser.upArrow.show()
        else:
            webBrowser.upArrow.hide()

        i = 1
        for item in list(self.actionLogList)[self.base:self.base + 11]:
            print(i)
            layout = webBrowser.findChild(QHBoxLayout, f"layout{i}")
            webBrowser.clearLayout(layout)
            
            actionLogEntry = item
            type = actionLogEntry[0]
            text = actionLogEntry[1]
            sizePolicy = QSizePolicy()
            sizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)
            sizePolicy.setVerticalPolicy(QSizePolicy.Expanding)
            if (type == ActionLogType.ACTION):
                label = QLabel(text)
                label.setStyleSheet("""
                    background-color: rgb(215, 215, 215);
                    border-radius: 20px; 
                    font-size: 20px;   
                    font-weight: bold;
                    font-family: sans-serif;
                    padding: 10px; 
                """)
                label.setSizePolicy(sizePolicy)
                layout.addWidget(label)
            else:
                button = QPushButton(text)
                button.setStyleSheet("""
                    QPushButton {
                        border: solid;
                        border-radius: 20px; 
                        background-color: rgb(165, 165, 165);
                        font-size: 20px;   
                        font-weight: bold;
                        font-family: sans-serif;
                    }

                    QPushButton:hover {
                        background-color: rgb(120, 120, 120);
                    }
                """)
                button.setSizePolicy(sizePolicy)
                if text[:8] == "https://":
                    button.clicked.connect(lambda: webBrowser.actionLogSiteClicked(text))
                layout.addWidget(button)
                
            i = i + 1
            
    
    def headIsSite(self):
        return self.actionLogList[0][0] == ActionLogType.SITE
    
    def clickedPrevious(self, browser):
        self.base -= 1
        if (self.base == 0): 
            browser.upArrow.hide()
        #for i in range (self.VISITED_SIZE + 1, self.VISITED_SIZE * 2 + 1): 
            #browser.clearIcon(QPushButton, f"visited_{i}")
           # browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displayActionLog(browser)

    def clickedNext(self, browser):
        self.base += 1
        if (self.base + 11 >= len(self.actionLogList)): 
            browser.upArrow.hide()
        #for i in range (self.VISITED_SIZE + 1, self.VISITED_SIZE * 2 + 1): 
            #browser.clearIcon(QPushButton, f"visited_{i}")
           # browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displayActionLog(browser)