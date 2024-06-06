import pickle

class Favourites:
    LIKED_FILENAME = "likedsites.txt"
    MOST_USED_FILENAME = "mostusedsites.txt"
    likedSet = {}
    mostUsedMap = {}
    
    def __init__(self):
        try:
            with open(self.LIKED_FILENAME, 'rb') as file:
                self.likedSet = pickle.load(file)
            with open(self.MOST_USED_FILENAME, 'rb') as file:
                self.mostUsedMap = pickle.load(file)
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
            
        