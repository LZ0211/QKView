import os,sys
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QListWidgetItem, QTreeWidgetItem, QSplitter, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QPushButton, QSplashScreen, QToolBar, QMainWindow, QSystemTrayIcon, QStatusBar, QToolBar, QMenuBar, QMenu, QAction,QStyleFactory,QFileDialog,QMessageBox
from PyQt5.QtCore import QUrl, pyqtSignal, QSize, Qt, QSettings
from PyQt5.QtGui import QIcon, QColor, QPixmap,QCursor
from . import Sketcher, Indraw, Editor, MainWindow, Table, Browser, QuestLine,DataView
from ..Core import API
from ..Core.SQL import MoleculeDataBase
from ..Core.Project import Project
import json,time,subprocess
from tempfile import mktemp

class QKView(QMainWindow,MainWindow):

    extensions = [
        "All (*.pdb;*.mol;*.xyz)",
        "PDB File (*.pdb)",
        "MOL File (*.mol)",
        "XYZ File (*.xyz)"
    ]

    FileMenu = {
        "name":"&File",
        "actions":[
            {
                "name":"&Add",
                "icon":"Add.png",
                "actions":[
                    ("Import",'import.png'),
                    ("Draw",'mol.png')
                ]
            },
            ("Preference",'setting.png'),
            ("Exit",'exit.png')
        ]
    }
    EditMenu = {
        "name":"&Edit",
        "actions":[
            ("Edit","edit.png"),
            ("Copy","copy.png"),
            ("Delete","delete.png"),
            {
                "name":"Export",
                "icon":"hexagonal.png",
                "actions":["pdb","xyz","mol"]
            },
            ("Add To Queue","queue.png")
        ]
    }

    DataMenu = {
        "name":"&Data",
        "actions":[
            ("Data Source","source.png"),
            ("Data Download","download.png")
        ]
    }

    ViewMenu = {
        "name":"&View",
        "actions":[
            ('GaussView','GaussView.png'),
            ('VESTA','VESTA.png'),
            ('VMD','VMD.png')
        ]
    }

    ToolMenu = {
        "name":"&Tool",
        "actions":[
            {
                "name":"Convert",
                "actions":['pdb2xyz','pdb2mol','mol2xyz','mol2Pdb','xyz2mol','xyz2pdb']
            },
            {
                "name":"OpenWith",
                "actions":[
                    ('Gaussian','Gaussian.png'),
                    ('ORCA','ORCA.png'),
                    ('Multiwfn','Multiwfn.png')
                ]
            },
            {
                "name":"QSPR Model",
                "actions":[
                    ('Crystal Density'),
                    ('Vapor Enthalpy'),
                    ('Sublime Enthalpy'),
                    ('Boiling Point'),
                    ('Melting Point'),
                    ('Flash Point'),
                    ('Solvation Free Energy'),
                    ('Surface Tension'),
                    ('Viscosity')
                ]
            }
        ]
    }

    ToolBar = ["Import","Draw","|","Edit","Delete","Copy","Add To Queue","|","Data Source","GaussView","VESTA","VMD"]

    def __init__(self,dirname):
        super(QKView, self).__init__(dirname)
        #MainWindow.__init__(self,dirname)
        self.calculator = Project(self)
        self.db = MoleculeDataBase()
        self.browser = Browser(self)
        #self.browser.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.view = DataView(self.tr("DataView"),self)
        self.view.setHidden(True)
        self.addDockWidget(Qt.RightDockWidgetArea,self.view)
        self.renderWindow()
        self.translateUI()
        self.show()
        self.editor = Editor(self)
        #self.freezeActions(["Edit","Delete","Data Source","Data Download"])
        self.bindActionEvents()
        self.bindTableEvents()
        self.loadDataBase()
        self.configCalculator()
        #self.browser.open('http://172.16.11.164/static/indraw/')

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
        #导航栏
        # self.navigation = QToolBar('Navigation')
        # self.navigation.setIconSize(QSize(16, 16))
        # self.addToolBar(self.navigation)
        #菜单栏
        self.menuBar = QMenuBar()
        self.setMenuBar(self.menuBar)
        self.menuView = QMenu("&View")
        self.menuTool = QMenu("&Tool")
        self.menuLang = QMenu("&Language")
        self.menuTheme = QMenu("&Theme")
        self.menuBar.addMenu(self.setMenu(self.FileMenu))
        self.menuBar.addMenu(self.setMenu(self.EditMenu))
        self.menuBar.addMenu(self.setMenu(self.DataMenu))
        self.menuBar.addMenu(self.setMenu(self.ViewMenu))
        self.menuBar.addMenu(self.setMenu(self.ToolMenu))
        self.menuBar.addMenu(self.LangMenu())
        self.menuBar.addMenu(self.ThemeMenu())
        
        #状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        #工具栏
        self.toolBar = QToolBar(self.tr("ToolBar"),self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.setBarActions(self.toolBar,self.ToolBar)
        #系统托盘
        self.tray = QSystemTrayIcon(QIcon('resource/icon.png'),self)
        self.trayMenu = QMenu("&Tray")
        self.trayMenu.addActions([
            self.getAction('Preference'),
            self.getAction('Exit')
        ])
        self.tray.setContextMenu(self.trayMenu)
        self.tray.show()
        #任务
        self.quest = QuestLine(self)
        #表格
        self.table = Table(self,
            cols = ['uuid','image','smiles','cas','name','formular','mass','alias','code','tags'],
            header = ['ID','2D Structure','smiles','CAS NO.','Chemical Name','Chemical Formular','Molecular Mass','Alias','Private Code','Property Labels']
        )
        layout = QHBoxLayout()
        layout.addWidget(self.quest)
        layout.addWidget(self.table)
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.testSql()

    def bindActionEvents(self):
        #事件槽
        self.getAction("Import").triggered.connect(
            lambda:self.importDataFile(
                lambda f:self.editMolecule(f,type="filename")
            )
        )
        self.getAction("Draw").triggered.connect(lambda :self.editMolecule())
        self.getAction("Exit").triggered.connect(self.close)
        self.getAction("GaussView").triggered.connect(self.interfaceGaussView)
        self.getAction("VESTA").triggered.connect(self.interfaceGaussVESTA)
        self.getAction("VMD").triggered.connect(self.interfaceGaussVMD)
        self.getAction('pdb').triggered.connect(self.pdbAction)
        self.getAction('mol').triggered.connect(self.molAction)
        self.getAction('xyz').triggered.connect(self.xyzAction)
        self.getAction('Edit').triggered.connect(self.editAction)
        self.getAction('Copy').triggered.connect(self.copyAction)
        self.getAction('Delete').triggered.connect(self.deleteAction)

    def bindTableEvents(self):
        def showTableMenu():
            self.table.tableView.contextMenu = QMenu(self)
            self.table.tableView.contextMenu.addActions([
                self.getAction('Edit'),
                self.getAction('Copy'),
                self.getAction('Delete'),
                self.getAction("Add To Queue"),
                self.getAction("Data Source")
            ])
            self.table.tableView.contextMenu.addMenu(self.allMenus["Export"])
            self.table.tableView.contextMenu.popup(QCursor.pos())
            self.table.tableView.contextMenu.show()

        def source():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            path = "{host}/{uuid}/".format(host=API.FTP,uuid=uuid)
            subprocess.Popen(["explorer.exe",path])
            #os.startfile()
            #self.browser.open(QUrl("ftp://{host}/{uuid}/".format(host=API.HOST,uuid=uuid)))
            #self.browser.show()

        def queue():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            data = self.db.index_query_id(uuid)[0]
            count = self.quest.list.topLevelItemCount()
            for i in range(count):
                if self.quest.list.topLevelItem(i).text(0) == uuid:
                    return
            item = QTreeWidgetItem(self.quest.list)
            item.setText(0,uuid)
            self.quest.list.insertTopLevelItem(count,item)
            self.calculator.add_queue(data)

        def search():
            text = self.table.searchText.text()
            keys = self.table.searchField.currentText()
            method = self.table.searchType.currentText()
            if method == 'Fuzzy':
                if keys == 'All':
                    return self.table.loadDatas(self.db.index_search(text))
                if keys in ['charge','mass','image','uuid']:
                    return
                self.table.loadDatas(self.db.index_search(text,[keys]))
            else:
                if keys in ['All','image','tags','note']:
                    return
                data = self.db.index_query(keys,text)
                self.table.loadDatas(data)

        def terminal():
            self.quest.startBtn.setEnabled(True)
            self.quest.clearBtn.setEnabled(True)

        def clearJobs():
            count = self.quest.list.topLevelItemCount()
            for i in range(count):
                self.quest.list.takeTopLevelItem(count-i-1)
            self.quest.processBar.setValue(0)
            self.calculator.clear()

        def startJobs():
            self.quest.startBtn.setDisabled(True)
            self.quest.clearBtn.setDisabled(True)
            self.calculator.isEnd = False
            self.calculator.interval = int(self.getSetting("Calculator/Interval",10))
            self.calculator.start()
            pass

        def stopJobs():
            self.calculator.end()
            pass

        def showDataView():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            if self.view.uuid == uuid and self.view.isVisible():
                return
            self.view.setId(uuid)
            self.view.setVisible(True)

        def swicthDataView(*argv):
            if self.view.isHidden():
                return
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            if self.view.uuid == uuid:
                return
            self.view.setId(uuid)

        def updateJobs():
            if self.calculator.isEnd:
                self.calculator.finish = []
                self.calculator.processed.emit(0)
            self.calculator.set_text_jobs(self.quest.valueList())

        self.table.tableView.setColumnHidden(0,True)
        self.table.tableView.customContextMenuRequested.connect(showTableMenu)
        self.table.tableView.doubleClicked.connect(showDataView)
        #self.table.tableView.clicked.connect(swicthDataView)
        self.table.tableView.selectionModel().selectionChanged.connect(swicthDataView)
        
        self.getAction('Add To Queue').triggered.connect(queue)
        self.getAction("Data Source").triggered.connect(source)
        self.table.searchBtn.clicked.connect(search)
        self.table.searchText.returnPressed.connect(search)
        self.quest.model.itemChanged.connect(updateJobs)
        self.quest.startBtn.clicked.connect(startJobs)
        self.quest.stopBtn.clicked.connect(stopJobs)
        self.quest.clearBtn.clicked.connect(clearJobs)
        self.calculator.processed.connect(self.quest.processBar.setValue)
        self.calculator.terminal.connect(terminal)

        #未实现的功能不允许选择
        texts = self.quest.Quests
        invalid = []
        for group in texts:
            all = True
            for sub in group['next']:
                if Project.selectText(sub['text']) == None:
                    invalid.append(sub['text'])
                else:
                    all = False
            if all:
                invalid.append(group['text'])
        self.quest.setDisableList(invalid)
        pass

    def editMolecule(self,input="",type="smi"):
        def add(string):
            molecule = json.loads(string)
            self.db.index_add(molecule)
            self.table.loadDatas(self.db.index_query_all())
        if type == "filename":
            ext = os.path.splitext(input)[1].lower()
            dat = open(input,encoding="utf-8").read()
            if ext == ".xyz":
                return self.editMolecule(dat,type="xyz")
            if ext == ".mol":
                return self.editMolecule(dat,type="mol")
            if ext == ".pdb":
                return self.editMolecule(dat,type="pdb")
            return
        if type == "xyz":
            self.editor.finished.connect(add)
            return self.editor.readXYZ(input)
        if type == "pdb":
            self.editor.finished.connect(add)
            return self.editor.readPDB(input)
        if type == "mol":
            self.editor.finished.connect(add)
            return self.editor.readMOL(input)
        if type == "smi":
            self.editor.finished.connect(add)
            return self.editor.readSMI(input)
        pass
    
    def interfaceGaussView(self):
        GaussView = self.getSetting("Interface/GaussView","")
        file = self.tempFile()
        if GaussView == "" or file == None:
            return
        subprocess.Popen([GaussView, file],shell=True)

    def interfaceGaussVESTA(self):
        VESTA = self.getSetting("Interface/VESTA","")
        file = self.tempFile()
        if VESTA == "" or file == None:
            return
        subprocess.Popen([VESTA, file],shell=True)

    def interfaceGaussVMD(self):
        VMD = self.getSetting("Interface/VMD","")
        file = self.tempFile()
        if VMD == "" or file == None:
            return
        subprocess.Popen([VMD, file],shell=True)

    def tempFile(self,format=".pdb"):
        format = format.lower()
        row = self.table.tableView.currentIndex().row()
        if row < 0:
            return
        uuid = self.table.model.item(row,0).text()
        data = self.db.index_query_id(uuid)
        if len(data) == 1:
            info = data[0]
            xyz = info['xyz']
            if xyz == "":
                return
            if format == ".pdb":
                string = API.xyz2pdb(xyz)
            elif format == ".mol":
                string = API.xyz2mol(xyz)
            else:
                format = ".xyz"
                string = xyz
            tempdir = self.getSetting('File/TempDirectory','')
            if tempdir == '':
                tempfile = mktemp() + format
            else:
                tempfile = os.path.join(tempdir,uuid + format)
            open(tempfile,"w+").write(string)
            return tempfile
        return

    def testSql(self):
        #print(self.db.index_search('碳酸酯 溶剂'))
        #self.calculator.add
        #self.calculator.("9fb05581-bd1b-3cfe-929a-75a14a4c4568")
        pass

    def loadDataBase(self):
        self.table.loadDatas(self.db.index_query_all())
        self.activateActions(['Edit','Delete'])

    #配置计算参数
    def configCalculator(self):
        keys = ["Gauss_Core","Gauss_Memory","XTB_Core","XTB_Memory"]
        for key in keys:
            val = self.getSetting("Server/"+key,"")
            if val != "":
                self.calculator.config[key] = val

    def pdbAction(self):
        info = self.getCurrentInfo()
        if info != None and info['xyz'] != '':
            self.exportDataFile(lambda :API.xyz2pdb(info['xyz']),"PDB File (*.pdb)")

    def molAction(self):
        info = self.getCurrentInfo()
        if info != None and info['xyz'] != '':
            self.exportDataFile(lambda :API.xyz2mol(info['xyz']),"MOL File (*.mol)")

    def xyzAction(self):
        info = self.getCurrentInfo()
        if info != None and info['xyz'] != '':
            self.exportDataFile(lambda :info['xyz'],"XYZ File (*.xyz)")

    def getCurrentInfo(self):
        row = self.table.tableView.currentIndex().row()
        if row < 0:
            return
        uuid = self.table.model.item(row,0).text()
        data = self.db.index_query_id(uuid)
        if len(data) == 1:
            return data[0]

    def editAction(self):
        def update(string):
            molecule = json.loads(string)
            self.db.index_update(molecule)
            self.table.loadDatas(self.db.index_query_all())
        info = self.getCurrentInfo()
        if info != None:
            self.editor.initForm(info)
            self.editor.finished.connect(update)
            self.editor.show()

    def copyAction(self):
        info = self.getCurrentInfo()
        if info != None and info["mol"] != "":
            self.editMolecule(info["mol"],type="mol")

    def deleteAction(self):
        row = self.table.tableView.currentIndex().row()
        if row < 0:
            return
        if self.prompt("Confirmed to delete?",msg='warnning') == QMessageBox.No:
            return
        uuid = self.table.model.item(row,0).text()
        self.db.index_del(uuid)
        self.table.loadDatas(self.db.index_query_all())

    def closeEvent(self, QCloseEvent):
        self.editor.close()
        self.tray.hide()
        QCloseEvent.accept()

