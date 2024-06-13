from enum import Enum  

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
        
    def displayActionLog(self):
        for item in self.actionLogList:
            print(item)
    
    def headIsSite(self):
        return self.actionLogList[0][0] == ActionLogType.SITE