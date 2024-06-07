import pickle
import urllib
from PyQt5.QtWidgets import QPushButton
from collections import OrderedDict
from itertools import islice
from functools import partial
import os

class SearchHistory:
    VISITED_TODAY = "visitedtoday.txt"
    VISITED_YESTERDAY = "visitedyesterday.txt"
    VISITED_DAYSAGO = "visiteddaysago.txt"

    todaySet = set()
    yesterdaySet = set()
    daysagoSet = set()

    todayShift = 0
    yesterdayShift = 0
    daysagoShift = 0

    VISITED_SIZE = 6 
    FAVICON_SIZE = 64
    
    def __init__(self):
        try:
            with open(self.VISITED_TODAY, 'rb') as file:
                self.todaySet = pickle.load(file)
            with open(self.VISITED_YESTERDAY, 'rb') as file:
                self.yesterdaySet = pickle.load(file)
            with open(self.VISITED_DAYSAGO, 'rb') as file:
                self.daysagoSet = pickle.load(file)
        except (EOFError, FileNotFoundError):
            pass
    
                
    def addVisitedSite(self, site):
        self.todaySet.add(site.toString())
        
    def removeVisitedSite(self, site):
        self.todaySet.remove(site.toString())
        
    def writeVisited(self):
        with open(self.VISITED_TODAY, 'wb') as file:
            pickle.dump(self.todaySet, file)
                
        with open(self.VISITED_YESTERDAY, 'wb') as file:
            pickle.dump(self.yesterdaySet, file)
        
        with open(self.VISITED_DAYSAGO, 'wb') as file:
            pickle.dump(self.daysagoSet, file)

    def displayVisited(self, browser):
        self.clearVisited(browser)
        self.displayToday(browser)
        #self.displayYesterday(browser)
        #self.displayDaysAgo(browser)
            
    def displayToday(self, browser):
        base = self.todayShift * self.VISITED_SIZE
        i = 1
        print(self.todaySet)
        print(list(self.todaySet)[base:base + self.VISITED_SIZE])
        for item in list(self.todaySet)[base:base + self.VISITED_SIZE]:
            url = item
            domain = url.removeprefix("https://").split('/', 1)[0]
            path = f"assets/favicons/{domain}.png"

            if not os.path.exists(path):
                faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
                urllib.request.urlretrieve(faviconUrl, path)
            
            button = browser.findAndSetIcon(QPushButton, f"visited_{i}", path, (90,90), partial(browser.gotoURL, url))
            if domain.startswith("www."): domain = domain[4:]
            text = f"<b><span style='font-family: Arial; font-size: 60px;'>{domain}</span></b><br>" \
                f"<span style='font-family: Arial; font-size: 30px;'>{url}</span>"
            button.setToolTip(text)
            
            i = i + 1
        
    def clearVisited(self, browser):
        for i in range (1,18):
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            

            
    def clickVisitedRightArrow(self, browser):
        if self.likedRightShift == 0: browser.likedLeftArrow.show()
        self.likedRightShift += 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"liked{i}")
        self.displayLiked(browser)
    
    def clickVisitedRightArrow_2(self, browser):
        if self.likedRightShift == 1: browser.likedLeftArrow.hide()
        self.likedRightShift -= 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"liked{i}")
        self.displayLiked(browser)
    
    def clickVisitedRightArrow_3(self, browser):
        if self.mostUsedRightShift == 0: browser.mostUsedLeftArrow.show()
        self.mostUsedRightShift += 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"mostVisited{i}")
        self.displayMostUsed(browser)
    
    def clickVisitedLeftArrow(self, browser):
        if self.mostUsedRightShift == 1: browser.mostUsedLeftArrow.hide()
        self.mostUsedRightShift -= 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"mostVisited{i}")
        self.displayMostUsed(browser)
    
    def clickVisitedLeftArrow_2(self, browser):
        if self.mostUsedRightShift == 1: browser.mostUsedLeftArrow.hide()
        self.mostUsedRightShift -= 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"mostVisited{i}")
        self.displayMostUsed(browser)

    def clickVisitedLeftArrow_3(self, browser):
        if self.mostUsedRightShift == 1: browser.mostUsedLeftArrow.hide()
        self.mostUsedRightShift -= 1
        for i in range (1,13): browser.clearIcon(QPushButton, f"mostVisited{i}")
        self.displayMostUsed(browser)