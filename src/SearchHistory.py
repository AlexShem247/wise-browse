import pickle
import urllib
from PyQt5.QtWidgets import QPushButton
from collections import OrderedDict
from itertools import islice
from functools import partial
import os
import datetime

class SearchHistory:
    VISITED_1 = "visited_1.txt"
    VISITED_2 = "visited_2.txt"
    VISITED_3 = "visited_3.txt"

    Set_1 = set()
    Set_2 = set()
    Set_3 = set()

    Shift_1 = 0
    Shift_2 = 0
    Shift_3 = 0

    date_1 = ""
    date_2 = ""
    date_3 = ""

    VISITED_SIZE = 6 
    FAVICON_SIZE = 64
    
    def __init__(self):
        current_date = datetime.date.today()
        print(current_date)
        try:
            with open(self.VISITED_1, 'r') as file_1:
                first_line_1 = file_1.readline()
                print(first_line_1)
                rest_of_line_1 = file_1.readlines()
                file_1.close()
            with open(self.VISITED_2, 'r') as file_2:
                first_line_2 = file_2.readline()
                rest_of_line_2 = file_2.readlines()
                file_2.close()
            with open(self.VISITED_3, 'r') as file_3:
                first_line_3 = file_3.readline()
                rest_of_line_3 = file_3.readlines()
                file_3.close()
            
            if (first_line_1.strip() != str(current_date)):
                for line in rest_of_line_1:
                    self.Set_2.add(line)
                for line in rest_of_line_2:
                    self.Set_3.add(line)
                self.date_1 = str(current_date)
                self.date_2 = first_line_1
                print(self.date_1, current_date)
                self.date_3 = first_line_2

            else:
                for item in rest_of_line_1:
                    self.Set_1.add(item)
                for item in rest_of_line_2:
                    self.Set_2.add(item)
                for item in rest_of_line_3:
                    self.Set_3.add(item)
                self.date_1 = first_line_1
                self.date_2 = first_line_2
                self.date_3 = first_line_3
                
        except (EOFError, FileNotFoundError):
            pass

    
                
    def addVisitedSite(self, site):
        self.Set_1.add(site.toString())
        
    def removeVisitedSite(self, site):
        self.Set_1.remove(site.toString())
        
    def writeVisited(self):
        self.writeFile(self.VISITED_1, self.Set_1, self.date_1)
                
        self.writeFile(self.VISITED_2, self.Set_2, self.date_2)

        self.writeFile(self.VISITED_3, self.Set_3, self.date_3)

    def writeFile(file_name, set, date):
        with open(file_name, 'w') as file:
            file.write(date + '\n')
            for item in set:
                file.write(item + '\n')
        file.close()

    def displayVisited(self, browser):
        self.clearVisited(browser)
        self.setHistoryDates(browser)
        self.displaySet_1(browser)
        self.displaySet_2(browser)
        self.displaySet_3(browser)

    def setHistoryDates(self, browser):
        browser.historydate_1.setText(self.date_1)
        browser.historydate_2.setText(self.date_2)
        browser.historydate_3.setText(self.date_3)

            
    def displaySet_1(self, browser):
        if ((self.Shift_1 + 1) * self.VISITED_SIZE >= len(self.Set_1)): 
            browser.visitedRightArrow.hide()
        else:
            browser.visitedRightArrow.show()

        if (self.Shift_1 > 0):
            browser.visitedLeftArrow.show()
        else:
            browser.visitedLeftArrow.hide()

        base = self.Shift_1 * self.VISITED_SIZE
        i = 1
        
        for item in list(self.Set_1)[base:base + self.VISITED_SIZE]:
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

    def displaySet_2(self, browser):
        if ((self.Shift_2 + 1) * self.VISITED_SIZE >= len(self.Set_2)): 
            browser.visitedRightArrow_2.hide()
        else:
            browser.visitedRightArrow_2.show()

        if (self.Shift_2 > 0):
            browser.visitedLeftArrow_2.show()
        else:
            browser.visitedLeftArrow_2.hide()

        base = self.Shift_2 * self.VISITED_SIZE
        i = self.VISITED_SIZE + 1
    
        for item in list(self.Set_2)[base:base + self.VISITED_SIZE]:
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

    def displaySet_3(self, browser):
        if ((self.Shift_3 + 1) * self.VISITED_SIZE >= len(self.Set_3)): 
            browser.visitedRightArrow_3.hide()
        else:
            browser.visitedRightArrow_3.show()

        if (self.Shift_3 > 0):
            browser.visitedLeftArrow_3.show()
        else:
            browser.visitedLeftArrow_3.hide()

        base = self.Shift_3 * self.VISITED_SIZE
        i = self.VISITED_SIZE * 2 + 1
        for item in list(self.Set_3)[base:base + self.VISITED_SIZE]:
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
        self.Shift_1 += 1
        if ((self.Shift_1 + 1) * self.VISITED_SIZE < len(self.Set_1)): 
            browser.visitedRightArrow.show()
        for i in range (1, self.VISITED_SIZE): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_1(browser)
    
    def clickVisitedRightArrow_2(self, browser):
        self.Shift_2 += 1
        if ((self.Shift_2 + 1) * self.VISITED_SIZE < len(self.Set_2)): 
            browser.visitedRightArrow_2.show()
        for i in range (self.VISITED_SIZE + 1, self.VISITED_SIZE * 2 + 1): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_2(browser)
    
    def clickVisitedRightArrow_3(self, browser):
        self.Shift_3 += 1
        if ((self.Shift_3 + 1) * self.VISITED_SIZE < len(self.Set_3)): 
            browser.visitedRightArrow_3.show()
        for i in range (self.VISITED_SIZE * 2 + 1, self.VISITED_SIZE * 3 + 1): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_3(browser)
    
    def clickVisitedLeftArrow(self, browser):
        self.Shift_1 -= 1
        if (self.Shift_1 == 0): 
            browser.visitedLeftArrow.hide()
        for i in range (1, self.VISITED_SIZE + 1): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_1(browser)
    
    def clickVisitedLeftArrow_2(self, browser):
        self.Shift_2 -= 1
        if (self.Shift_2 == 0): 
            browser.visitedLeftArrow_2.hide()
        for i in range (self.VISITED_SIZE + 1, self.VISITED_SIZE * 2 + 1): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_2(browser)

    def clickVisitedLeftArrow_3(self, browser):
        self.Shift_3 -= 1
        if (self.Shift_3 == 0): 
            browser.visitedLeftArrow_3.hide()
        for i in range (self.VISITED_SIZE + 2, self.VISITED_SIZE * 3 + 1): 
            browser.clearIcon(QPushButton, f"visited_{i}")
            browser.findChild(QPushButton, f"visited_{i}").setToolTip(None)            
        self.displaySet_3(browser)