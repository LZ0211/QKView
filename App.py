import os,sys
#sys.path = ['','libs','libs/python.zip','libs/env']
from PyQt5 import QtWebEngineWidgets, QtCore, QtSql
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from QKView.UI import QKView

if __name__ == '__main__':
    QApplication.setOrganizationName("ATL")
    QApplication.setOrganizationDomain("http://www.atlinfo.com")
    QApplication.setApplicationName("Quantum Chemistry Viewer")
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap("resource/init.png"))
    splash.show()
    mainWin = QKView(os.path.dirname(os.sys.argv[0]))
    splash.finish(mainWin)
    app.exec_()