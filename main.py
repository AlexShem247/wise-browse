import sys
from PyQt5.QtWidgets import QApplication

from src.WebBrowser import WebBrowser

if __name__ == "__main__":
    if "test" in sys.argv:
        print("Build verification only, skipping GUI initialisation")
    else:
        app = QApplication(sys.argv)
        window = WebBrowser()
        window.show()
        sys.exit(app.exec_())
