from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGridLayout, QPushButton, QVBoxLayout,QFormLayout,QLabel,QTextEdit,QLineEdit,QAbstractSpinBox,QDoubleSpinBox
from PyQt5.QtCore import QUrl, pyqtSignal, Qt,QSize,QThread
from PyQt5.QtGui import QIcon, QPixmap,QImage,QMouseEvent
from ..Core import API
from .Sketcher import Sketcher
from .Indraw import Indraw
from .Browser import Browser
from .ComboCheckBox import ComboCheckBox
import json

class SpinBox(QDoubleSpinBox):
    def __init__(self,suffix=None,lower=0,upper=1E6,dec=0,step=1,button=False):
        super().__init__()
        suffix and self.setSuffix(suffix)
        upper and self.setMaximum(upper)
        self.setMinimum(lower)
        self.setDecimals(dec)
        if button == False:
            self.setButtonSymbols(QAbstractSpinBox.NoButtons)

class ImageLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()

class Searcher(QThread):
    returned = pyqtSignal(str)

    def __int__(self):
        super(Searcher, self).__init__()

    def input(self,smiles):
        self.smiles = smiles

    def run(self):
        try:
            info = API.searchPubchem(self.smiles)
            data = API.hashReplace(info,{
                "IUPACName":'name',
                "Charge":'charge',
                "MolecularFormula":'formular',
                "CAS":'cas'
            })
            self.returned.emit(json.dumps(data))
        except:
            self.returned.emit("{}")
        

class Editor(QWidget):
    finished = pyqtSignal(str,name='finished')

    tags = ["溶剂","添加剂","成膜添加剂","负极添加剂","正极添加剂","阻燃剂","除水剂","络合剂","环状","链状","碳酸酯","羧酸酯","磷酸酯","亚磷酸酯","硫酸酯","磺酸酯","亚硫酸酯","砜类","硼酸酯","硅酸酯","醚类","醇类","酮类","胺类","腈类","氟代","芳香族","离子液体","阴离子","阳离子","锂盐","钠盐","钾盐"]

    searcher = Searcher()
    
    def __init__(self,parent=None):
        super(Editor, self).__init__()
        self.parent = parent
        if self.parent.getSetting("Editor/Sketcher","Sketcher") == "Sketcher":
            self.sketcher = Sketcher(self)
        else:
            self.sketcher = Indraw(self)
        if self.parent and getattr(self.parent,'browser'):
            self.browser = self.parent.browser
        else:
            self.browser = Browser(self)
            self.browser.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.parent.browser = self.browser
        self.initUI()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def initUI(self):
        self.setGeometry(0, 0, 360, 500)
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        posX = (screen.width() - size.width()) // 2
        posY = (screen.height() - size.height()) // 2
        self.move(posX,posY)
        self.setFixedSize(360,500)

        #标题
        self.setWindowTitle(self.tr('New Molecule'))
        self.setWindowIcon(QIcon(QPixmap('resource/benzene.png')))

        formLayout = QGridLayout()
        #分子图像
        
        self.Structure = ImageLabel('')
        self.Structure.setScaledContents(True)
        self.Structure.clicked.connect(lambda :self.readMOL2D(self.MOL.toPlainText()))
        formLayout.addWidget(QLabel(self.tr("Structure")), 0, 0, 1, 3)
        formLayout.addWidget(self.Structure, 0, 3, 1, 7,alignment=Qt.AlignHCenter)
        #self.disPlayStructure(API.smi2png('c1ccccc1O'))
        #分子信息
        self.UUID = QLineEdit()
        #self.UUID.setReadOnly(True)
        self.SMILES = QLineEdit()
        self.SMILES.setReadOnly(True)
        self.CAS = QLineEdit()
        self.Name = QLineEdit()
        self.Formular = QLineEdit()
        self.Formular.setReadOnly(True)
        self.Mass = SpinBox(dec=4)
        self.Mass.setReadOnly(True)
        self.Charge = SpinBox(lower=-6,upper=6,dec=0,button=True)
        self.Code = QLineEdit()
        self.Alias = QLineEdit()
        self.Tags = ComboCheckBox(self.tags)
        self.Note = QTextEdit()
        #self.Atoms = QLineEdit()
        self.XYZ = QTextEdit()
        self.MOL = QTextEdit()
        self.Image =  QLineEdit()
        #按钮
        self.Search = QPushButton(QIcon("resource/Search.png"),self.tr('Search'),self)
        self.PubChem = QPushButton(QIcon("resource/PubChem.png"),'',self)
        self.PubChem.setIconSize(QSize(54, 18))
        self.Save = QPushButton(QIcon("resource/Save.png"),self.tr('Save'),self)
        self.Search.clicked.connect(self.searchMolecule)
        self.Save.clicked.connect(self.saveMolecule)
        self.PubChem.clicked.connect(self.openPubChem)
        #formLayout.addWidget(QLabel(self.translate("UUID")), 0, 0, 1, 3)
        #formLayout.addWidget(self.UUID, 0, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("SMILES")), 1, 0, 1, 3)
        formLayout.addWidget(self.SMILES, 1, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("CAS NO.")), 2, 0, 1, 3)
        formLayout.addWidget(self.CAS, 2, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Chemical Name")), 3, 0, 1, 3)
        formLayout.addWidget(self.Name, 3, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Chemical Formular")), 4, 0, 1, 3)
        formLayout.addWidget(self.Formular, 4, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Molecular Mass")), 5, 0, 1, 3)
        formLayout.addWidget(self.Mass, 5, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Charge")), 6, 0, 1, 3)
        formLayout.addWidget(self.Charge, 6, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Private Code")), 7, 0, 1, 3)
        formLayout.addWidget(self.Code, 7, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Alias")), 8, 0, 1, 3)
        formLayout.addWidget(self.Alias, 8, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Property Labels")), 9, 0, 1, 3)
        formLayout.addWidget(self.Tags, 9, 3, 1, 7)
        formLayout.addWidget(QLabel(self.tr("Note")), 10, 0, 1, 3)
        formLayout.addWidget(self.Note, 10, 3, 1, 7)
        formLayout.addWidget(self.Search, 11, 0, 1, 2)
        formLayout.addWidget(self.PubChem, 11, 4, 1, 2)
        formLayout.addWidget(self.Save, 11, 8, 1, 2)
        self.setLayout(formLayout)

        self.searcher.returned.connect(lambda str:self.updateForm(json.loads(str)))

    def readXYZ(self,xyz):
        self.sketcher.once(self.renderForm)
        if xyz != "":
            try:
                self.sketcher.loadMolecule(API.pdb2mol2D(xyz))
            except:
                self.sketcher.show()
        else:
            self.sketcher.show()
        pass

    def readPDB(self,pdb):
        self.sketcher.once(self.renderForm)
        if pdb != "":
            try:
                self.sketcher.loadMolecule(API.pdb2mol2D(pdb))
            except:
                self.sketcher.show()
        else:
            self.sketcher.show()
        pass

    def readMOL(self,mol):
        self.sketcher.once(self.renderForm)
        if mol != "":
            try:
                self.sketcher.loadMolecule(API.mol2mol2D(mol))
            except:
                self.sketcher.show()
        else:
            self.sketcher.show()
        pass

    def readSMI(self,smi):
        self.sketcher.once(self.renderForm)
        if smi != "":
            try:
                self.sketcher.loadMolecule(API.smi2mol2D2(smi))
            except:
                self.sketcher.show()
        else:
            self.sketcher.show()
        pass

    def readMOL2D(self,mol):
        self.sketcher.once(self.renderForm)
        if mol != "":
            try:
                self.sketcher.loadMolecule(mol)
            except:
                self.sketcher.show()
        else:
            self.sketcher.show()
        pass

    def renderForm(self,mol,img):
        smi = API.mol2can(mol)
        info = {
            'smiles':smi,
            'mol':mol,
            'image':img,
            'cas': '',
            'name': '',
            'code':'',
            'alias':'',
            'tags':'',
            'note':''
        }
        info['xyz'] = API.mol2xyz(mol)
        #info['atoms'] = 
        info['formular'] = API.calcFormular(API.calcAtomList(info['xyz']))
        info['mass'] = API.calcFormularMass(info['formular'])
        info['charge'] = API.smi2chg(smi)
        info['uuid'] = API.md5(smi)
        self.initForm(info)

    def initForm(self,info):
        if info['smiles'] != self.SMILES.text():
            smi = info['smiles']
            xyz = info['xyz'] or API.smi2xyz(smi)
            formular = info['formular'] or API.calcFormular(API.calcAtomList(xyz))
            mass = info['mass'] or API.calcFormularMass(formular)
            chg = info['charge'] or API.smi2chg(smi)
            uuid = info['uuid'] or API.md5(smi)
            cas = info['cas']
            name = info['name']
            code = info['code']
            alias = info['alias']
            tags = info['tags']
            note = info['note']
            self.UUID.setText(uuid)
            self.SMILES.setText(smi)
            self.CAS.setText(cas)
            self.Name.setText(name)
            self.Formular.setText(formular)
            self.Mass.setValue(mass)
            self.Charge.setValue(chg)
            self.Code.setText(code)
            self.Alias.setText(alias)
            self.Tags.setText(tags)
            self.Note.setPlainText(note)
            self.XYZ.setPlainText(xyz)
            
        mol = info['mol'] or API.smi2mol2D2(smi)
        img = info['image'] or API.smi2png(smi)
        self.MOL.setPlainText(mol)
        self.disPlayStructure(img)
        self.show()

    def updateForm(self,info):
        cas = API.getKey(info,'cas')
        cas and self.CAS.setText(cas)
        name = API.getKey(info,'name')
        name and self.Name.setText(name)
        code = API.getKey(info,'code')
        code and self.Code.setText(code)
        alias = API.getKey(info,'alias')
        alias and self.Alias.setText(alias)
        tags = API.getKey(info,'tags')
        tags and self.Tags.setText(tags)
        note = API.getKey(info,'note')
        note and self.Note.setPlainText(note)
        self.Search.setEnabled(True)

    def initDefault(self):
        smi = "c1ccccc1"
        mol = ''''''
        xyz = ''''''

    def searchMolecule(self):
        self.Search.setDisabled(True)
        smi = self.SMILES.text()
        if self.parent and getattr(self.parent,'db'):
            res = self.parent.db.index_query_smi(smi)
            if len(res) >= 1:
                return self.updateForm(res[0])
        self.searcher.input(smi)
        self.searcher.start()
        pass

    def openPubChem(self):
        self.browser.open(QUrl(API.pubChemURI(self.SMILES.text())))
        self.browser.show()

    def saveMolecule(self):
        data = {
            "uuid":self.UUID.text(), #uuid
            "smiles":self.SMILES.text(), #smiles
            "cas":self.CAS.text(), #cas
            "name":self.Name.text(), #name
            "formular":self.Formular.text(), #formular
            "mass":self.Mass.value(), #mass
            "charge":self.Charge.value(), #charge
            #"atoms":self.Atoms.text(), #atoms
            "code":self.Code.text(), #code
            "alias":self.Alias.text(), #alias
            "tags":self.Tags.text(), #tags
            "note":self.Note.toPlainText(), #note
            "xyz":self.XYZ.toPlainText(), #xyz
            "mol":self.MOL.toPlainText(), #mol
            "image":self.Image.text(), #imgae
        }
        self.finished.emit(json.dumps(data))
        self.close()
        pass

    def disPlayStructure(self,str):
        self.Image.setText(str)
        img = API.base64ToImage(str)
        img = QImage.fromData(img)
        pix = QPixmap.fromImage(img)       
        height = pix.height()
        width = pix.width()
        ratio = min(180/width,60/height)
        self.Structure.setPixmap(pix)
        if ratio < 1:
            width *= ratio
            height *= ratio
        self.Structure.setFixedSize(width,height)

    def once(self,fn):
        def func(*argv):
            fn(*argv)
            self.finished.disconnect(func)
        self.finished.connect(func)

    def closeEvent(self, event):
        self.sketcher.close()
        self.browser.close()
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