import os,sys
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QListWidgetItem, QTreeWidgetItem, QSplitter, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QPushButton, QSplashScreen, QToolBar, QMainWindow, QSystemTrayIcon, QStatusBar, QToolBar, QMenuBar, QMenu, QAction,QStyleFactory,QFileDialog,QMessageBox
from PyQt5.QtCore import QUrl, pyqtSignal, QSize, Qt, QSettings
from PyQt5.QtGui import QIcon, QColor, QPixmap,QCursor
from . import Sketcher, Indraw, Editor, MainWindow, Table, Browser, QuestLine
from ..Core import API,SQL
from ..Core.SQL import MoleculeDataBase
import json,time

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
            }
        ]
    }

    ToolBar = ["Import","Draw","|","Edit","Delete","Copy","Add To Queue","|","Data Source","Data Download"]

    def __init__(self,dirname):
        super(QKView, self).__init__(dirname)
        #MainWindow.__init__(self,dirname)
        self.db = MoleculeDataBase()
        self.browser = Browser(self)
        self.browser.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.renderWindow()
        self.translateUI()
        self.show()
        self.editor = Editor(self)
        #self.freezeActions(["Edit","Delete","Data Source","Data Download"])
        self.bindActionEvents()
        self.bindTableEvents()
        self.loadDataBase()
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
        self.navigation = QToolBar('Navigation')
        self.navigation.setIconSize(QSize(16, 16))
        self.addToolBar(self.navigation)
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
        self.toolBar = QToolBar()
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
        #布局
        self.quest = QuestLine(self)
        self.table = Table(self,
            cols = ['uuid','image','smiles','cas','name','formular','mass','alias','code','tags'],
            header = ['ID','分子结构','SMI','CAS号','化学名称','分子式','分子量','简称','代号','标签']
        )
        layout = QHBoxLayout()
        layout.addWidget(self.quest)
        layout.addWidget(self.table)
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def bindActionEvents(self):
        #事件槽
        self.getAction("Import").triggered.connect(
            lambda:self.importDataFile(
                lambda f:self.editMolecule(f,type="filename")
            )
        )
        self.getAction("Draw").triggered.connect(lambda :self.editMolecule())
        self.getAction("Exit").triggered.connect(self.close)

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

        def exportPDB():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            smi = self.table.model.item(row,2).text()
            self.exportDataFile(lambda :API.smi2pdb(smi),"PDB File (*.pdb)")

        def exportMOL():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            smi = self.table.model.item(row,2).text()
            self.exportDataFile(lambda :API.smi2mol(smi),"MOL File (*.mol)")
            pass

        def exportXYZ():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            smi = self.table.model.item(row,2).text()
            self.exportDataFile(lambda :API.smi2xyz(smi),"XYZ File (*.xyz)")
            pass

        def edit():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            data = self.db.index_query_id(uuid)
            if len(data) == 1:
                self.editor.initForm(data[0])
                self.editor.finished.connect(update)
                self.editor.show()

        def copy():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            data = self.db.index_query_id(uuid)
            if len(data) == 1:
                dat = data[0]["mol"]
                if dat != "":
                    self.editMolecule(dat,type="mol")

        def update(string):
            molecule = json.loads(string)
            self.db.index_update(molecule)
            self.table.loadDatas(self.db.index_query_all())

        def delete():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            if self.prompt("Confirmed to delete?",msg='warnning') == QMessageBox.No:
                return
            uuid = self.table.model.item(row,0).text()
            self.db.index_del(uuid)
            self.table.loadDatas(self.db.index_query_all())

        def source():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            self.browser.open(QUrl("{host}/files/{uuid}/".format(host=API.HOST,uuid=uuid)))
            self.browser.show()

        def queue():
            row = self.table.tableView.currentIndex().row()
            if row < 0:
                return
            uuid = self.table.model.item(row,0).text()
            count = self.quest.list.topLevelItemCount()
            for i in range(count):
                if self.quest.list.topLevelItem(i).text(0) == uuid:
                    return
            item = QTreeWidgetItem(self.quest.list)
            item.setText(0,uuid)
            self.quest.list.insertTopLevelItem(count,item)

        def clear():
            count = self.quest.list.topLevelItemCount()
            for i in range(count):
                self.quest.list.takeTopLevelItem(count-i-1)

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

        def start():
            pass

        def stop():
            pass

        self.table.tableView.setColumnHidden(0,True)
        self.table.tableView.customContextMenuRequested.connect(showTableMenu)
        self.getAction('Edit').triggered.connect(edit)
        self.getAction('Copy').triggered.connect(copy)
        self.getAction('Delete').triggered.connect(delete)
        self.getAction('Add To Queue').triggered.connect(queue)
        self.getAction("Data Source").triggered.connect(source)
        self.getAction('pdb').triggered.connect(exportPDB)
        self.getAction('mol').triggered.connect(exportMOL)
        self.getAction('xyz').triggered.connect(exportXYZ)
        self.table.searchBtn.clicked.connect(search)
        self.table.searchText.returnPressed.connect(search)
        self.quest.startBtn.clicked.connect(start)
        self.quest.stopBtn.clicked.connect(stop)
        self.quest.clearBtn.clicked.connect(clear)
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
    
    def testSql(self):
        #print(self.db.index_search('碳酸酯 溶剂'))
        pass

    def loadDataBase(self):
        self.table.loadDatas(self.db.index_query_all())
        self.activateActions(['Edit','Delete'])

    def closeEvent(self, QCloseEvent):
        self.editor.close()
        self.tray.hide()
        QCloseEvent.accept()

