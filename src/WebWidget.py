import sys
import os
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl, QStandardPaths, Qt, QProcess


class WebWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.handle_download)

    def handle_download(self, download):
        downloads_path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        file_path = os.path.join(downloads_path, download.suggestedFileName())

        # Create a progress dialog
        progress_dialog = QProgressDialog(f"Downloading {download.suggestedFileName()}...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Downloading")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        progress_dialog.show()

        # Update progress dialog as the download progresses
        download.downloadProgress.connect(lambda received, total: progress_dialog.setValue(int(received / total * 100)))
        download.finished.connect(lambda: progress_dialog.close())
        download.finished.connect(lambda: self.open_file(file_path))

        # Handle cancel action from progress dialog
        progress_dialog.canceled.connect(download.cancel)

        download.setPath(file_path)
        download.accept()

    def open_file(self, file_path):
        if platform.system() == 'Darwin':  # macOS
            QProcess.startDetached('open', [file_path])
        elif platform.system() == 'Windows':  # Windows
            os.startfile(file_path)
        else:  # Linux
            QProcess.startDetached('xdg-open', [file_path])

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
