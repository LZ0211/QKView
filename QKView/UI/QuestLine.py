from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QTreeView,QPushButton,QLabel,QStyledItemDelegate,QProgressBar,QTreeWidget,QGridLayout
from PyQt5.QtGui import QIcon, QPixmap,QImage,QPainter,QStandardItemModel,QStandardItem

class QuestLine(QWidget):
    Quests = [
        {
            "text":"基本计算",
            "next":[{"text":"结构优化"},{"text":"单点计算"},{"text":"振动分析"}]
        },
        {
            "text":"氧化还原",
            "next":[{"text":"概念密度泛函"},{"text":"氧化电位（G4+SMD）"},{"text":"还原电位（G4+SMD）"}]
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
            "next":[{"text":"质子结合能"},{"text":"Li+结合能"},{"text":"Na+结合能"},{"text":"Mg2+结合能"},{"text":"Mn2+结合能"},{"text":"Co2+结合能"},{"text":"Fe2+结合能"},{"text":"Fe3+结合能"},{"text":"Cu2+结合能"},{"text":"Zn2+结合能"},{"text":"Ni2+结合能"},{"text":"F-结合能"},{"text":"Cl-结合能"}]
        },
        {
            "text":"光谱",
            "next":[{"text":"核磁共振谱"},{"text":"红外光谱"},{"text":"拉曼光谱"},{"text":"紫外可见吸收"},{"text":"荧光光谱"}]
        },
        {
            "text":"基本分子描述符",
            "next":[{"text":"氢键受体数"},{"text":"氢键供体数"},{"text":"可旋转键数"},{"text":"脂肪环数量"},{"text":"芳香环数量"},{"text":"SP3杂化碳原子比例"}]
        }
    ]
    def __init__(self,parent):
        super(QuestLine, self).__init__(parent)
        self.parent = parent
        self.setFixedWidth(240)
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
        self.model.setHorizontalHeaderLabels([self.tr('Calculation Quests')])
        self.initTree(self.model,self.Quests)
        self.treeView.setModel(self.model)

        self.model.itemChanged.connect(self.treeItemChanged)

        self.processBar = QProgressBar()
        #self.processBar.setFixedWidth(220)
        self.processBar.setValue(0)
        self.processBar.setMaximum(100)
        self.startBtn = QPushButton(QIcon("resource/start.png"),self.tr("Start"))
        self.stopBtn = QPushButton(QIcon("resource/stop.png"),self.tr("Stop"))
        self.clearBtn = QPushButton(QIcon("resource/clear.png"),self.tr("Clear"))
        self.list = QTreeWidget()
        self.list.setFixedHeight(200)
        self.list.setHeaderLabel(self.tr("Calculation Queue"))
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
            if item.hasChildren():
                for i in range(item.rowCount()):
                    sub = item.child(i)
                    if sub.checkState() == Qt.Checked:
                        list.append(sub.text())
            elif item.checkState() == Qt.Checked:
                list.append(item.text())
        return list

    def setValueList(self,list):
        rows = self.model.rowCount()
        for i in range(rows):
            item = self.model.item(i,0)
            if item.hasChildren():
                for i in range(item.rowCount()):
                    sub = item.child(i)
                    if sub.checkState() == Qt.Checked:
                        self.checkChildChanged(sub)
            elif item.checkState() == Qt.Checked:
                self.checkChildChanged(item)

    def setDisableList(self,list):
        rows = self.model.rowCount()
        for i in range(rows):
            item = self.model.item(i,0)
            if item.hasChildren():
                for i in range(item.rowCount()):
                    sub = item.child(i)
                    if sub.isCheckable() and sub.text() in list:
                        sub.setCheckable(False)
            elif item.isCheckable():
                item.setCheckable(False)

    def tr(self,text):
        if self.parent:
            return self.parent.tr(text)
        return text
        