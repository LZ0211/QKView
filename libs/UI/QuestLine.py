import sys
from PyQt5.QtCore import Qt,QThread
from PyQt5.QtWidgets import QWidget,QTreeView,QPushButton,QLabel,QStyledItemDelegate,QProgressBar,QTreeWidget,QGridLayout
from PyQt5.QtGui import QPixmap,QImage,QPainter,QStandardItemModel,QStandardItem
from ..Core import API
import requests,re

reg_braket = re.compile(r'^\{\s*(\w+)\s*\}$')
reg_double_braket = re.compile(r'^\{\{\s*(\S+)\s*\}\}$')

class Project(QThread):
    gauss_setting = {}
    xtb_setting = {}
    options = [
        {
            "work":"xtb_calc",
            "name":"xtb_calc_opt",
            "text":"XTB程序优化分子结构",
            "inp":["opt"]
        },
        {
            "work":"gauss_calc",
            "name":"read_xtb_geom",
            "text":"读取XTB程序优化结构",
            "require":["xtb_calc_opt"],
            "inp":[]
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_opt",
            "text":"Gaussian程序优化分子结构",
            "inp":["opt"]
        },
        {
            "work":"gauss_calc",
            "name":"read_gauss_geom",
            "text":"读取Gaussian程序优化结构",
            "require":["gauss_calc_opt"],
            "inp":[]
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_sp",
            "text":"Gaussian程序计算单点能",
            "require":["read_gauss_geom"],
            "inp":["sp"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_dipole",
            "text":"Gaussian程序计算偶极矩",
            "require":["read_gauss_geom"],
            "inp":["dipole"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_fukui",
            "text":"Gaussian程序计算Fukui函数",
            "require":["read_gauss_geom"],
            "inp":["fukui"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_freq",
            "text":"Gaussian程序计算红外",
            "require":["read_gauss_geom"],
            "inp":["freq"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_raman",
            "text":"Gaussian程序计算拉曼",
            "require":["read_gauss_geom"],
            "inp":["raman"],
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_surface",
            "text":"Multiwfn程序计算分子表面性质",
            "require":["gauss_calc_dipole"],
            "inp":["gauss_surface"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_fukui",
            "text":"Multiwfn程序处理Fukui函数",
            "require":["gauss_calc_fukui"],
            "inp":["gauss_fukui"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_cm5_charge",
            "text":"Multiwfn计算CM5原子电荷",
            "require":["gauss_calc_sp"],
            "inp":["gauss_cm5_charge"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_adch_charge",
            "text":"Multiwfn计算ADCH原子电荷",
            "require":["gauss_calc_sp"],
            "inp":["gauss_adch_charge"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_mulliken_charge",
            "text":"Multiwfn计算Mulliken原子电荷",
            "require":["gauss_calc_sp"],
            "inp":["gauss_mulliken_charge"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_resp_charge",
            "text":"Multiwfn计算RESP原子电荷",
            "require":["gauss_calc_sp"],
            "inp":["gauss_resp_charge"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_mayer_bo",
            "text":"Multiwfn计算Mayer键级",
            "require":["gauss_calc_sp"],
            "inp":["gauss_mayer_bo"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_laplacian_bo",
            "text":"Multiwfn计算拉普拉斯键级",
            "require":["gauss_calc_sp"],
            "inp":["gauss_laplacian_bo"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_mulliken_bo",
            "text":"Multiwfn计算Mulliken键级",
            "require":["gauss_calc_sp"],
            "inp":["gauss_mulliken_bo"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_fuzzy_bo",
            "text":"Multiwfn计算模糊键级",
            "require":["gauss_calc_sp"],
            "inp":["gauss_fuzzy_bo"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_surface",
            "require":"mwfn_calc_surface",
            "inp":["gauss_surface"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_adch_charge",
            "require":["mwfn_calc_adch_charge"],
            "inp":["gauss_adch_charge"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_cm5_charge",
            "require":["mwfn_calc_cm5_charge"],
            "inp":["gauss_cm5_charge"]
        },

        {
            "work":"pipline_calc_homo",
            "name":"pipline_calc_homo",
            "text":"计算HOMO轨道",
            "require":["gauss_calc_sp"],
            "inp":["{{name}}"]
        },
        {
            "work":"pipline_calc_lumo",
            "name":"pipline_calc_lumo",
            "text":"计算LUMO轨道",
            "require":["gauss_calc_sp"],
            "inp":["{{name}}"]
        },
        {
            "work":"pipline_calc_fukui",
            "name":"pipline_calc_fukui",
            "text":"计算Fukui函数",
            "require":["gauss_calc_fukui","mwfn_calc_fukui"],
            "inp":["{{name}}"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_fukui",
            "text":"计算偶极矩",
            "require":["mwfn_calc_fukui"],
            "inp":["{{name}}","gauss_fukui"]
        }
    ]
    def __init__(self):
        super(Project, self).__init__()
        self.charge = 0
        self.spin = 1
        self.jobs = []

    def init_smi(self,smi='C'):
        self.smi = smi
        self.name = API.md5(smi)
        self.init_geom(API.smi2xyz(self.smi))
        self.set_charge(API.smi2chg(smi))

    def init_mol(self,mol):
        self.smi = API.mol2smi(mol)
        self.name = API.md5(self.smi)
        self.init_geom(API.smi2xyz(self.smi))
        found = re.search(r'M\s+CHG\s+\d+(.*)',mol)
        if found:
            charges = [int(i) for i in found.group(1).split()[1::2]]
            self.set_charge(sum(charges))

    def init_xyz(self,xyz):
        self.smi = API.xyz2smi(xyz)
        self.name = API.md5(self.smi)
        self.init_geom(xyz)

    def init_geom(self,xyz):
        lines = xyz.strip().split('\n')[2:]
        self.geometry = [line.split() for line in lines]

    def set_charge(self,charge=0):
        self.charge = charge

    def set_spin(self,spin=1):
        self.spin = spin

    def parse_input(self,param):
        found = reg_double_braket.search(param)
        if found:
            keys = re.sub(r'\[\s*(-?\d+\s*:?\s*-?\d*)\s*\]',r'.\g<1>',found.group(1)).split('.')
            this = self
            while len(keys):
                key = keys.pop(0)
                if isinstance(this,dict):
                    if not key in this:
                        return None
                    this = this[key]
                elif isinstance(this,list) or isinstance(this,tuple):
                    try:
                        matched = re.search(r'^(-?\d+)\s*:\s*(-?\d+)$',key)
                        if matched:
                            this = this[int(matched.group(1)):int(matched.group(2))]
                        elif re.search(r'^-?\d+$',key):
                            this = this[int(key)]
                        else:
                            return None
                    except:
                        return None
                else:
                    try:
                        this = getattr(this,key)
                    except:
                        return None
            return this
        found = reg_braket.search(param)
        if found:
            return param.format(**self.__dict__)
        return param

    def execute(self):
        jobs = self.jobs
        percent = 0
        count = 0
        for job in jobs:
            #反射,获取执行函数
            func = getattr(self, job["work"])
            inp = list(map(self.parse_input,job["inp"]))
            func(*inp)
            count += 1
            percent = count / len(jobs)

    def gauss_calc(self,job,**kvargv):
        status = API.read_gauss_status(self.name,job)
        #如果文件不存在或者之前计算失败，则重新提交计算
        if status in ['NonExist','Failed']:
            param = {
                'name':self.name,
                'geometry':self.geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(kvargv)
            param.update(self.gauss_setting)
            res = requests.post('{host}/job/submit/gauss/{job}'.format(host=API.HOST,job=job),json=param)
            json = JSON.loads(res.text)
            id = json['data']
        #如果任务正在运行，获取ID
        
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        #如果文件不存在，监听计算任务
        if not status == 'Exist':
            while(True):
                status = self.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(30)
        return self

    def xtb_calc(self,job,**kvargv):
        status = API.read_xtb_status(self.name,job)
        if status in ["NonExist","Failed"]:
            param = {
                'name':self.name,
                'geometry':self.geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(kvargv)
            param.update(self.gauss_setting)
            res = requests.post('{host}/job/submit/xtb/{job}'.format(host=API.HOST,job=job),json=param)
            json = JSON.loads(res.text)
            id = json['data']
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        if not status == 'Exist':
            while(True):
                status = API.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(10)
        return self

    def mwfn_calc(self,job,**kvargv):
        status = API.read_mwfn_status(self.name,job)
        if status in ['NonExist','Failed']:
            param = {'name':self.name}
            param.update(kvargv)
            res = requests.post('{host}/job/submit/mwfn/{job}'.format(host=API.HOST,job=job),json=param)
            json = JSON.loads(res.text)
            id = json['data']
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        if not status == 'Exist':
            while(True):
                status = API.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(10)
        return self

    def read_gauss_geom(self):
        self.geometry = API.read_gauss_data(self.name,'opt')[0]['Summary']['Geometry']

    def read_xtb_geom(self,name):
        self.geometry = API.read_xtb_data(self.name,'opt')["Geometry"]

    def read_mwfn_data(self,name):
        pass

    def add_job(self,jobname):
        job = Project.select(jobname)
        if job in self.jobs:
            return
        if 'require' in job:
            for pre in job['require']:
                self.add_job(pre)
        self.jobs.append(job)

    @staticmethod
    def select(jobname):
        for job in Project.options:
            if job['name'] == jobname:
                return job


class QuestLine(QWidget):
    Quests = [
        {
            "text":"结构优化",
            "next":[{"text":"XTB结构优化"},{"text":"Gaussian结构优化"}]
        },
        {
            "text":"氧化还原",
            "next":[{"text":"HOMO&LUMO能级"},{"text":"Fukui函数"},{"text":"概念密度泛函"},{"text":"氧化电位（G4+SMD）"},{"text":"还原电位（G4+SMD）"}]
        },
        {
            "text":"原子电荷",
            "next":[{"text":"Mulliken电荷"},{"text":"ADCH电荷"},{"text":"CM5电荷"},{"text":"RESP电荷"}]
        },
        {
            "text":"键级",
            "next":[{"text":"Mulliken键级"},{"text":"Mayer键级"},{"text":"拉普拉斯键级"},{"text":"模糊键级"}]
        },
        {
            "text":"表面性质",
            "next":[{"text":"分子偶极矩"},{"text":"表面静电势"},{"text":"极化率"}]
        },
        {
            "text":"结合能",
            "next":[{"text":"Li+结合能"},{"text":"Na+结合能"},{"text":"Mn2+结合能"},{"text":"Co2+结合能"},{"text":"Cu2+结合能"},{"text":"Ni2+结合能"}]
        },
        {
            "text":"光谱",
            "next":[{"text":"核磁共振谱"},{"text":"红外光谱"},{"text":"拉曼光谱"},{"text":"紫外可见吸收"},{"text":"荧光光谱"}]
        },
        {
            "text":"基本分子描述符",
            "next":[{"text":"氢键受体数"},{"text":"氢键供体数"},{"text":"可旋转键数"},{"text":"脂肪环数量"},{"text":"芳香环数量"},{"text":"SP3杂化碳原子比例"}]
        },
        {
            "text":"QSPR性质预测",
            "next":[{"text":"晶体密度"},{"text":"蒸发焓"},{"text":"升华焓"},{"text":"沸点"},{"text":"溶解自由能"},{"text":"表面张力"},{"text":"粘性"}]
        }
    ]
    def __init__(self,parent):
        super(QuestLine, self).__init__(parent)
        self.parent = parent
        self.setFixedWidth(260)
        self.treeView = QTreeView(self)
        # 禁止编辑
        self.treeView.setEditTriggers(QTreeView.NoEditTriggers)
        # 一次选中整行
        self.treeView.setSelectionBehavior(QTreeView.SelectRows)
        # 单选
        self.treeView.setSelectionMode(QTreeView.SingleSelection)
        # 每间隔一行颜色不一样，当有qss时该属性无效
        #self.treeView.setAlternatingRowColors(True)
        # 去掉鼠标移到单元格上时的虚线框
        self.treeView.setFocusPolicy(Qt.NoFocus)
        # 最后一列自适应宽度
        #self.treeView.header().setStretchLastSection(True)
        # 列头文字默认居中对齐
        self.treeView.header().setDefaultAlignment(Qt.AlignCenter)
        self.model = QStandardItemModel(0,1,self.treeView)
        self.model.setHorizontalHeaderLabels(['计算任务'])
        self.initTree(self.model,self.Quests)
        self.treeView.setModel(self.model)

        self.model.itemChanged.connect(self.treeItemChanged)

        self.processBar = QProgressBar()
        #self.processBar.setFixedWidth(220)
        self.processBar.setValue(0)
        self.startBtn = QPushButton("开始计算")
        self.stopBtn = QPushButton("停止计算")
        self.clearBtn = QPushButton("清空队列")
        self.list = QTreeWidget()
        self.list.setFixedHeight(160)
        self.list.setHeaderLabel('计算队列')
        self.list.headerItem().setTextAlignment(0,Qt.AlignHCenter)

        layout = QGridLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        #layout.setSpacing(0)
        layout.addWidget(self.treeView,0,0,1,6)
        layout.addWidget(self.list,1,0,1,6)
        layout.addWidget(self.processBar,2,0,1,6)
        layout.addWidget(self.startBtn,3,0,1,2)
        layout.addWidget(self.stopBtn,3,2,1,2)
        layout.addWidget(self.clearBtn,3,4,1,2)
        self.setLayout(layout)

    def treeItemChanged(self,item):
        if item == None:
            return
        if item.isCheckable():
            state = item.checkState()
            if item.isTristate():
                if state != Qt.PartiallyChecked:
                    self.checkAllChild(item,state == Qt.Checked)
            else:
                self.checkChildChanged(item)

    def checkAllChild(self,item,checked):
        if item == None:
            return
        rowCount = item.rowCount()
        for i in range(rowCount):
            child = item.child(i)
            self.checkAllChild(child,checked)
        if item.isCheckable():
            item.setCheckState(Qt.Checked if checked  else Qt.Unchecked)

    def checkAllChild_recursion(self,item,checked):
        if item == None:
            return
        rowCount = item.rowCount()
        for i in range(rowCount):
            child = item.child(i)
            self.checkAllChild_recursion(child,checked)
        if item.isCheckable():
            item.setCheckState(Qt.Checked if checked  else Qt.Unchecked)

    def checkChildChanged(self,item):
        if item == None:
            return
        state = self.checkSibling(item)
        last = item.parent()
        if last == None:
            return
        if Qt.PartiallyChecked == state:
            if last.isCheckable() and last.isTristate():
                last.setCheckState(Qt.PartiallyChecked)
        elif Qt.Checked == state:
            if last.isCheckable():
                last.setCheckState(Qt.Checked)
        else:
            if last.isCheckable():
                last.setCheckState(Qt.Unchecked)
        self.checkChildChanged(last)

    def checkSibling(self,item):
        last = item.parent()
        if last == None:
            return item.checkState()
        brotherCount = last.rowCount()
        checkedCount = 0
        unCheckedCount = 0
        for i in range(brotherCount):
            sibling = last.child(i)
            state = sibling.checkState()
            if Qt.PartiallyChecked == state:
                return Qt.PartiallyChecked
            elif Qt.Unchecked == state:
                unCheckedCount += 1
            else:
                checkedCount += 1
            if checkedCount > 0 and unCheckedCount > 0:
                return Qt.PartiallyChecked
        if unCheckedCount > 0:
            return Qt.Unchecked
        return Qt.Checked

    def initTree(self,model,items):
        for it in items:
            item = QStandardItem(it["text"])
            item.setCheckable(True)
            model.appendRow([item])
            if "next" in it:
                self.initTree(item,it["next"])
                item.setTristate(True)

    def valueList(self):
        list = []
        rows = self.model.rowCount()
        for i in range(rows):
            item = self.model.item(i,0)
            if item.isCheckable() and item.checkState() == Qt.Checked and not item.isTristate():
                list.append(item.text())
        return list

    def setValueList(self,list):
        rows = self.model.rowCount()
        for i in range(rows):
            item = self.model.item(i,0)
            if item.isCheckable() and item.text() in list and not item.isTristate():
                self.checkChildChanged(item)

    def setDisableList(self,list):
        rows = self.model.rowCount()
        for i in range(rows):
            item = self.model.item(i,0)
            if item.isCheckable() and item.text() in list:
                item.setDisabled(True)
        