from PyQt5.QtWidgets import QLineEdit,QListWidget,QCheckBox,QListWidgetItem,QComboBox
from PyQt5.QtCore import Qt

class ComboCheckBox(QComboBox):
    def __init__(self, items):
        super(ComboCheckBox, self).__init__()
        self.items = items
        self.row_num = len(self.items)
        self.Selectedrow_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        for i in range(self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(self.show)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)

    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        qItem = QListWidgetItem(self.qListWidget)
        self.qCheckBox[i].setText(self.items[i])
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    def Selectlist(self):
        Outputlist = []
        for i in range(self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
        self.Selectedrow_num = len(Outputlist)
        return Outputlist

    def show(self):
        show = ''
        Outputlist = self.Selectlist()
        #self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in Outputlist:
            show += i + ';'
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)

    def text(self):
        return self.qLineEdit.text()

    def setText(self,text):
        arr = text.split(';')
        Outputlist = []
        for i in range(self.row_num):
            text = self.qCheckBox[i].text()
            if text in arr:
                Outputlist.append(text)
                self.qCheckBox[i].setChecked(True)
            else:
                self.qCheckBox[i].setChecked(False)
        show = ''
        #self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in Outputlist:
            show += i + ';'
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)

    def clear(self):
        for i in range(self.row_num):
            self.qCheckBox[i].setChecked(False)