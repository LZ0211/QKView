from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGridLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from ..Core import API

class Editor(QWidget):
    finished = pyqtSignal(str, str, str, name='finished')
    
    def __init__(self,parent=None):
        super(Editor, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(20, 20, 400, 800)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)

        #标题
        self.setWindowTitle(self.translate('New Molecule'))
        self.setWindowIcon(QIcon(QPixmap('resource/benzene.png')))

        

    def noop(self,*argv):
        pass

    def closeEvent(self, QCloseEvent):
        if self.parent:
            self.parent.setEnabled(True)
        QCloseEvent.accept()

    def translate(self,text):
        if self.parent:
            return self.parent.translate(text)
        return text