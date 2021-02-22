import sys
from PyQt5.QtCore import Qt, pyqtSignal,QRect
from PyQt5.QtWidgets import QWidget,QTableView,QAbstractItemView,QComboBox,QLineEdit,QPushButton,QHBoxLayout,QVBoxLayout,QLabel,QStyledItemDelegate,QHeaderView,QStyle, QStyleOptionButton
from PyQt5.QtGui import QPixmap,QImage,QPainter,QStandardItemModel,QStandardItem,QIcon
from ..Core import API


class ImageDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super(ImageDelegate,self).__init__(parent)

    def paint(self,painter,option,index):
        data = index.data()
        if data[:10] == "data:image":
            img = API.base64ToImage(data)
            img = QImage.fromData(img)
            pix = QPixmap.fromImage(img)
            pix = pix.scaled(min(pix.width(),100),min(pix.height(),60),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            height = pix.height()
            width = pix.width()
            rect=option.rect
            x = rect.x() + rect.width()/2-width/2   
            y = rect.y() + rect.height()/2-height/2
            painter.setRenderHint(QPainter.Antialiasing, True)
            #painter.drawImage(QRect(x,y,width,height), img)
            painter.drawPixmap(x,y,pix)
        # else:
        #     super(QStyledItemDelegate,self).paint(painter,option,index)

class CheckBoxHeader(QHeaderView):
    """自定义表头类"""
    select_all_clicked = pyqtSignal(bool)
    size = 14

    def __init__(self, orientation=Qt.Horizontal,parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.state = -1
        self.parent = parent
        self.setStyleSheet("CheckBoxHeader::section{height:24;padding:0}")

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.initFrom(self)
            self.y_offset = (rect.height() - self.size) / 2
            self.x_offset = (rect.width() - self.size) / 2
            option.rect = QRect(rect.x() + self.x_offset, rect.y() + self.y_offset, self.size, self.size)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.state == 1:
                option.state |= QStyle.State_On
            elif self.state == 0:
                option.state |= QStyle.State_NoChange
            else:
                option.state |= QStyle.State_Off
            self.style().drawPrimitive(QStyle.PE_IndicatorCheckBox, option, painter)

    def mousePressEvent(self, event):
        pos = event.pos()
        index = self.logicalIndexAt(pos)
        if 0 == index:
            x = self.sectionPosition(0)
            if x + self.x_offset < pos.x() < x + self.x_offset + self.size and self.y_offset < pos.y() < self.y_offset + self.size:
                if self.state == -1:
                    self.state = 1
                else:
                    self.state = -1
                self.select_all_clicked.emit(self.state==1)
                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    def setCheckState(self,state):
        if state == Qt.PartiallyChecked:
            self.state = 0
        elif state == Qt.Checked:
            self.state = 1
        else:
            self.state = -1
        self.updateSection(0)

class Table(QWidget):
    Display = {
        'uuid':'ID',
        'image':'2D Structure',
        'smiles':'smiles',
        'cas':'CAS NO.',
        'name':'Chemical Name',
        'formular':'Chemical Formular',
        'mass':'Molecular Mass',
        'alias':'Alias',
        'code':'Private Code',
        'tags':'Property Labels'
    }
    Field = ['uuid','cas','name','formular','alias','code','tags','note']
    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        # 设置标题与初始大小
        #self.setWindowTitle('QTableView表格视图的例子')
        self.parent = parent
        self.resize(500, 300)
        self.sortId = -1
        self.cols = [""]
        self.colsNum = 1
        self.header = [""]
        for (k,v) in self.Display.items():
            self.cols.append(k)
            self.header.append(self.tr(v))
            self.colsNum += 1

        # 设置数据层次结构，4行4列
        self.model = QStandardItemModel(0, self.colsNum)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(self.header)

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setHorizontalHeader(CheckBoxHeader(Qt.Horizontal,self))
        self.horizontalHeader = self.tableView.horizontalHeader()
        self.verticalHeader = self.tableView.verticalHeader()
        # 图片
        self.tableView.setItemDelegateForColumn(2,ImageDelegate(self))
        self.tableView.setColumnWidth(2, 104)
        # 隐藏ID
        self.tableView.setColumnHidden(1,True)
        # 隐藏默认序号
        self.tableView.verticalHeader().setHidden(True)
        # 交替背景颜色
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setStyleSheet('border 0px; color: #6b6d7b; alternate-background-color: gray; background: white;')
        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.horizontalHeader.setStretchLastSection(True)
        self.horizontalHeader.setHighlightSections(False)
        # 水平方向，表格大小拓展到适当的尺寸
        # self.horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)
        # 垂直方向，表格大小拓展
        self.verticalHeader.setDefaultSectionSize(64)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)

        # self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableView.resizeRowsToContents()

        # self.model.sort(1,Qt.DescendingOrder)
        self.horizontalHeader.setSortIndicatorShown(False)
        self.sortOrder = 'AscendingOrder'
        self.horizontalHeader.sectionClicked.connect(self.sortTable)
        #self.setStyleSheet(style)
        self.tableView.setColumnWidth(0, 21)
        self.horizontalHeader.setSectionResizeMode(0, QHeaderView.Fixed)
        #
        # 当前选中的数据
        # indexs=self.tableView.selectionModel().selection().indexes()

        self.horizontalHeader.select_all_clicked.connect(self.onAllClicked)
        self.tableView.clicked.connect(self.onChecked)

        # 设置布局
        self.toolBar = QWidget()
        self.searchType = QComboBox(self)
        self.searchType.addItems(['Fuzzy','Precise'])
        self.searchField = QComboBox(self)
        self.searchField.addItem('All')
        self.searchField.addItems(self.Field)
        self.searchText = QLineEdit(self)
        self.searchBtn = QPushButton(QIcon("resource/Search.png"),self.tr("Search"))
        barLayout = QHBoxLayout()
        barLayout.setContentsMargins(0, 0, 0, 5)
        barLayout.addWidget(QLabel(self.tr("Search Method")))
        barLayout.addWidget(self.searchType)
        barLayout.addWidget(QLabel(self.tr("Search Field")))
        barLayout.addWidget(self.searchField)
        barLayout.addWidget(self.searchText)
        barLayout.addWidget(self.searchBtn)
        self.toolBar.setLayout(barLayout)
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def sortTable(self,idx):
        if idx == 0:
            self.horizontalHeader.setSortIndicatorShown(False)
            return
        self.sortId = idx
        if self.sortOrder == "DescendingOrder":
            self.horizontalHeader.setSortIndicatorShown(True)
            self.model.sort(idx, Qt.DescendingOrder)
            self.horizontalHeader.setSortIndicator(idx, Qt.DescendingOrder)
            self.sortOrder = "AscendingOrder"
        else:
            self.horizontalHeader.setSortIndicatorShown(True)
            self.model.sort(idx, Qt.AscendingOrder)
            self.horizontalHeader.setSortIndicator(idx, Qt.AscendingOrder)
            self.sortOrder = "DescendingOrder"

    def loadDatas(self,array):
        selected = self.selectedItems()
        self.model.removeRows(0,self.model.rowCount())
        #self.tableView.reset()
        for record in array:
            check = QStandardItem()
            check.setCheckable(True)
            if record['uuid'] in selected:
                check.setCheckState(Qt.Checked)
            data = [check]
            for col in self.cols[1:]:
                val = record[col]
                data.append(QStandardItem(str(val)))
            self.model.appendRow(data)
        if self.sortId >= 0:
            if self.sortOrder == "AscendingOrder":
                self.model.sort(self.sortId, Qt.DescendingOrder)
            else:
                self.model.sort(self.sortId, Qt.AscendingOrder)

    def selectedItems(self):
        list = []
        for i in range(self.model.rowCount()):
            if self.model.item(i,0).checkState() == Qt.Checked:
                list.append(self.model.item(i,1).text())
        return list

    def searchItem(self,uuid):
        for i in range(self.model.rowCount()):
            if self.model.item(i,1).text() == uuid:
                return i
        return -1

    def selectAll(self):
        for i in range(self.model.rowCount()):
            self.model.item(i,0).setCheckState(Qt.Checked)

    def unSelectAll(self):
        for i in range(self.model.rowCount()):
            self.model.item(i,0).setCheckState(Qt.Unchecked)

    def onAllClicked(self,state):
        if state == True:
            self.selectAll()
        else:
            self.unSelectAll()

    def onChecked(self,index):
        state = False
        all = False
        for i in range(self.model.rowCount()):
            if self.model.item(i,0).checkState() == Qt.Checked:
                state = True
            else:
                all = True
        if state == False:
            self.horizontalHeader.setCheckState(Qt.Unchecked)
        elif all == False:
            self.horizontalHeader.setCheckState(Qt.Checked)
        else:
            self.horizontalHeader.setCheckState(Qt.PartiallyChecked)

    def tr(self,text):
        if self.parent:
            return self.parent.tr(text)
        return text

