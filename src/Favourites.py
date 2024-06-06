import pickle
import urllib
from PyQt5.QtWidgets import QPushButton
from collections import OrderedDict
from itertools import islice
from functools import partial

class Favourites:
    LIKED_FILENAME = "likedsites.txt"
    MOST_USED_FILENAME = "mostusedsites.txt"
    likedSet = {}
    mostUsedMap = {}
    likedRightShift = 0
    mostUsedRightShift = 0
    FAVICON_SIZE = 64
    
    def __init__(self):
        try:
            with open(self.LIKED_FILENAME, 'rb') as file:
                self.likedSet = pickle.load(file)
            with open(self.MOST_USED_FILENAME, 'rb') as file:
                tempMap = pickle.load(file)
                self.mostUsedMap = OrderedDict(sorted(tempMap.items(), key=lambda item: item[1]))
        except (EOFError, FileNotFoundError):
            pass
                
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
        base = 2*self.likedRightShift
        i = 1
        for key, value in islice(self.mostUsedMap.items(), base, base + 12):
            url = key
            domain = url.removeprefix("https://").split('/', 1)[0]
            faviconUrl = f"https://www.google.com/s2/favicons?domain={domain}&sz={self.FAVICON_SIZE}"
            location = f"assets/favicons/{domain}.png"
            urllib.request.urlretrieve(faviconUrl, location)
            print(url)
            browser.findAndSetIcon(QPushButton, f"liked{i}", location, (90,90), partial(browser.gotoURL, url))
            i = i + 1
            
        