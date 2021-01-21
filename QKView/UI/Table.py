import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QTableView,QAbstractItemView,QComboBox,QLineEdit,QPushButton,QHBoxLayout,QVBoxLayout,QLabel,QStyledItemDelegate
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
            pix = pix.scaled(100,60,Qt.KeepAspectRatio,Qt.SmoothTransformation)
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

class Table(QWidget):
    def __init__(self, parent=None,cols=[],header=[]):
        super(Table, self).__init__(parent)
        # 设置标题与初始大小
        #self.setWindowTitle('QTableView表格视图的例子')
        self.parent = parent
        self.resize(500, 300)
        self.sortId = -1
        self.cols = cols
        self.colsNum = len(cols)
        self.header = []
        for char in header:
            self.header.append(self.tr(char))
        for i in range(len(header),self.colsNum):
            self.header.append(cols[i])

        # 设置数据层次结构，4行4列
        self.model = QStandardItemModel(0, self.colsNum)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(self.header)

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.horizontalHeader = self.tableView.horizontalHeader()
        self.verticalHeader = self.tableView.verticalHeader()
        for i in range(self.colsNum):
            if self.cols[i] == 'image':
                self.tableView.setItemDelegateForColumn(i,ImageDelegate(self))
                self.tableView.setColumnWidth(i, 104)
                #self.tableView.resizeColumnToContents(i)
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

        self.tableView.resizeRowsToContents()

        # self.model.sort(1,Qt.DescendingOrder)
        self.horizontalHeader.setSortIndicatorShown(True)
        self.sortOrder = 'AscendingOrder'
        self.horizontalHeader.sectionClicked.connect(self.sortTable)
        #self.setStyleSheet(style)

        #
        # 当前选中的数据
        # indexs=self.tableView.selectionModel().selection().indexes()

        # 设置布局
        self.toolBar = QWidget()
        self.searchType = QComboBox(self)
        self.searchType.addItems(['Fuzzy','Precise'])
        self.searchField = QComboBox(self)
        self.searchField.addItem('All')
        self.searchField.addItems(list(filter(lambda x:x in cols,['uuid','cas','name','formular','alias','code','tags','note'])))
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
        self.sortId = idx
        if self.sortOrder == "DescendingOrder":
            self.model.sort(idx, Qt.DescendingOrder)
            self.horizontalHeader.setSortIndicator(idx, Qt.DescendingOrder)
            self.sortOrder = "AscendingOrder"
        else:
            self.model.sort(idx, Qt.AscendingOrder)
            self.horizontalHeader.setSortIndicator(idx, Qt.AscendingOrder)
            self.sortOrder = "DescendingOrder"

    def loadDatas(self,array):
        self.model.removeRows(0,self.model.rowCount())
        #self.tableView.reset()
        for record in array:
            data = []
            for col in self.cols:
                val = record[col]
                data.append(QStandardItem(str(val)))
            self.model.appendRow(data)
        if self.sortId >= 0:
            if self.sortOrder == "AscendingOrder":
                self.model.sort(self.sortId, Qt.DescendingOrder)
            else:
                self.model.sort(self.sortId, Qt.AscendingOrder)

    def tr(self,text):
        if self.parent:
            return self.parent.tr(text)
        return text

