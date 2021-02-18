import os,sys
#sys.path = ['','libs','python.zip','env']
from PyQt5 import QtWebEngineWidgets, QtCore, QtSql
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from QKView.UI import QKView

if __name__ == '__main__':
    dirname = os.path.dirname(os.path.abspath(__file__))
    config = os.path.join(dirname,"FLAGS.txt")
    if os.path.exists(config):
        flags = open(config).read()
        os.putenv("QTWEBENGINE_CHROMIUM_FLAGS", flags)
    QApplication.setOrganizationName("ATL")
    QApplication.setOrganizationDomain("http://www.atlinfo.com")
    QApplication.setApplicationName("Quantum Chemistry Viewer")
    argv = [
        '--enable-webgl-software-rendering',
        '--ignore-gpu-blacklist',
        '--enable-gpu-rasterization',
        '--enable-native-gpu-memory-buffers',
        '--enable-checker-imaging'
    ]
    app = QApplication(sys.argv+argv)
    splash = QSplashScreen(QPixmap("resource/init.png"))
    splash.show()
    mainWin = QKView(dirname)
    splash.finish(mainWin)
    app.exec_()