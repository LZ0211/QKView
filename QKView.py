import os,sys
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QGridLayout, QGroupBox, QPushButton, QSplashScreen, QToolBar, QMainWindow, QSystemTrayIcon, QStatusBar, QToolBar, QMenuBar, QMenu, QAction,QStyleFactory,QFileDialog,QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, QSize, Qt, QSettings
from PyQt5.QtGui import QIcon, QColor, QPixmap
from libs.UI import Sketcher, Editor
from libs.Core import API
import json

class QKView(QMainWindow):
    def __init__(self,dirname):
        splash = QSplashScreen(QPixmap("resource/init.png"))
        splash.show()
        super(QKView, self).__init__()
        self.settings = QSettings(os.path.join(dirname,"setting.ini"),QSettings.IniFormat)
        self.languages = API.getLanguages(dirname)
        self.renderWindow()
        self.translateUI()
        self.show()
        self.editor = Editor(self)
        self.editor.show()
        #self.sketcher = Sketcher(self)
        #self.sketcher.once(lambda x,y,z:open('test.png','wb+').write(API.base64ToImage(z)))
        #self.sketcher.loadMolecule(API.smi2mol2D('c1ccccc1'))

    def renderWindow(self):
        self.setGeometry(20, 20, 900, 600)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)
        #标题
        self.setWindowTitle('Quantum Chemistry Viewer')
        self.setWindowIcon(QIcon(QPixmap('resource/icon.png')))
        #系统托盘
        self.tray = QSystemTrayIcon()  
        self.tray.setIcon(QIcon('resource/icon.png'))
        self.tray.show()
        #导航栏
        self.navigation = QToolBar('Navigation')
        self.navigation.setIconSize(QSize(16, 16))
        self.addToolBar(self.navigation)
        #菜单栏
        self.menuBar = QMenuBar()
        self.setMenuBar(self.menuBar)
        self.menuFile = QMenu("&File")
        self.menuEdit = QMenu("&Edit")
        self.menuData = QMenu("&Data")
        self.menuView = QMenu("&View")
        self.menuTool = QMenu("&Tool")
        self.menuLang = QMenu("&Language")
        self.menuTheme = QMenu("&Theme")
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)
        self.menuBar.addMenu(self.menuData)
        self.menuBar.addMenu(self.menuView)
        self.menuBar.addMenu(self.menuTool)
        self.menuBar.addMenu(self.menuLang)
        self.menuBar.addMenu(self.menuTheme)
        self.addFileActions()
        self.addEditActions()
        self.addDataActions()
        self.addViewActions()
        self.addToolActions()
        self.addLangActions()
        self.addThemeActions()
        
        #状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        #工具栏
        self.toolBar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.addSeparator()
        #布局
        self.centralWidget = QWidget()
        layout = QGridLayout()
        self.centralWidget.setLayout(layout)

    def addFileActions(self):
        self.actionAddImport = QAction()
        self.actionAddImport.setIcon(QIcon('resource/import.png'))
        self.actionAddDraw = QAction()
        self.actionAddDraw.setIcon(QIcon('resource/mol.png'))
        self.actionFilePref = QAction()
        self.actionFilePref.setIcon(QIcon('resource/setting.png'))
        self.actionFileExit = QAction()
        self.actionFileExit.setIcon(QIcon('resource/exit.png'))
        self.actionAddDraw.setIcon(QIcon('resource/mol.png'))
        self.menuAdd = QMenu('&Open',self)
        self.menuAdd.setIcon(QIcon('resource/Add.png'))
        #self.menuAdd.setShortcut('Ctrl+Q')
        self.menuAdd.addActions([self.actionAddImport,self.actionAddDraw])
        self.menuFile.addMenu(self.menuAdd)
        self.menuFile.addActions([self.actionFilePref,self.actionFileExit])
        #事件槽
        self.actionAddImport.triggered.connect(lambda :self.importDataFile(print))
        self.actionFileExit.triggered.connect(self.close)
        #self.actionFileExit.setStatusTip('Exit application')

    def addEditActions(self):
        self.actionEditCopy = QAction()
        self.actionEditPaste = QAction()
        self.actionEditDelete = QAction()
        self.menuEdit.addActions([
            self.actionEditCopy,
            self.actionEditPaste,
            self.actionEditDelete
        ])

    def addDataActions(self):
        self.actionDataSource = QAction()
        self.menuData.addAction(self.actionDataSource)

    def addViewActions(self):
        self.actionView2D = QAction()
        self.actionView3D = QAction()
        self.actionRenderWithGV = QAction('GaussView')
        self.actionRenderWithVESTA = QAction('VESTA')
        self.actionRenderWithVMD = QAction('VMD')
        self.menuRenderWith = QMenu()
        self.menuRenderWith.addActions([
            self.actionRenderWithGV,
            self.actionRenderWithVESTA,
            self.actionRenderWithVMD
        ])
        self.menuView.addMenu(self.menuRenderWith)
        self.menuView.addAction(self.actionView2D)
        self.menuView.addAction(self.actionView3D)

    def addToolActions(self):
        self.actionConvertPDB2XYZ = QAction('pdb2xyz')
        self.actionConvertPDB2MOL = QAction('pdb2mol')
        self.actionConvertMOL2XYZ = QAction('mol2xyz')
        self.actionConvertMOL2PDB = QAction('mol2Pdb')
        self.actionConvertXYZ2MOL = QAction('xyz2mol')
        self.actionConvertXYZ2DPB = QAction('xyz2pdb')
        self.actionOpenWithGaussian = QAction('Gaussian')
        self.actionOpenWithORCA = QAction('ORCA')
        self.actionOpenWithMultiwfn = QAction('Multiwfn')
        self.menuConvert = QMenu()
        self.menuOpenWith = QMenu()
        self.menuConvert.addActions([
            self.actionConvertPDB2XYZ,
            self.actionConvertPDB2MOL,
            self.actionConvertMOL2XYZ,
            self.actionConvertMOL2PDB,
            self.actionConvertXYZ2MOL,
            self.actionConvertXYZ2DPB
        ])
        self.menuOpenWith.addActions([
            self.actionOpenWithGaussian,
            self.actionOpenWithORCA,
            self.actionOpenWithMultiwfn
        ])
        self.menuTool.addMenu(self.menuConvert)
        self.menuTool.addMenu(self.menuOpenWith)

    def addLangActions(self):
        def changeLang(lang):
            def func():
                self.setSetting('UI/Language',lang)
                self.translateUI()
            return func
        for lang in self.languages:
            action = QAction(lang,self)
            action.triggered.connect(changeLang(lang))
            self.menuLang.addAction(action)

    def addThemeActions(self):
        def useTheme(style):
            def func():
                QApplication.setStyle(QStyleFactory.create(style))
                QApplication.setPalette(QApplication.style().standardPalette())
                self.setSetting('UI/Theme',style)
            return func
        themes = QStyleFactory.keys()
        for theme in themes:
            action = QAction(theme,self)
            action.setText(theme.capitalize())
            action.triggered.connect(useTheme(theme))
            self.menuTheme.addAction(action)
        useTheme(self.getSetting('UI/Theme',themes[-1]))()

    def importDataFile(self,fn):
        lastFilePath = self.getSetting("File/lastFilePath",os.path.expanduser('~'))
        extensions = "All (*.pdb;*.mol;*.xyz);;PDB File (*.pdb);;MOL File (*.mol);;XYZ File (*.xyz)"
        (fileName,fileType) =QFileDialog.getOpenFileName(self,self.translate('Open'),lastFilePath,extensions,"All (*.pdb;*.mol;*.xyz)")
        if fileName == '':
            return
        fileName = API.formatPath(fileName)
        dirName = os.path.dirname(fileName)
        self.setSetting('File/lastFilePath',dirName)
        try:
            fn(fileName)
        except Exception as identify:
            print(identify)
            self.critical('Invalid Data File!')

    def prompt(self,text,msg='information'):
        if msg == 'critical':
            return QMessageBox.critical(self,self.translate("Critical"),self.translate(text),QMessageBox.Yes | QMessageBox.No)
        elif msg == 'warnning':
            return QMessageBox.warning(self,self.translate("Warning"),self.translate(text),QMessageBox.Yes | QMessageBox.No)
        else:
            return QMessageBox.information(self,self.translate("Information"),self.translate(text),QMessageBox.Yes | QMessageBox.No)

    def information(self,text):
        return QMessageBox.information(self,self.translate("Information"),self.translate(text),QMessageBox.Yes)
        
    def critical(self,text):
        return QMessageBox.critical(self,self.translate("Critical"),self.translate(text),QMessageBox.Yes)

    def warnning(self,text):
        return QMessageBox.warning(self,self.translate("Warning"),self.translate(text),QMessageBox.Yes)

    def setSetting(self,key,value):
        self.settings.setValue(key,value)
        self.settings.sync()

    def getSetting(self,key,default):
        value = self.settings.value(key)
        if value == None or value == '':
            self.settings.setValue(key,default)
            self.settings.sync()
            return default
        return value

    def translate(self,text):
        if text in self.langText:
            return self.langText[text]
        return text

    def useLanguage(self,lang):
        self.langText = {}
        try:
            self.langText = json.load(open('languages/%s.lang' % lang,encoding='utf-8'))
        except:
            pass

    def translateUI(self):
        lang = self.getSetting('UI/Language','English')
        self.useLanguage(lang)
        _ = self.translate
        self.menuFile.setTitle(_('File'))
        self.menuEdit.setTitle(_('Edit'))
        self.menuData.setTitle(_('Data'))
        self.menuView.setTitle(_('View'))
        self.menuLang.setTitle(_('Language'))
        self.menuTheme.setTitle(_('Theme'))

        self.menuAdd.setTitle(_('Add'))
        self.actionAddImport.setText(_('Import'))
        self.actionAddDraw.setText(_('Draw'))
        self.actionFilePref.setText(_('Preference'))
        self.actionFileExit.setText(_('Exit'))
        self.actionFileExit.setStatusTip(_('Exit application'))

        self.actionEditCopy.setText(_('Copy'))
        self.actionEditPaste.setText(_('Paste'))
        self.actionEditDelete.setText(_('Delete'))

        self.actionDataSource.setText(_('Source'))

        self.menuRenderWith.setTitle(_('Render With'))
        self.actionView2D.setText(_('2D Model'))
        self.actionView3D.setText(_('3D Model'))

        self.menuTool.setTitle(_('Tool'))
        self.menuConvert.setTitle(_('Convert'))
        self.menuOpenWith.setTitle(_('Open With'))



if __name__ == '__main__':
    QApplication.setOrganizationName("ATL")
    QApplication.setOrganizationDomain("http://www.atlinfo.com")
    QApplication.setApplicationName("Quantum Chemistry Viewer")
    app = QApplication(sys.argv)
    dirname = os.path.dirname(os.path.abspath(__file__))
    mainWin = QKView(dirname)
    app.exec_()
