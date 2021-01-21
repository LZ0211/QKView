import os,sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir

class Explorer(QWidget):

    def __init__(self,root=""):
        super().__init__()
        #self.title = 'PyQt5 file system view'
        self.root = root
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        #self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root)
        #self.model.setNameFilters(['*.out','*.log','*.tif','*.txt','*.fch','*.fchk','*.chk'])
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.model.setReadOnly(False)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.root))
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        #self.tree.setWindowTitle("Dir View")
        self.tree.resize(640, 480)
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)
        
        self.show()

    def bindEvents(self):
        self.tree.clicked.connect()

    #def 
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

void DirectoryViewer::createDirectory()
{
    QModelIndex index = treeView->currentIndex();
    if (!index.isValid())
    {
        return;
    }
    QString dirName = QInputDialog::getText(this, tr("Create Directory"), tr("Directory name"));
    if (!dirName.isEmpty())
    {
        if (!model->mkdir(index, dirName).isValid())
        {
            QMessageBox::information(this, tr("Create Directory"), tr("Failed to create the directory"));
        }
    }
}

void DirectoryViewer::remove()
{
    QModelIndex index = treeView->currentIndex();
    if (!index.isValid())
    {
        return;
    }
    bool ok;
    if (model->fileInfo(index).isDir())
    {
        ok = model->rmdir(index);
    }
    else
    {
        ok = model->remove(index);
    }
    if (!ok)
    {
        QMessageBox::information(this, tr("Remove"), tr("Failed to remove %1").arg(model->fileName(index)));
    }
}
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dirname = os.path.dirname(os.path.abspath(__file__))
    ex = Explorer("ftp://172.16.11.164/61a505c2-69bb-3431-ab45-7497c13c6756/gauss/")
    sys.exit(app.exec_())