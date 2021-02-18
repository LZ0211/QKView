import os,sys,re,traceback
from json import load
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QBrush, QColor, QCursor, QPalette, QPainter, QFont, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtWidgets import QWidget, QLineEdit, QFileDialog, QListWidget, QListWidgetItem, QApplication, QStackedWidget, QRadioButton, QAbstractItemView, QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, QLineEdit, QCheckBox, QLabel,QComboBox,QDesktopWidget, QPushButton, QSpinBox, QColorDialog, QMenu, QAction, QTextEdit, QDoubleSpinBox, QSlider, QFrame,QButtonGroup
from ..Core import API

class ColorBar(QFrame):
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()
    def __init__(self,color='#000000'):
        super().__init__()
        self.setFixedSize(80,20)
        self.setColor(color)

    def setColor(self,color='#ffffff'):
        self.color = color
        self.setStyleSheet('border-width:1px;border-style:solid;border-color:rgb(120, 120, 120);background-color:' + color)

    def getColor(self):
        return self.color

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

    def mouseDoubleClickEvent(self, e):
        self.doubleClicked.emit()

class SwitchButton(QSlider):
    def __init__(self, parent=None):
        super(SwitchButton, self).__init__(parent)
        self.resize(50, 20)
        self.setFixedSize(50,20)
        self.setMinimum(0)
        self.setMaximum(1)
        self.setOrientation(Qt.Orientation.Horizontal)

    def paintEvent(self, event):
        """绘制按钮"""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # 定义字体样式
        font = QFont('Microsoft YaHei')
        font.setPixelSize(10)
        font.setWeight(500)
        painter.setFont(font)
        # 开关为开的状态
        if self.value() == 1:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#2292DD'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)
            # 绘制圆圈
            painter.setPen(Qt.NoPen)
            brush.setColor(QColor('#ffffff'))
            painter.setBrush(brush)
            painter.drawRoundedRect(32, 2, 16, 16, 8, 8)
            # 绘制文本
            painter.setPen(QPen(QColor('#ffffff')))
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(10, 2, 36, 16), Qt.AlignLeft, 'ON')
        else:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#FFFFFF'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height()//2, self.height()//2)
            # 绘制圆圈
            pen = QPen(QColor('#999999'))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(2, 2, 16, 16, 8, 8)
            # 绘制文本
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(20, 2, 36, 16), Qt.AlignLeft, 'OFF')

class SpinBox(QDoubleSpinBox):
    def __init__(self,suffix=None,lower=0,upper=None,dec=0,step=1):
        super().__init__()
        suffix and self.setSuffix(suffix)
        upper and self.setMaximum(upper)
        self.setMinimum(lower)
        self.setDecimals(dec)
        self.setSingleStep(step)
        self.setFixedWidth(80)

class Preference(QWidget):
    def __init__(self,parent=None):
        super(Preference, self).__init__()
        self.parent = parent
        self.setupUI()

    def center(self):
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) / 2
        posY = (screen.height() - size.height()) / 2
        self.move(posX,posY)

    def setupUI(self):
        self.setGeometry(20, 20, 560, 400)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)
        self.setFixedSize(560, 400)

        self.setWindowTitle(self.tr('Preference'))
        self.setWindowIcon(QIcon('resource/chemical.png'))

        self.list = QListWidget()
        self.list.setFixedWidth(120)
        self.list.insertItem(0,self.tr('UI'))
        self.list.insertItem(1,self.tr('Plugins'))
        self.list.insertItem(2,self.tr('Graph'))
        self.list.insertItem(3,self.tr('Server'))
        self.list.insertItem(4,self.tr('Gaussian'))
        self.stack = QStackedWidget()
        self.tabUI()
        self.tabPlugins()
        self.tabGraph()
        self.tabServer()
        self.tabGaussian()

        hbox = QHBoxLayout()
        hbox.addWidget(self.list)
        hbox.addWidget(self.stack)
        self.setLayout(hbox)

        self.list.currentRowChanged.connect(self.display)
        index = int(self.getSetting("UI/Preference",0))
        self.list.setCurrentRow(index)

    def tabUI(self):
        self.UI = QWidget()
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        def switchSketcher(name):
            self.setSetting("UI/Sketcher",name)
            if self.parent:
                self.parent.editor.initSketcher()

        self.sketcherOptions = QComboBox(self)
        self.sketcherOptions.addItems(['Sketcher','Indraw'])
        self.sketcherOptions.currentTextChanged.connect(switchSketcher)
        self.sketcherOptions.setCurrentText(self.getSetting("UI/Sketcher","Indraw"))

        self.molViewerOptions = QComboBox(self)
        self.molViewerOptions.addItems(['3Dmol','3Dview'])
        self.molViewerOptions.currentTextChanged.connect(lambda str:self.setSetting("UI/3DViewer",str))
        self.molViewerOptions.setCurrentText(self.getSetting("UI/3DViewer","3Dmol"))

        self.recordWindowSize = SwitchButton(self)
        self.recordWindowSize.valueChanged.connect(lambda val:self.setSetting("UI/recordWindowSize",val))
        self.recordWindowSize.setValue(int(self.getSetting("UI/recordWindowSize",0)))
        self.recordWindowPos = SwitchButton(self)
        self.recordWindowPos.valueChanged.connect(lambda val:self.setSetting("UI/recordWindowPos",val))
        self.recordWindowPos.setValue(int(self.getSetting("UI/recordWindowPos",0)))

        def switchSelection(val):
            self.setSetting("UI/recordSelection",val)
            if val == 0:
                self.displayDataAtStartUp.setValue(0)

        def switchDataDisplay(val):
            self.setSetting("UI/displayDataAtStartUp",val)
            if val == 1:
                self.recordSelection.setValue(1)
        self.recordSelection = SwitchButton(self)
        self.recordSelection.valueChanged.connect(switchSelection)
        self.displayDataAtStartUp = SwitchButton(self)
        self.displayDataAtStartUp.valueChanged.connect(switchDataDisplay)
        self.recordSelection.setValue(int(self.getSetting("UI/recordSelection",0)))
        self.displayDataAtStartUp.setValue(int(self.getSetting("UI/displayDataAtStartUp",0)))

        layout.addRow(self.tr("Sketcher"),self.sketcherOptions)
        layout.addRow(self.tr("3dViewer"),self.molViewerOptions)
        layout.addRow(self.tr("Record Window Size"),self.recordWindowSize)
        layout.addRow(self.tr("Record Window Position"),self.recordWindowPos)
        layout.addRow(self.tr("Record Selection"),self.recordSelection)
        layout.addRow(self.tr("Display Data At StartUp"),self.displayDataAtStartUp)

        self.UI.setLayout(layout)
        self.stack.addWidget(self.UI)

    def tabPlugins(self):
        self.Plugins = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        def selectTempDirectory():
            filepath = QFileDialog.getExistingDirectory(None,self.tr('Select Cache Directory'), cacheFile.TempDirectory.text())
            if not filepath:
                return
            cacheFile.TempDirectory.setText(filepath)
            self.setSetting('File/TempDirectory',filepath)

        radio_system = QRadioButton(self.tr('Use temporary directory of system'))
        radio_custom = QRadioButton(self.tr('Use custom directory: '))

        tempbox = QHBoxLayout()
        tempbox.setContentsMargins(0, 0, 0, 0)
        cacheFile = QWidget()
        cacheFile.buttonGroup = QButtonGroup(cacheFile)
        cacheFile.buttonGroup.addButton(radio_system)
        cacheFile.buttonGroup.addButton(radio_custom)
        cacheFile.setLayout(tempbox)
        cacheFile.TempDirectory = QLineEdit(self.getSetting('File/TempDirectory',os.path.join(self.parent.thisDir,"cache")))
        cacheFile.TempDirectory.setReadOnly(True)
        cacheFile.selectBtn = QPushButton(self.tr('Browse'))
        cacheFile.selectBtn.setFixedWidth(50)
        cacheFile.selectBtn.clicked.connect(selectTempDirectory)
        tempbox.addWidget(radio_custom)
        tempbox.addWidget(cacheFile.TempDirectory)
        tempbox.addWidget(cacheFile.selectBtn)
    
        layout.addWidget(QLabel(self.tr("Temporary directory")))
        layout.addWidget(radio_system)
        layout.addWidget(cacheFile)

        def selectGaussViewPath(*argv):
            (Name,Type) = QFileDialog.getOpenFileName(
                self,
                self.tr('Select GaussView Path'), 
                gviewFile.Path.text()
            )
            if Name == '':
                return
            fileName = API.formatPath(Name)
            gviewFile.Path.setText(Name)
            self.setSetting('Interface/GaussView',Name)

        gviewbox = QHBoxLayout()
        gviewbox.setContentsMargins(0, 0, 0, 0)
        gviewFile = QWidget()
        gviewFile.setLayout(gviewbox)
        gviewFile.Path = QLineEdit(self.getSetting("Interface/GaussView",os.path.join(self.parent.thisDir,"plugins/g16w/gview.exe")))
        gviewFile.Path.setReadOnly(True)
        gviewFile.selectBtn = QPushButton(self.tr('Browse'))
        gviewFile.selectBtn.setFixedWidth(50)
        gviewFile.selectBtn.clicked.connect(self.tryRun(selectGaussViewPath))
        gviewbox.addWidget(gviewFile.Path)
        gviewbox.addWidget(gviewFile.selectBtn)
    
        layout.addWidget(QLabel(self.tr("GaussView program path")))
        layout.addWidget(gviewFile)

        def selectVESTAPath(*argv):
            (Name,Type) = QFileDialog.getOpenFileName(
                self,
                self.tr('Select VESTA Path'), 
                vestaFile.Path.text()
            )
            if Name == '':
                return
            fileName = API.formatPath(Name)
            vestaFile.Path.setText(Name)
            self.setSetting('Interface/VESTA',Name)

        vestabox = QHBoxLayout()
        vestabox.setContentsMargins(0, 0, 0, 0)
        vestaFile = QWidget()
        vestaFile.setLayout(vestabox)
        vestaFile.Path = QLineEdit(self.getSetting("Interface/VESTA",os.path.join(self.parent.thisDir,"plugins/VESTA/VESTA.exe")))
        vestaFile.Path.setReadOnly(True)
        vestaFile.selectBtn = QPushButton(self.tr('Browse'))
        vestaFile.selectBtn.setFixedWidth(50)
        vestaFile.selectBtn.clicked.connect(self.tryRun(selectVESTAPath))
        vestabox.addWidget(vestaFile.Path)
        vestabox.addWidget(vestaFile.selectBtn)
    
        layout.addWidget(QLabel(self.tr("VESTA program path")))
        layout.addWidget(vestaFile)

        def selectVMDPath(*argv):
            (Name,Type) = QFileDialog.getOpenFileName(
                self,
                self.tr('Select VMD Path'), 
                vmdFile.Path.text()
            )
            if Name == '':
                return
            fileName = API.formatPath(Name)
            vmdFile.Path.setText(Name)
            self.setSetting('Interface/VMD',Name)

        vmdbox = QHBoxLayout()
        vmdbox.setContentsMargins(0, 0, 0, 0)
        vmdFile = QWidget()
        vmdFile.setLayout(vmdbox)
        vmdFile.Path = QLineEdit(self.getSetting("Interface/VMD",os.path.join(self.parent.thisDir,"plugins/VMD/vmd.exe")))
        vmdFile.Path.setReadOnly(True)
        vmdFile.selectBtn = QPushButton(self.tr('Browse'))
        vmdFile.selectBtn.setFixedWidth(50)
        vmdFile.selectBtn.clicked.connect(self.tryRun(selectVMDPath))
        vmdbox.addWidget(vmdFile.Path)
        vmdbox.addWidget(vmdFile.selectBtn)
    
        layout.addWidget(QLabel(self.tr("VMD program path")))
        layout.addWidget(vmdFile)

        def selectMultiwfnPath(*argv):
            (Name,Type) = QFileDialog.getOpenFileName(
                self,
                self.tr('Select Multiwfn Path'), 
                mwfnFile.Path.text()
            )
            if Name == '':
                return
            fileName = API.formatPath(Name)
            mwfnFile.Path.setText(Name)
            self.setSetting('Interface/Multiwfn',Name)

        mwfnbox = QHBoxLayout()
        mwfnbox.setContentsMargins(0, 0, 0, 0)
        mwfnFile = QWidget()
        mwfnFile.setLayout(mwfnbox)
        mwfnFile.Path = QLineEdit(self.getSetting("Interface/Multiwfn",os.path.join(self.parent.thisDir,"plugins/Multiwfn/Multiwfnexe")))
        mwfnFile.Path.setReadOnly(True)
        mwfnFile.selectBtn = QPushButton(self.tr('Browse'))
        mwfnFile.selectBtn.setFixedWidth(50)
        mwfnFile.selectBtn.clicked.connect(self.tryRun(selectMultiwfnPath))
        mwfnbox.addWidget(mwfnFile.Path)
        mwfnbox.addWidget(mwfnFile.selectBtn)
    
        layout.addWidget(QLabel(self.tr("Multiwfn program path")))
        layout.addWidget(mwfnFile)

        self.Plugins.setLayout(layout)
        self.stack.addWidget(self.Plugins)

    def tabGraph(self):
        self.Graph = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.Graph.setLayout(layout)
        self.stack.addWidget(self.Graph)

    def tabServer(self):
        self.Server = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.Server.setLayout(layout)
        self.stack.addWidget(self.Server)

    def tabGaussian(self):
        self.Gaussian = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.Gaussian.setLayout(layout)
        self.stack.addWidget(self.Gaussian)

    def display(self,index):
        self.stack.setCurrentIndex(index)
        self.setSetting("Display/Preference",index)

    def getSetting(self,key,value):
        if self.parent:
            return self.parent.getSetting(key,value)
        return value

    def setSetting(self,key,value):
        if self.parent:
            return self.parent.setSetting(key,value)

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

    def tryRun(self,fn):
        def fun(*argv):
            try:
                fn(*argv)
            except:
                print(traceback.format_exc())
        return fun
