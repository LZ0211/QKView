from PyQt5.QtWidgets import QDockWidget,QWidget,QFileDialog,QTabWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QGridLayout,QLabel,QTextEdit,QPushButton,QAbstractItemView,QTableView,QMenu,QAction,QTreeView,QFileSystemModel,QComboBox
from PyQt5.QtCore import QUrl,Qt,QDir
from PyQt5.QtGui import QPixmap,QImage,QStandardItemModel,QStandardItem,QIcon,QCursor,QDoubleValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView,QWebEngineSettings
from ..Core import API
import traceback,os,requests,json

class QDataLineEdit(QWidget):
    def __init__(self,text="",suffix=None,prefix=None):
        super().__init__()
        self.lineEdit = QLineEdit(text)
        self.suffix_label = None
        self.prefix_label = None
        layout = QHBoxLayout(self)
        #layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        if prefix != None:
            self.prefix_label = QLabel(prefix)
            #self.prefix_label.setFixedHeight(28)
            layout.addWidget(self.prefix_label)
        layout.addWidget(self.lineEdit)
        if suffix != None:
            self.suffix_label = QLabel(suffix)
            #self.suffix_label.setFixedHeight(28)
            layout.addWidget(self.suffix_label)
        
        validator = QDoubleValidator(self.lineEdit)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.lineEdit.setValidator(validator)
        self.lineEdit.setFixedWidth(160)
        #self.setStyleSheet("background-color:black;")
        #self.setFixeHeight(26)
        #self.show()

    def setValue(self,val):
        self.lineEdit.setText(str(val))

    def value(self):
        text = self.lineEdit.text()
        if text != "":
            return float(text)


JS_test = '''var pdb = `REMARK
HETATM    1  O   MOL A   1      -2.030   0.000  -0.000  -0.33957515   1.5200 O
HETATM    2  C   MOL A   1      -0.845  -0.000   0.000   0.36693862   1.7000 C
HETATM    3  O   MOL A   1      -0.068   1.100   0.105  -0.19657335   1.5200 O
HETATM    4  C   MOL A   1       1.285   0.755  -0.114  -0.05553065   1.7000 C
HETATM    5  C   MOL A   1       1.285  -0.755   0.114  -0.05533179   1.7000 C
HETATM    6  O   MOL A   1      -0.068  -1.100  -0.105  -0.19670603   1.5200 O
HETATM    7  H   MOL A   1       1.923   1.308   0.588   0.12701495   1.2000 H
HETATM    8  H   MOL A   1       1.569   1.025  -1.145   0.11137415   1.2000 H
HETATM    9  H   MOL A   1       1.569  -1.025   1.146   0.11136246   1.2000 H
HETATM   10  H   MOL A   1       1.923  -1.308  -0.588   0.12702678   1.2000 H
END
`
        
var mol = viewer.addModel(pdb, 'pqr');
mol.setStyle({}, {
    stick:{
        radius: 0.075,
        colorscheme:{
            prop:'ss',
            map:$3Dmol.ssColors.Jmol
        }
    }, 
    sphere:{
        radius:0.35, 
        colorscheme:{
            prop:'ss',
            map:$3Dmol.ssColors.Jmol
        }
    }
});
mol.setStyle({ elem: 'H' }, {
    sphere: {
        radius:0.25, 
        colorscheme:{ 
            prop:'ss',
            map:$3Dmol.ssColors.Jmol
        }
    }
}, true);
viewer.zoomTo();
viewer.render(noop);
'''

JS_loadXYZ = '''var xyz = `%s`
viewer.clear();
var mol = viewer.addModel(xyz, 'xyz');
mol.setStyle({}, {
    stick:{radius: 0.075,singleBonds:false,colorscheme:'Jmol'}, 
    sphere:{scale:0.25,colorscheme:'Jmol'}
});
viewer.zoomTo();
viewer.render(noop);
'''

JS_displayCharge = '''var pdb = `%s`
viewer.clear();     
var mol = viewer.addModel(pdb, 'pqr');
var grad =  new $3Dmol.Gradient.RWB(%s,%s);
mol.setStyle({},{
    stick:{radius:0.075,colorscheme:{prop:'partialCharge',gradient:grad}},
    sphere:{radius:0.25,colorscheme:{prop:'partialCharge',gradient:grad}}
});
viewer.addPropertyLabels("atom",{},{fontSize: 14,showBackground:false,alignment:"center"})
viewer.addPropertyLabels("charge",{},{fontSize: 12,showBackground:false})
//mol.setStyle({elem:'H'},{sphere:{radius:0.25,colorscheme:{prop:'partialCharge',gradient:grad}}},true);
viewer.zoomTo();
viewer.render(noop);
'''

JS_loadMOL = '''var mol = `%s`
transformer3d.loadMolecule(ChemDoodle.readMOL(mol,1))
'''

class DataView(QDockWidget):
    def __init__(self,str,parent=None):
        super(DataView,self).__init__(str,parent)
        self.parent = parent
        self.uuid = ""
        self.cache = []
        self.pageIndex = 0
        self.setFixedWidth(360)
        #self.setMinimumSize(300,600)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        #self.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.window = QTabWidget()
        self.Summary = QWidget()
        self.Structure = QWidget()
        self.Explorer = QWidget()
        self.Property = QWidget()
        self.Reactivity = QWidget()
        self.Spectrum = QWidget()
        self.setWidget(self.window)

        self.window.addTab(self.Summary,self.tr("Summary"))
        self.window.addTab(self.Structure,self.tr("Structure"))
        self.window.addTab(self.Explorer,self.tr("Raw Data"))
        self.window.addTab(self.Property,self.tr("Properties"))
        self.window.addTab(self.Reactivity,self.tr("Reactivity"))
        self.window.addTab(self.Spectrum,self.tr("Spectrum"))

        self.window.currentChanged.connect(self.switchPage)

        self.initSummary()
        self.initStructure()
        self.initExplorer()
        self.initProperty()
        self.initReactivity()

    def showDataContent(self):
        if self.pageIndex in self.cache:
            return
        if self.pageIndex == 0:
            self.tryRun(self.showSummary)()
        elif self.pageIndex == 1:
            self.tryRun(self.showStructure)()
        elif self.pageIndex == 2:
            self.tryRun(self.showExplorer)()
        elif self.pageIndex == 3:
            self.tryRun(self.showProperty)()
        elif self.pageIndex == 4:
            self.tryRun(self.showReactivity)()
        elif self.pageIndex == 5:
            pass
        self.cache.append(self.pageIndex)

    def switchPage(self,ndx):
        self.pageIndex = ndx
        self.showDataContent()

    def setId(self,uuid):
        self.uuid = uuid
        self.cache = []
        self.showDataContent()

    def initSummary(self):
        self.summary_3dView = QWebEngineView(self)
        self.summary_3dView.setUrl(QUrl(API._3DViewURL))
        self.summary_3dView.page().settings().setAttribute(QWebEngineSettings.ShowScrollBars,False)
        self.summary_3dView.setFixedHeight(200)
        #self._3dView.setFixedWidth(300)
        #self._3dView.loadFinished.connect(lambda:self.execute(JS_test))
        self.summary_smiles = QLineEdit("")
        self.summary_formular = QLineEdit("")
        self.summary_name = QLineEdit("")
        self.summary_cas = QLineEdit("")
        self.summary_mass = QLineEdit("")
        self.summary_charge = QLineEdit("")
        # self.alias = QLabel("")
        self.summary_point_group = QLineEdit("C1")
        self.summary_dipole = QLineEdit("")
        self.summary_homo = QLineEdit("")
        self.summary_lumo = QLineEdit("")
        self.summary_note = QTextEdit("")
        form = QWidget()
        layout = QVBoxLayout(self.Summary)
        #layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(0)
        layout.addWidget(self.summary_3dView)
        layout.addWidget(form)
        infos = {
            "SMILES":self.summary_smiles,
            "Chemical Formular":self.summary_formular,
            "Chemical Name":self.summary_name,
            "CAS NO.":self.summary_cas,
            "Molecular Mass":self.summary_mass,
            "Charge":self.summary_charge,
            "Point Group":self.summary_point_group,
            "Dipole":self.summary_dipole,
            "HOMO":self.summary_homo,
            "LUMO":self.summary_lumo,
            "Note":self.summary_note
        }
        formLayout = QFormLayout()
        for (k,v) in infos.items():
            t = QLabel('<font face="Times New Roman">'+self.tr(k)+'</font>')
            formLayout.addRow(t,v)
            v.setReadOnly(True)
            #v.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.setLayout(formLayout)
        self.Summary.setLayout(layout)
        pass

    def showSummary(self):
        #self.setFixedWidth(360)
        info = self.parent.db.index_query_id(self.uuid)[0]
        self.summary_3dView.page().runJavaScript(JS_loadMOL % API.xyz2mol(info["xyz"]),lambda *argv:None)
        self.summary_smiles.setText(info["smiles"])
        self.summary_formular.setText(info["formular"])
        self.summary_name.setText(info["name"])
        self.summary_cas.setText(info["cas"])
        self.summary_mass.setText(str(info["mass"]))
        self.summary_charge.setText(str(info["charge"]))
        self.summary_note.setText(info["note"])
        summary = self.parent.db.summary_query(self.uuid)
        if len(summary) == 1:
            summary = summary[0]
            self.summary_point_group.setText(summary["point_group"])
            self.summary_dipole.setText('%.4f' % summary["dipole"])
            self.summary_homo.setText('%.4f eV' % summary["homo"])
            self.summary_lumo.setText('%.4f eV' % summary["lumo"])
        else:
            self.summary_point_group.setText("")
            self.summary_dipole.setText("")
            self.summary_homo.setText("")
            self.summary_lumo.setText("")
        pass

    def initStructure(self):
        def saveGeom():
            xyz = self.structure_xyz.toPlainText()
            self.parent.db.index_update({"uuid":self.uuid,"xyz":xyz})
            self.structure_edit.setDisabled(True)

        def saveImage(*argv):
            info = self.parent.db.index_query_id(self.uuid)[0]
            if info['image'] != "":
                img = API.base64ToImage(info['image'])
                ext = "Portable Network Graphics (*.png)"
                (Name,Type) = QFileDialog.getSaveFileName(
                    self,self.tr("Save File"),
                    self.parent.getSetting("File/lastFilePath",self.parent.defaultDir),ext,ext)
                if Name == '':
                    return
                fileName = API.formatPath(Name)
                open(fileName,'wb+').write(img)

        def showMenu():
            menu = QMenu(self)
            saveImg = QAction(self.tr('Save Image'),self)
            saveImg.triggered.connect(self.tryRun(saveImage))
            self.img_menu = menu
            menu.addAction(saveImg)
            menu.popup(QCursor.pos())
            menu.show()
        self.structure_image = QLabel('')
        self.structure_image.setScaledContents(True)
        self.structure_xyz = QTextEdit("")
        self.structure_edit = QPushButton(self.tr("Save Geometry"))
        self.structure_edit.clicked.connect(saveGeom)
        self.structure_xyz.textChanged.connect(lambda :self.structure_edit.setEnabled(True))
        self.structure_image.setContextMenuPolicy(Qt.CustomContextMenu)
        self.structure_image.customContextMenuRequested.connect(showMenu)
        layout = QVBoxLayout(self.Structure)
        layout.addWidget(self.structure_image,alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("XYZ"))
        layout.addWidget(self.structure_xyz)
        layout.addWidget(self.structure_edit)
        pass

    def showStructure(self):
        #self.setFixedWidth(360)
        info = self.parent.db.index_query_id(self.uuid)[0]
        if info['image'] == "":
            self.structure_image.setText("")
        else:
            img = API.base64ToImage(info['image'])
            img = QImage.fromData(img)
            pix = QPixmap.fromImage(img)
            pix = pix.scaled(min(pix.width(),300),min(pix.height(),80),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.structure_image.setPixmap(pix)
        self.structure_xyz.setText(info['xyz'])
        self.structure_edit.setDisabled(True)
        pass

    def initExplorer(self):
        def sortTable(idx):
            self.file_id = idx
            if self.file_order == "D":
                self.file_model.sort(idx, Qt.DescendingOrder)
                self.file_view.horizontalHeader().setSortIndicator(idx, Qt.DescendingOrder)
                self.file_order = "A"
            else:
                self.file_model.sort(idx, Qt.AscendingOrder)
                self.file_view.horizontalHeader().setSortIndicator(idx, Qt.AscendingOrder)
                self.file_order = "D"
        def showTableMenu(*argv):
            menu = QMenu(self)
            self.file_view.contextMenu = menu
            file = currentTableFile()
            if file == None:
                menu.addActions([self.file_refresh])
                menu.popup(QCursor.pos())
                menu.show()
                return
            menu.addActions([self.file_down,self.file_refresh])
            menu.popup(QCursor.pos())
            menu.show()

        def showTreeMenu(*argv):
            menu = QMenu(self)
            self.tree.contextMenu = menu
            file = currentTreeFile()
            if file == "":
                return
            menu.addActions([self.file_read,self.file_dele])
            ext = file.split(".")[-1].lower()
            if ext in ["gjf"]:
                menu.addActions([self.file_gview])
            if ext in ["out","log","fchk","fch"]:
                menu.addActions([self.file_gview,self.file_mwfn])
            if ext in ["cub","cube"]:
                menu.addActions([self.file_gview,self.file_vmd])
            if ext in ["chg","wfn"]:
                menu.addActions([self.file_mwfn])
            if ext in ["pdb"]:
                menu.addActions([self.file_gview,self.file_vesta,self.file_vmd,self.file_mwfn])
            menu.popup(QCursor.pos())
            menu.show()

        def currentTableFile():
            row = self.file_view.currentIndex().row()
            if row < 0:
                return
            if self.parent == None:
                dirname = os.path.expanduser('~')
            else:
                dirname = self.parent.thisDir
            filename = self.file_model.item(row,0).text()
            return os.path.join(dirname,'datas',self.uuid,filename)

        def currentTreeFile():
            return self.tree_model.filePath(self.tree.currentIndex())

        def download():
            file = currentTableFile()
            if file != None and not os.path.exists(file):
                API.downloadFile(self.uuid,file)

        def view():
            file = currentTreeFile()
            if file != None and os.path.exists(file):
                os.startfile(file)

        def delete():
            file = currentTreeFile()
            os.remove(file)

        def tableClick():
            file = currentTableFile()
            if file == None:
                return
            if not os.path.exists(file):
                API.downloadFile(self.uuid,file)
            os.startfile(file)

        def treeClick():
            file = currentTreeFile()
            os.startfile(file)

        self.file_down = QAction(QIcon("resource/download.png"),self.tr('Download'),self)
        self.file_read = QAction(QIcon("resource/View.png"),self.tr('View'),self)
        self.file_dele = QAction(QIcon("resource/Delete.png"),self.tr('Delete'),self)
        self.file_refresh = QAction(QIcon("resource/refresh.png"),self.tr('Refresh'),self)
        self.file_gview = QAction(QIcon("resource/GaussView.png"),self.tr('GaussView'),self)
        self.file_vesta = QAction(QIcon("resource/VESTA.png"),self.tr('VESTA'),self)
        self.file_vmd = QAction(QIcon("resource/VMD.png"),self.tr('VMD'),self)
        self.file_mwfn = QAction(QIcon("resource/Multiwfn.png"),self.tr('Multiwfn'),self)

        self.file_down.triggered.connect(download)
        self.file_read.triggered.connect(view)
        self.file_dele.triggered.connect(delete)
        self.file_refresh.triggered.connect(self.showExplorer)
        self.file_gview.triggered.connect(lambda:self.parent.interfaceGaussView(currentTreeFile()))
        self.file_vesta.triggered.connect(lambda:self.parent.interfaceVESTA(currentTreeFile()))
        self.file_vmd.triggered.connect(lambda:self.parent.interfaceVMD(currentTreeFile()))
        self.file_mwfn.triggered.connect(lambda:self.parent.interfaceMultiwfn(currentTreeFile()))
        
        self.file_model = QStandardItemModel(0, 3)
        self.file_model.setHorizontalHeaderLabels(["Name","Size","Type","Date Modified"])
        self.file_view = QTableView()
        self.file_view.setModel(self.file_model)
        self.file_view.verticalHeader().setVisible(False)
        self.file_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.file_view.horizontalHeader().setStretchLastSection(True)
        self.file_view.horizontalHeader().setHighlightSections(False)
        self.file_view.setShowGrid(False)

        self.file_view.horizontalHeader().setSortIndicatorShown(True)
        self.file_order = 'A'
        self.file_id = 0
        self.file_view.horizontalHeader().sectionClicked.connect(sortTable)
        self.file_view.customContextMenuRequested.connect(self.tryRun(showTableMenu))
        self.file_view.doubleClicked.connect(tableClick)

        self.tree_model = QFileSystemModel()
        
        #self.model.setNameFilters(['*.out','*.log','*.tif','*.txt','*.fch','*.fchk','*.chk'])
        self.tree_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        #self.tree_model.setReadOnly(False)
        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setAnimated(False)
        self.tree.setIndentation(0)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionMode(QTreeView.SingleSelection)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.tryRun(showTreeMenu))
        self.tree.doubleClicked.connect(treeClick)
        #self.tree.header().hide()

        layout = QVBoxLayout(self.Explorer)
        layout.addWidget(self.file_view)
        layout.addWidget(self.tree)

    def showExplorer(self):
        #self.setFixedWidth(900)
        self.file_model.removeRows(0,self.file_model.rowCount())
        files = API.getFiles(self.uuid)
        for file in files:
            filename = QStandardItem(file[0])
            ext = file[2]
            if ext in ["chk","fchk","fch","log","out","gjf","cub","cube"]:
                filename.setIcon(QIcon("resource/GaussView.png"))
            elif ext in ["pdb","cif","mol","mol2","vasp","xyz"]:
                filename.setIcon(QIcon("resource/VESTA.png"))
            elif ext == "txt":
                filename.setIcon(QIcon("resource/txt.ico"))
            else:
                filename.setIcon(QIcon("resource/Blank.ico"))
            size = QStandardItem()
            size.setData(int(file[1]),Qt.EditRole)
            types = QStandardItem(file[2] + " File")
            time = QStandardItem(file[3])
            self.file_model.appendRow([filename,size,types,time])
        if self.file_id >= 0:
            if self.file_order == "A":
                self.file_model.sort(self.file_id, Qt.DescendingOrder)
            else:
                self.file_model.sort(self.file_id, Qt.AscendingOrder)
        self.file_view.resizeColumnsToContents()
        self.file_view.resizeRowsToContents()
        self.file_view.resizeColumnsToContents()
        self.file_view.resizeRowsToContents()
        root = os.path.join(self.parent.thisDir,'datas',self.uuid)
        if not os.path.exists(root):
            os.makedirs(root)
        self.tree_model.setRootPath(root)
        self.tree.setRootIndex(self.tree_model.index(root))

    def initProperty(self):
        def save(*argv):
            properties = {
                "uuid":self.uuid,
                "density":self.pro_density.value(),
                "melting":self.pro_melting.value(),
                "boiling":self.pro_boiling.value(),
                "refractive":self.pro_refractive.value(),
                "flash":self.pro_flash.value(),
                "ignition":self.pro_ignition.value(),
                "dielectric":self.pro_dielectric.value(),
                "re_potential":self.pro_reduction.value(),
                "ox_potential":self.pro_oxidation.value(),
                "ionization":self.pro_ionization.value(),
                "viscosity":self.pro_viscosity.value(),
                "vis_temp":self.pro_visTemp.value(),
                "vis_temp_ka":self.pro_visTempA.value(),
                "vis_temp_kb":self.pro_visTempB.value(),
                "vis_temp_kc":self.pro_visTempC.value(),
                "vis_temp_kd":self.pro_visTempD.value(),
                "surf_tension_a":self.pro_tensionA.value(),
                "surf_tension_b":self.pro_tensionB.value(),
                "pK1":self.pro_pK1.value()
            }
            isNull = []
            for (k,v) in properties.items():
                if v == None:
                    isNull.append(k)
            for k in isNull:
                del properties[k]
            self.parent.db.physic_update_insert(properties)
        layout = QVBoxLayout(self.Property)
        form = QWidget()
        form_layout = QFormLayout(form)
        self.pro_save = QPushButton(self.tr("Save Properties to DataBase"))
        self.pro_density = QDataLineEdit(suffix="<font face='Times New Roman'>g/mL</font>")
        self.pro_melting = QDataLineEdit(suffix="<font face='Times New Roman'>°C</font>")
        self.pro_boiling = QDataLineEdit(suffix="<font face='Times New Roman'>°C at 1atm</font>")
        self.pro_flash = QDataLineEdit(suffix="<font face='Times New Roman'>°C</font>")
        self.pro_ignition = QDataLineEdit(suffix="<font face='Times New Roman'>°C</font>")
        self.pro_refractive = QDataLineEdit(suffix="")
        self.pro_dielectric = QDataLineEdit(suffix="")
        self.pro_oxidation = QDataLineEdit(suffix="<font face='Times New Roman'>V v.s Li<sup>+</sup>/Li</font>")
        self.pro_reduction = QDataLineEdit(suffix="<font face='Times New Roman'>V v.s Li<sup>+</sup>/Li</font>")
        self.pro_ionization = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.pro_viscosity = QDataLineEdit(suffix="<font face='Times New Roman'>mN·s·m<sup>-2</sup></font>")
        self.pro_visTemp = QDataLineEdit(suffix="<font face='Times New Roman'>°C</font>")
        self.pro_visTempA = QDataLineEdit(suffix="")
        self.pro_visTempB = QDataLineEdit(suffix="<font face='Times New Roman'>×10<sup>-2</sup>·K</font>")
        self.pro_visTempC = QDataLineEdit(suffix="<font face='Times New Roman'>×10<sup>2</sup>·K<sup>-1</sup></font>")
        self.pro_visTempD = QDataLineEdit(suffix="<font face='Times New Roman'>×10<sup>5</sup>·K<sup>-2</sup></font>")
        self.pro_tensionA = QDataLineEdit(suffix="<font face='Times New Roman'>mN·m<sup>-1</sup></font>")
        self.pro_tensionB = QDataLineEdit(suffix="<font face='Times New Roman'>mN·m<sup>-1</sup>·°C<sup>-1</sup></font>")
        self.pro_pK1 = QDataLineEdit(suffix="")
        form_layout.addRow(QLabel(self.tr("Density")),self.pro_density)
        form_layout.addRow(QLabel(self.tr("Melting Point")),self.pro_melting)
        form_layout.addRow(QLabel(self.tr("Boiling Point")),self.pro_boiling)
        form_layout.addRow(QLabel(self.tr("Flash Point")),self.pro_flash)
        form_layout.addRow(QLabel(self.tr("Ignition Point")),self.pro_ignition)
        form_layout.addRow(QLabel(self.tr("Refractive")),self.pro_refractive)
        form_layout.addRow(QLabel(self.tr("Oxidation Potential")),self.pro_oxidation)
        form_layout.addRow(QLabel(self.tr("Reduction Potential")),self.pro_reduction)
        form_layout.addRow(QLabel(self.tr("Ionization Energy")),self.pro_ionization)
        form_layout.addRow(QLabel(self.tr("Dielectric Constant")),self.pro_dielectric)
        form_layout.addRow(QLabel(self.tr("Viscosity")),self.pro_viscosity)
        form_layout.addRow(QLabel(self.tr("Vis Test Temp")),self.pro_visTemp)
        #r=a-bt
        form_layout.addRow(QLabel(self.tr("Vis-Temp Equation")),QLabel("<font face='Times New Roman'>lg(η)=A + B/T + C×T + D×T<sup>2</sup></font>"))
        form_layout.addRow(QLabel(self.tr("Vis-Temp Ka")),self.pro_visTempA)
        form_layout.addRow(QLabel(self.tr("Vis-Temp Kb")),self.pro_visTempB)
        form_layout.addRow(QLabel(self.tr("Vis-Temp Kc")),self.pro_visTempC)
        form_layout.addRow(QLabel(self.tr("Vis-Temp Kd")),self.pro_visTempD)
        form_layout.addRow(QLabel(self.tr("Surface Tension Equation")),QLabel("<font face='Times New Roman'><i>γ</i>=<i>a</i> - <i>bt</i></font>"))
        form_layout.addRow(QLabel(self.tr("Surface Tension a")),self.pro_tensionA)
        form_layout.addRow(QLabel(self.tr("Surface Tension b")),self.pro_tensionB)
        form_layout.addRow(QLabel(self.tr("pK1")),self.pro_pK1)
        layout.addWidget(form)
        layout.addWidget(self.pro_save)
        self.pro_save.clicked.connect(self.tryRun(save))

    def showProperty(self):
        self.setFixedWidth(360)
        properties = self.parent.db.physic_query(self.uuid)
        if len(properties) == 1:
            properties = properties[0]
            self.pro_density.setValue(properties["density"])
            self.pro_melting.setValue(properties["melting"])
            self.pro_boiling.setValue(properties["boiling"])
            self.pro_refractive.setValue(properties["refractive"])
            self.pro_flash.setValue(properties["flash"])
            self.pro_ignition.setValue(properties["ignition"])
            self.pro_dielectric.setValue(properties["dielectric"])
            self.pro_reduction.setValue(properties["re_potential"])
            self.pro_oxidation.setValue(properties["ox_potential"])
            self.pro_ionization.setValue(properties["ionization"])
            self.pro_viscosity.setValue(properties["viscosity"])
            self.pro_visTemp.setValue(properties["vis_temp"])
            self.pro_visTempA.setValue(properties["vis_temp_ka"])
            self.pro_visTempB.setValue(properties["vis_temp_kb"])
            self.pro_visTempC.setValue(properties["vis_temp_kc"])
            self.pro_visTempD.setValue(properties["vis_temp_kd"])
            self.pro_tensionA.setValue(properties["surf_tension_a"])
            self.pro_tensionB.setValue(properties["surf_tension_b"])
            self.pro_pK1.setValue(properties["pK1"])
        else:
            self.pro_density.setValue("")
            self.pro_melting.setValue("")
            self.pro_boiling.setValue("")
            self.pro_refractive.setValue("")
            self.pro_flash.setValue("")
            self.pro_ignition.setValue("")
            self.pro_dielectric.setValue("")
            self.pro_reduction.setValue("")
            self.pro_oxidation.setValue("")
            self.pro_ionization.setValue("")
            self.pro_viscosity.setValue("")
            self.pro_visTemp.setValue("")
            self.pro_visTempA.setValue("")
            self.pro_visTempB.setValue("")
            self.pro_visTempC.setValue("")
            self.pro_visTempD.setValue("")
            self.pro_tensionA.setValue("")
            self.pro_tensionB.setValue("")
            self.pro_pK1.setValue("") 

    def initReactivity(self):
        self.reax_viewer = QWebEngineView(self)
        self.reax_viewer.setUrl(QUrl(API._3DMOLURL))
        self.reax_viewer.page().settings().setAttribute(QWebEngineSettings.ShowScrollBars,False)
        self.reax_viewer.setFixedHeight(300)

        self.reax_charge = QComboBox(self.Reactivity)
        self.reax_cdft = QComboBox(self.Reactivity)

        def displayCharge(name):
            if name != "":
                data = json.loads(self.reax_charge_data[name])
                upper = max(max(data),abs(min(data)))
                pdb = API.geomchg2pdb(self.reax_geom,data)
                self.reax_viewer.page().runJavaScript(JS_displayCharge % (pdb,-1*upper,upper),lambda *argv:None)
            else:
                self.reax_viewer.page().runJavaScript(JS_loadXYZ % API.geom2xyz(self.reax_geom),lambda *argv:None)
        self.reax_charge_data = {}
        self.reax_charge.currentTextChanged.connect(self.tryRun(displayCharge))

        def displayCdft(name):
            if name != "":
                data = json.loads(self.reax_cdft_data[name])
                upper = max(data)
                pdb = API.geomchg2pdb(self.reax_geom,data)
                self.reax_viewer.page().runJavaScript(JS_displayCharge % (pdb,-1*upper,upper),lambda *argv:None)
            else:
                self.reax_viewer.page().runJavaScript(JS_loadXYZ % API.geom2xyz(self.reax_geom),lambda *argv:None)
        self.reax_cdft_data = {}
        self.reax_cdft.currentTextChanged.connect(self.tryRun(displayCdft))

        form = QWidget()
        layout = QVBoxLayout(self.Reactivity)
        layout.addWidget(self.reax_viewer)
        layout.addWidget(form)
        formLayout = QFormLayout(form)
        formLayout.addRow(QLabel('<font face="Times New Roman">'+self.tr("Atomic Charge")+'</font>'),self.reax_charge)
        formLayout.addRow(QLabel('<font face="Times New Roman">'+self.tr("Conceptual DFT")+'</font>'),self.reax_cdft)

        self.reax_vip = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.reax_vea = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.reax_negativity = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.reax_potential = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.reax_hardness = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.reax_softness = QDataLineEdit(suffix="<font face='Times New Roman'>eV<sup>-1</sup></font>")
        self.electr_index = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")
        self.nucle_index = QDataLineEdit(suffix="<font face='Times New Roman'>eV</font>")

        infos = {
            "Vertical IP":self.reax_vip,
            "Vertical EA":self.reax_vea,
            "Electro Negativity":self.reax_negativity,
            "Chemical Potential":self.reax_potential,
            "Hardness":self.reax_hardness,
            "Softness":self.reax_softness,
            "Electrophilicity Index":self.electr_index,
            "Nucleophilicity Index":self.nucle_index,
        }
        for (k,v) in infos.items():
            t = QLabel('<font face="Times New Roman">'+self.tr(k)+'</font>')
            formLayout.addRow(t,v)
        pass

    def showReactivity(self):
        info = self.parent.db.index_query_id(self.uuid)[0]
        self.reax_viewer.page().runJavaScript(JS_loadXYZ % info["xyz"],lambda *argv:None)
        self.reax_charge_data = {}
        self.reax_cdft_data = {}
        self.reax_charge.clear()
        self.reax_cdft.clear()

        summary = self.parent.db.summary_query(self.uuid)
        if len(summary) == 1:
            self.reax_geom = json.loads(summary[0]["geometry"])
        charges = self.parent.db.charge_query(self.uuid)
        if len(charges) == 1:
            self.reax_charge_data = charges[0]
            self.reax_charge.addItem("")
            isEmpty = True
            for (key,val) in self.reax_charge_data.items():
                if key != "uuid" and val != "":
                    self.reax_charge.addItem(key)
                    isEmpty = False
            if isEmpty:
                self.reax_charge.clear()
        cdfts = self.parent.db.cdft_query(self.uuid)
        if len(cdfts) == 1:
            self.reax_cdft_data = cdfts[0]
            self.reax_cdft.addItem("")
            isEmpty = True
            for (key,val) in self.reax_cdft_data.items():
                if key in ["f_plus","f_minus","f_zero","cdd","condensed_electr_index","condensed_nucle_index","condensed_softness"] and val != "":
                    self.reax_cdft.addItem(key)
                    isEmpty = False
            if isEmpty:
                self.reax_cdft.clear()
            self.reax_vip.setValue(self.reax_cdft_data["vertical_ip"])
            self.reax_vea.setValue(self.reax_cdft_data["vertical_ea"])
            self.reax_negativity.setValue(self.reax_cdft_data["electro_negativity"])
            self.reax_potential.setValue(self.reax_cdft_data["chemical_potential"])
            self.reax_hardness.setValue(self.reax_cdft_data["hardness"])
            self.reax_softness.setValue(self.reax_cdft_data["softness"])
            self.electr_index.setValue(self.reax_cdft_data["electr_index"])
            self.nucle_index.setValue(self.reax_cdft_data["nucle_index"])
        else:
            self.reax_vip.setValue("")
            self.reax_vea.setValue("")
            self.reax_negativity.setValue("")
            self.reax_potential.setValue("")
            self.reax_hardness.setValue("")
            self.reax_softness.setValue("")
            self.electr_index.setValue("")
            self.nucle_index.setValue("")

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

    def closeEvent(self,e):
        self.setHidden(True)