from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class WebWidget(QWebEngineView):
    def createWindow(self, _type):
        new_webview = QWebEngineView()
        new_page = WebEnginePage(new_webview)
        new_page.urlChanged.connect(self.handleNewWindowUrlChange)
        new_webview.setPage(new_page)
        return new_webview

    def handleNewWindowUrlChange(self, url):
        self.setUrl(url)


class WebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent