from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery

class MoleculeIndex(object):
    def __init__(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('index.db')
        self.db.open()
        self.init_table()
    def init_table(self):
        q = QSqlQuery()
        sql_code = '''CREATE TABLE IF NOT EXISTS molecule_index
(
    uuid CHARACTER(36) PRIMARY KEY,
    smiles VARCHAR(512),
    cas VARCHAR(255),
    name VARCHAR(255),
    formular VARCHAR(255),
    mass REAL,
    code VARCHAR(255),
    alias VARCHAR(255),
    tags VARCHAR(255)
);'''
        q.exec_(sql_code)

    def addRecord(self,molecule):
        q = QSqlQuery()
        sql_code = 'insert into molecule_index values(1, "name", 15)'
        q.exec_(sql_code)

    def search(self):
        pass

    def queryBySmi(self,smi):
        pass

    def queryById(self,smi):
        pass

    def queryByName(self,name):
        pass

    def queryByCode(self,code):
        pass

    def queryByFormular(self,formular):
        pass

class MoleculeCharge(object):
    def __init__(self):
        pass