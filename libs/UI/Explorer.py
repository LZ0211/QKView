import os,sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon

class Explorer(QWidget):

    def __init__(self,root=""):
        super().__init__()
        self.title = 'PyQt5 file system view - pythonspot.com'
        self.root = root
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.root))
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.setWindowTitle("Dir View")
        self.tree.resize(640, 480)
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)
        
        self.show()

    def bindEvents(self):
        self.tree.clicked.connect()
'''
QModelIndex index = treeView->currentIndex();
    if (!index.isValid()) {
        return;
    }
    bool ok;
    if (model->fileInfo(index).isDir()) {
        ok = model->rmdir(index);
    } else {
        ok = model->remove(index);
    }
    if (!ok) {
        QMessageBox::information(this,
                         tr("Remove"),
                         tr("Failed to remove %1").arg(model->fileName(index)));
    }
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dirname = os.path.dirname(os.path.abspath(__file__))
    ex = Explorer(dirname)
    sys.exit(app.exec_())