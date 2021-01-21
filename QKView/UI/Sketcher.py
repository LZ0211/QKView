from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGridLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from ..Core import API

JS_loadCanvas2D = '''mol = `%s`
function wait(){
    if(typeof(loadCanvas2D) !== 'function') return setTimeout(wait,100)
    loadCanvas2D(mol)
}
setTimeout(wait,100)'''

JS_getCurrentMol = '''
function getCurrentMol(){
    return [toMOL(),getImage()]
}
getCurrentMol()'''

JS_clearMol = '''
try{
    sketcher.toolbarManager.buttonClear.getElement().click()
}catch(e){
}
'''

class Sketcher(QWidget):
    confirmed = pyqtSignal(str, str, name='confirmed')
    def __init__(self,parent=None):
        super(Sketcher, self).__init__()
        self.isReady = False
        self.parent = parent
        self.renderWindow()
        self.bindConfirmEvent()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def ready(self):
        self.isReady = True

    def renderWindow(self):
        self.setGeometry(20, 20, 460, 440)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)
        self.setFixedSize(460, 440)
        #self.setFixedSize(430, 440)
        #标题
        self.setWindowTitle('Sketcher')
        self.setWindowIcon(QIcon(QPixmap('resource/benzene.png')))
        #布局
        layout = QGridLayout()
        self.setLayout(layout)
        self.webView = QWebEngineView()
        #self.webView.setFixedSize(400,400)
        self.webView.load(QUrl(API.SketcherURL))
        self.webView.show()
        self.webView.loadFinished.connect(self.ready)

        self.confirm = QPushButton(self.tr('Save'))
        layout.addWidget(self.webView, 0, 0, 3, 3)
        layout.addWidget(self.confirm, 3, 2, 1, 1)

    def loadMolecule(self,mol):
        if self.isReady:
            self.execute(JS_loadCanvas2D % mol,self.noop)
        def run():
            self.execute(JS_loadCanvas2D % mol,self.noop)
            self.webView.loadFinished.disconnect(run)
        self.webView.loadFinished.connect(run)
        self.show()

    def bindConfirmEvent(self):
        def updateMol(arr):
            self.confirmed.emit(*arr)
            self.close()
            self.setEnabled(True)
        def confirmEvent():
            self.setDisabled(True)
            self.execute(JS_getCurrentMol,updateMol)
        self.confirm.clicked.connect(confirmEvent)

    def execute(self,cmd,cb):
        self.webView.page().runJavaScript(cmd,cb)

    def once(self,fn):
        def func(*argv):
            fn(*argv)
            self.confirmed.disconnect(func)
            self.execute(JS_clearMol,self.noop)
        self.confirmed.connect(func)

    def noop(self,*argv):
        pass

    def closeEvent(self, event):
        if self.parent:
            self.parent.setEnabled(True)
        event.accept()

    def showEvent(self,event):
        if self.parent:
            self.parent.setDisabled(True)
        event.accept()

    def tr(self,text):
        if self.parent:
            return self.parent.tr(text)
        return text