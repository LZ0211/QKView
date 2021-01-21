from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class Browser(QMainWindow):
    def __init__(self,parent=None):
        super(Browser, self).__init__()
        self.parent = parent
        self.setGeometry(5,30,1080,680)
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

    def open(self,uri):
        self.browser.load(QUrl(uri))
        self.show()
        pass

    def closeEvent(self, event):
        if self.parent:
            self.parent.setEnabled(True)
        event.accept()

    def showEvent(self,event):
        if self.parent:
            self.parent.setDisabled(True)
        event.accept()