from enum import Enum
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QSizePolicy

class ActionLogType(Enum):
    ACTION = 1
    SITE = 2

class ActionLog:
    actionLogList = []

    def addAction(self, actionText):
        print("ACTION: " + actionText)
        self.actionLogList.insert(0, (ActionLogType.ACTION, actionText))
    
    def addSite(self, siteText):
        print("SITE  : " + siteText)
        self.actionLogList.insert(0, (ActionLogType.SITE, siteText))
        
    def displayActionLog(self, webBrowser):
        base = 0
        i = 1
        for item in list(self.actionLogList)[base:base + 11]:
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