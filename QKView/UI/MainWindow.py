import os,sys
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QAction, QStyleFactory, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon
from ..Core import API
import json

class MainWindow(QWidget):
    allActions = {}
    allMenus = {}
    defaultDir = os.path.expanduser('~')

    def __init__(self,dirname):
        super(MainWindow, self).__init__()
        self.thisDir = dirname
        self.configDir = os.path.join(dirname,"setting.ini")
        self.langDir = os.path.join(dirname,"languages")
        self.settings = QSettings(self.configDir,QSettings.IniFormat)
        self.languages = API.getLanguages(self.langDir)
        self.useLanguage(self.getSetting('UI/Language','English'))

    def setAction(self,name,ico=None):
        if ico != None:
            action = QAction(QIcon("resource/" + ico),name,self)
        else:
            action = QAction(name,self)
        self.allActions[name] = action
        return action

    def getAction(self,name):
        return self.allActions[name]

    def freezeActions(self,list):
        for (name,action) in self.allActions.items():
            if name in list:
                action.setDisabled(True)

    def activateActions(self,list):
        for (name,action) in self.allActions.items():
            if name in list:
                action.setEnabled(True)

    def setBarActions(self,bar,list):
        bar.clear()
        for name in list:
            if name == "|":
                bar.addSeparator()
            else:
                bar.addAction(self.getAction(name))

    def setMenu(self,config):
        menu = QMenu(config['name'],self)
        if "icon" in config:
            menu.setIcon(QIcon('resource/'+config["icon"]))
        for obj in config['actions']:
            if isinstance(obj,tuple):
                menu.addAction(self.setAction(*obj))
            elif isinstance(obj,dict):
                menu.addMenu(self.setMenu(obj))
            elif obj == "|":
                menu.addSeparator()
            elif isinstance(obj,str):
                menu.addAction(self.setAction(obj))
        self.allMenus[config['name']] = menu
        return menu

    def prompt(self,text,msg='information'):
        if msg == 'critical':
            return QMessageBox.critical(self,self.tr("Critical"),self.tr(text),QMessageBox.Yes | QMessageBox.No)
        elif msg == 'warnning':
            return QMessageBox.warning(self,self.tr("Warning"),self.tr(text),QMessageBox.Yes | QMessageBox.No)
        else:
            return QMessageBox.information(self,self.tr("Information"),self.tr(text),QMessageBox.Yes | QMessageBox.No)

    def information(self,text):
        return QMessageBox.information(self,self.tr("Information"),self.tr(text),QMessageBox.Yes)
        
    def critical(self,text):
        return QMessageBox.critical(self,self.tr("Critical"),self.tr(text),QMessageBox.Yes)

    def warnning(self,text):
        return QMessageBox.warning(self,self.tr("Warning"),self.tr(text),QMessageBox.Yes)

    def setSetting(self,key,value):
        self.settings.setValue(key,value)
        self.settings.sync()

    def getSetting(self,key,default):
        value = self.settings.value(key)
        if value == None or value == '':
            self.settings.setValue(key,default)
            self.settings.sync()
            return default
        return value

    def exportDataFile(self,data,ext="Text File (*.txt)"):
        (Name,Type) = QFileDialog.getSaveFileName(
            self,self.tr("Save File"),
            self.getSetting("File/lastFilePath",self.defaultDir),
            ext,ext
        )
        if Name == '':
            return
        fileName = API.formatPath(Name)
        self.setSetting('File/lastFilePath',os.path.dirname(fileName))
        open(fileName,'w+').write(data())
        self.information('Export successful!')

    def LangMenu(self):
        def changeLang(lang):
            def func():
                if lang == self.getSetting("UI/Language","English"):
                    return
                self.setSetting('UI/Language',lang)
                if self.warnning("Do you want to restart the program to implement language switch?"):
                    self.tray.hide()
                    exe = os.sys.argv[0]
                    os.execl(exe, exe, *sys.argv[1:])
            return func
        menu = QMenu(self)
        for lang in self.languages:
            action = self.setAction(lang)
            action.triggered.connect(changeLang(lang))
            menu.addAction(action)
        self.allMenus['&Language'] = menu
        return menu

    def ThemeMenu(self):
        def useTheme(style):
            def func():
                QApplication.setStyle(QStyleFactory.create(style))
                QApplication.setPalette(QApplication.style().standardPalette())
                self.setSetting('UI/Theme',style)
            return func
        themes = QStyleFactory.keys()
        menu = QMenu(self)
        for theme in themes:
            action = self.setAction(theme.capitalize())
            action.triggered.connect(useTheme(theme))
            menu.addAction(action)
        useTheme(self.getSetting('UI/Theme',themes[-1]))()
        self.allMenus['&Theme'] = menu
        return menu

    def importDataFile(self,fn):
        (Name,Type) = QFileDialog.getOpenFileName(
            self,self.tr('Open'),
            self.getSetting("File/lastFilePath",self.defaultDir),
            ";;".join(self.extensions),
            self.extensions[0]
        )
        if Name == '':
            return
        fileName = API.formatPath(Name)
        self.setSetting('File/lastFilePath',os.path.dirname(fileName))
        try:
            fn(fileName)
        except Exception as identify:
            print(identify)
            self.critical('Invalid Data File!')


    def tr(self,text):
        if text in self.langText:
            return self.langText[text]
        return text

    def useLanguage(self,lang):
        self.langText = {}
        try:
            self.langText = json.load(open(os.path.join(self.langDir, '%s.lang' % lang),encoding='utf-8'))
        except:
            pass

    def translateUI(self):
        _ = self.tr
        for name in self.allActions:
            self.getAction(name).setText(_(name))
        for name in self.allMenus:
            self.allMenus[name].setTitle(_(name))
