import pickle
import urllib
from PyQt5.QtWidgets import QPushButton
from collections import OrderedDict
from itertools import islice
from functools import partial
import os

class Favourites:
    LIKED_FILENAME = "likedsites.txt"
    MOST_USED_FILENAME = "mostusedsites.txt"
    likedSet = set()
    mostUsedMap = dict()
    likedRightShift = 0
    mostUsedRightShift = 0
    FAVICON_SIZE = 128
    
    def __init__(self):
        try:
            with open(self.LIKED_FILENAME, 'rb') as file:
                self.likedSet = pickle.load(file)
            with open(self.MOST_USED_FILENAME, 'rb') as file:
                self.mostUsedMap = pickle.load(file)
        except (EOFError, FileNotFoundError):
            pass
    
    def isLikedSite(self, site):
        return site.toString() in self.likedSet
                
    def addLikedSite(self, site):
        self.likedSet.add(site.toString())
        
    def removeLikedSite(self, site):
        self.likedSet.remove(site.toString())
        
    def incrementSiteUses(self, site):
        if not site.toString().removeprefix("https://").split('/', 1)[0][:len("www.google.")] == "www.google.":
            self.mostUsedMap[site.toString()] = self.mostUsedMap.get(site.toString(), 0) + 1
        
    def writeFavourites(self):
        with open(self.LIKED_FILENAME, 'wb') as file:
            pickle.dump(self.likedSet, file)
                
        with open(self.MOST_USED_FILENAME, 'wb') as file:
            pickle.dump(self.mostUsedMap, file)

    def displayFavourites(self, browser):
        self.clearFavourites(browser)
        self.displayLiked(browser)
        self.displayMostUsed(browser)
            
    def displayLiked(self, browser):
        base = 2*self.likedRightShift
        i = 1
        buttonSize = browser.findChild(QPushButton, f"liked{i}").size()
        size = (buttonSize.width() - 20, buttonSize.height() - 20)
        for item in list(self.likedSet)[base:base + 12]:
            url = item
            domain = url.removeprefix("https://").split('/', 1)[0]
            path1 = f"assets/favicons"

            if not os.path.exists(path1):
                os.makedirs(path1)
            
            faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
            urllib.request.urlretrieve(faviconUrl, f"assets/favicons/{domain}.png")
            
            button = browser.findAndSetIcon(QPushButton, f"liked{i}", f"assets/favicons/{domain}.png", size, partial(browser.favouritedSiteClicked, url))
            if domain.startswith("www."): domain = domain[4:]
            text = f"<b><span style='font-family: Arial; font-size: 60px;'>{domain}</span></b><br>" \
                f"<span style='font-family: Arial; font-size: 30px;'>{url}</span>"
            button.setToolTip(text)
            
            i = i + 1
        
    def displayMostUsed(self, browser):
        base = 2*self.mostUsedRightShift
        i = 1
        self.mostUsedMap = OrderedDict(sorted(self.mostUsedMap.items(), key=lambda item: item[1], reverse=True))
        buttonSize = browser.findChild(QPushButton, f"mostVisited{i}").size()
        size = (buttonSize.width() - 20, buttonSize.height() - 20)
        for key, value in islice(self.mostUsedMap.items(), base, base + 12):
            url = key
            domain = url.removeprefix("https://").split('/', 1)[0]
            path1 = f"assets/favicons"
            
            if not os.path.exists(path1):
                os.makedirs(path1)

            faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
            urllib.request.urlretrieve(faviconUrl, f"assets/favicons/{domain}.png")
        
            button = browser.findAndSetIcon(QPushButton, f"mostVisited{i}", f"assets/favicons/{domain}.png", size, partial(browser.mostUsedSiteClicked, url))
            if domain.startswith("www."): domain = domain[4:]
            text = f"<b><span style='font-family: Arial; font-size: 60px;'>{domain}</span></b><br>" \
                f"<span style='font-family: Arial; font-size: 30px;'>{url}</span>"
            button.setToolTip(text)

            i = i + 1
        
    def clearFavourites(self, browser):
        for i in range (1,13):
            browser.clearIcon(QPushButton, f"liked{i}")
            browser.findChild(QPushButton, f"liked{i}").setToolTip(None)            
            browser.clearIcon(QPushButton, f"mostVisited{i}")
            browser.findChild(QPushButton, f"mostVisited{i}").setToolTip(None)
            
    def clickLikedRightArrow(self, browser):
        if self.likedRightShift == 0: browser.likedLeftArrow.show()
        self.likedRightShift += 1
        for i in range (1,13): 
            browser.clearIcon(QPushButton, f"liked{i}")
            browser.findChild(QPushButton, f"liked{i}").setToolTip(None)            
        self.displayLiked(browser)
    
    def clickLikedLeftArrow(self, browser):
        if self.likedRightShift == 1: browser.likedLeftArrow.hide()
        self.likedRightShift -= 1
        for i in range (1,13): 
            browser.clearIcon(QPushButton, f"liked{i}")
            browser.findChild(QPushButton, f"liked{i}").setToolTip(None)            
        self.displayLiked(browser)
    
    def clickMostUsedRightArrow(self, browser):
        if self.mostUsedRightShift == 0: browser.mostUsedLeftArrow.show()
        self.mostUsedRightShift += 1
        for i in range (1,13): 
            browser.clearIcon(QPushButton, f"mostVisited{i}")
            browser.findChild(QPushButton, f"mostVisited{i}").setToolTip(None)            
        self.displayMostUsed(browser)
    
    def clickMostUsedLeftArrow(self, browser):
        if self.mostUsedRightShift == 1: browser.mostUsedLeftArrow.hide()
        self.mostUsedRightShift -= 1
        for i in range (1,13): 
            browser.clearIcon(QPushButton, f"mostVisited{i}")
            browser.findChild(QPushButton, f"mostVisited{i}").setToolTip(None)            
        self.displayMostUsed(browser)
    
    