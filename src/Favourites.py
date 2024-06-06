import pickle
import urllib
from PyQt5.QtWidgets import QPushButton
from collections import OrderedDict
from itertools import islice
from functools import partial

class Favourites:
    LIKED_FILENAME = "likedsites.txt"
    MOST_USED_FILENAME = "mostusedsites.txt"
    likedSet = set()
    mostUsedMap = dict()
    likedRightShift = 0
    mostUsedRightShift = 0
    FAVICON_SIZE = 64
    
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
        print(site.toString())
        self.mostUsedMap[site.toString()] = self.mostUsedMap.get(site.toString(), 0) + 1
        print(self.mostUsedMap[site.toString()])
        
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
        print(self.likedSet)
        print(list(self.likedSet)[base:base + 12])
        for item in list(self.likedSet)[base:base + 12]:
            url = item
            domain = url.removeprefix("https://").split('/', 1)[0]
            faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
            location = f"assets/favicons/{domain}.png"
            urllib.request.urlretrieve(faviconUrl, location)
            browser.findAndSetIcon(QPushButton, f"liked{i}", location, (90,90), partial(browser.gotoURL, url))
            i = i + 1
        
    def displayMostUsed(self, browser):
        base = 2*self.mostUsedRightShift
        i = 1
        self.mostUsedMap = OrderedDict(sorted(self.mostUsedMap.items(), key=lambda item: item[1], reverse=True))
        for key, value in islice(self.mostUsedMap.items(), base, base + 12):
            url = key
            domain = url.removeprefix("https://").split('/', 1)[0]
            faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
            location = f"assets/favicons/{domain}.png"
            urllib.request.urlretrieve(faviconUrl, location)
            browser.findAndSetIcon(QPushButton, f"mostVisited{i}", location, (90,90), partial(browser.gotoURL, url))
            i = i + 1
        
    def clearFavourites(self, browser):
        for i in range (1,13):
            browser.clearIcon(QPushButton, f"liked{i}")
            browser.clearIcon(QPushButton, f"mostVisited{i}")