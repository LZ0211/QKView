from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFormLayout, QPushButton, QDialogButtonBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from ..Core import API
import time,requests

JS_forbidden = '''trigger = $.prototype.trigger;
$.prototype.trigger = function(name){
    if(name == 'contextmenu') return
    trigger.call(this,name)
}
var _ = function(name){return document.querySelector(name) || {}}
try{
    _('#structure-search').style = "display:none";
    //_('.scale-value-wrap').style = "display:none";
    _('a[data-name="showLogo"]').style = "display:none";
    _('a[data-name="feedbackNew"]').style = "display:none";
    _('#action-mp-topbottom').style = "display:none";
    _('#action-mp-center').style = "display:none";
    _('#action-mp-acs').style = "display:none";
    _('#action-mp-nmr').style = "display:none";
    _('#action-mp-textSearch').style = "display:none";
    //_('#action-mp-zoomIn').style = "display:none";
    //_('#action-mp-zoomOut').style = "display:none";
    _('#action-mp-hint').style = "display:none";
    _('#action-mp-tlc').style = "display:none";
    _('#action-mp-svgtemplate-56').style = "display:none";
    //_('#action-mp-savefullpic').style = "display:none";
}catch(e){}
'''

JS_getImage = '''
function getImage(){
    molpad.savefullpic()
    return document.querySelector('.modalbox-body img').src
}
getImage()
'''

JS_loadCanvas2D = 'molpad.loadMOL(`%s`)'

JS_loadSMILES = '''
molpad.mol.loadSMILES(`%s`)
'''

JS_getCurrentMol = '''
function getImage(){
    molpad.savefullpic()
    return document.querySelector('.modalbox-body img').src
}
function getCurrentMol(){
    return [molpad.mol.getMOL(),getImage()]
}
getCurrentMol()'''

JS_clearMol = '''molpad.clear()
document.querySelector('.modalbox-body a').click()
'''

class Indraw(QWidget):
    confirmed = pyqtSignal(str, str, name='confirmed')
    def __init__(self,parent=None):
        super(Indraw, self).__init__()
        self.isReady = False
        self.parent = parent
        self.renderWindow()
        self.bindConfirmEvent()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def ready(self):
        self.isReady = True

    def renderWindow(self):
        self.setGeometry(20, 20, 680, 480)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)
        self.setFixedSize(680, 480)
        #标题
        self.setWindowTitle('Sketcher')
        self.setWindowIcon(QIcon(QPixmap('resource/benzene.png')))
        #布局
        layout = QFormLayout()
        self.setLayout(layout)
        self.webView = QWebEngineView()
        #self.webView.setFixedSize(400,400)
        #self.webView.settings().setDefaultTextEncoding("iso-8859-1")
        self.webView.setHtml(requests.get(API.IndrawURL).text,QUrl("http://indrawforweb.integle.com/indraw_inline/"))
        #self.webView.load(QUrl(API.IndrawURL+"?"+str(time.time())))
        self.webView.show()
        self.webView.loadFinished.connect(lambda:self.execute(JS_forbidden))
        self.webView.loadFinished.connect(self.ready)

        self.confirm = QPushButton(self.tr('Save'))
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal,self)
        layout.addRow(self.webView)
        layout.addRow(self.buttonBox)

    def loadMolecule(self,mol):
        if self.isReady:
            self.execute(JS_loadCanvas2D % mol)
        def run():
            self.execute(JS_loadCanvas2D % mol)
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
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(confirmEvent)

    def execute(self,cmd,cb=None):
        if cb == None:
            cb = self.noop
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