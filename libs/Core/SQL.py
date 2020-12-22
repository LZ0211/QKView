from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery
from time import time

def like_compile(str,cols):
    str = str.replace("/", "\\/")
    str = str.replace("'", "''")
    str = str.replace("[", "\\[")
    str = str.replace("]", "\\]")
    str = str.replace("%", "\\%")
    str = str.replace("&","\\&")
    str = str.replace("_", "\\_")
    str = str.replace("(", "\\(")
    str = str.replace(")", "\\)")
    return ' OR '.join(map(lambda col:col+" LIKE '%{str}%'".format(str=str),cols))

class MoleculeDataBase(object):
    index_conflict_scheme = "IGNORE"# REPLACE IGNORE FAIL ABORT ROLLBACK
    index_table = '''CREATE TABLE IF NOT EXISTS molecule_index
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    smiles VARCHAR(512) NOT NULL UNIQUE,
    formular VARCHAR(255) NOT NULL,
    mass REAL NOT NULL,
    charge INTEGER NOT NULL,
    cas VARCHAR(255),
    name VARCHAR(255),
    code VARCHAR(255),
    alias VARCHAR(255),
    tags VARCHAR(255),
    image TEXT,
    note TEXT,
    mol TEXT,
    xyz TEXT,
    date_add REAL,
    date_modify REAL
);'''
    index_cols_add = ['uuid', 'smiles', 'formular', 'mass', 'charge', 'cas', 'name', 'code', 'alias', 'tags', 'image', 'note', 'mol', 'xyz', 'date_add', 'date_modify']
    index_cols_update = ['formular', 'cas', 'name', 'code', 'alias', 'tags', 'image', 'note', 'mol', 'xyz', 'date_modify']
    index_cols_query = ['uuid', 'smiles', 'formular', 'mass', 'charge', 'cas', 'name', 'code', 'alias', 'tags', 'image', 'note', 'mol', 'xyz', 'date_add', 'date_modify']

    summary_table = '''CREATE TABLE IF NOT EXISTS summary
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    geometry TEXT,
    charge INTEGER,
    spin INTEGER,
    homo REAL,
    lumo REAL,
    hf REAL,
    cor_zpe REAL,
    cor_energy REAL,
    cor_enthalpy REAL,
    cor_gibbs REAL
)'''
    summary_cols = ['uuid','geometry','charge','spin','homo','lumo','hf','cor_zpe','cor_energy','cor_enthalpy','cor_gibbs']

    spectrum_table = '''CREATE TABLE IF NOT EXISTS spectrum
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    ir TEXT,
    raman TEXT,
    uv TEXT,
    nmr TEXT,
    ecd TEXT,
    vcd TEXT
)'''
    spectrum_cols = ['ir','raman','uv','nmr','ecd','vcd']

    charge_table = '''CREATE TABLE IF NOT EXISTS atomic_charge
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    mulliken TEXT,
    adch TEXT,
    cm5 TEXT,
    resp TEXT
)'''

    charge_cols = ['uuid','mulliken','adch','cm5','resp']

    bo_table = '''CREATE TABLE IF NOT EXISTS bond_order
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    mulliken TEXT,
    mayer TEXT,
    laplacian TEXT,
    fuzzy TEXT
)'''
    bo_cols = ['uuid','mulliken','mayer','laplacian','fuzzy']

    summery_table = '''CREATE TABLE IF NOT EXISTS qc_summary
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    mulliken TEXT,
    mayer TEXT,
    laplacian TEXT,
    fuzzy TEXT
)
'''

    surface_table = '''CREATE TABLE IF NOT EXISTS surface
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    volume REAL,
    density REAL,
    minimal REAL,
    maximal REAL,
    total_area REAL,
    positive_area REAL,
    negative_area REAL,
    total_avg REAL,
    positive_avg REAL,
    negative_avg REAL,
    total_var REAL,
    positive_var REAL,
    negative_var REAL,
    sigma_product REAL,
    charge_balance REAL,
    mpi REAL,
    polar_area REAL,
    nonpolar_area REAL,
    pi REAL
)'''
    surface_cols = ['uuid','volume','density','minimal','maximal','total_area','positive_area','negative_area','total_avg','positive_avg','negative_avg','total_var','positive_var','negative_var','sigma_product','charge_balance','mpi','polar_area','nonpolar_area','pi']

    cdft_table = '''CREATE TABLE IF NOT EXISTS conceptual_dft
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    vertical_ip REAL,
    vertical_ea REAL,
    electro_negativity REAL,
    chemical_potential REAL,
    softness REAL,
    hardness REAL,
    electr_index REAL,
    nucle_index REAL,
    f_plus TEXT,
    f_minus TEXT,
    f_zero TEXT,
    cdd TEXT,
    condensed_electr_index TEXT,
    condensed_nucle_index TEXT,
    condensed_softness TEXT
)'''
    cdft_cols = ['uuid','vertical_ip','vertical_ea','electro_negativity','chemical_potential','softnes','hardness','electr_index','nucle_index','f_plus','f_minus','f_zero','cdd','condensed_electr_index','condensed_nucle_index','condensed_softness']

    physic_table = '''CREATE TABLE IF NOT EXISTS physical_prop
(
    uuid CHARACTER(36) PRIMARY KEY UNIQUE,
    density REAL,
    melting REAL,
    boiling REAL,
    vapor REAL,
    vapor_temp REAL,
    dielectric REAL,
    flash REAL,
    viscosity REAL,
    vis_temp REAL,
    vis_const_1 REAL,
    vis_const_2 REAL,
    vis_const_3 REAL,
    surf_tension REAL,
    re_potential REAL,
    ox_potential REAL
)'''
    physic_cols = ['uuid','density','melting','boiling','vapor','vapor_temp','dielectric','flash','viscosity','vis_temp','vis_const_1','vis_const_2','vis_const_3','surf_tension','re_potential','ox_potential']

    def __init__(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('molecule.db')
        self.db.open()
        self.index_init()

    def query_sql(self,sql):
        res = []
        q = QSqlQuery()
        found = q.exec_(sql)
        if found:
            idx = {}
            record = q.record()
            count = record.count()
            keys = list(map(lambda idx:record.fieldName(idx),range(count)))
            while q.next():
                data = {}
                for idx in range(count):
                    data[keys[idx]] = q.value(idx)
                res.append(data)
        return res

    def index_init(self):
        q = QSqlQuery()
        q.exec_(self.index_table)

    def index_add(self,molecule):
        if molecule == None:
            return False
        q = QSqlQuery()
        molecule['date_add'] = molecule['date_modify'] = time()
        sql_code = "INSERT OR {scheme} INTO molecule_index ({keys}) VALUES (:{values});".format(
            scheme = self.index_conflict_scheme,
            keys = ', '.join(self.index_cols_add),
            values = ', :'.join(self.index_cols_add)
        )
        q.prepare(sql_code)
        for key in self.index_cols_add:
            q.bindValue(":%s" % key, molecule[key])
        q.exec_()

    def index_update(self,molecule):
        if molecule == None:
            return False
        q = QSqlQuery()
        molecule['date_modify'] = time()
        sql_code = "UPDATE molecule_index SET {key_val} WHERE uuid=:uuid".format(
            key_val = ', '.join(map(lambda k:'%s=:%s' % (k,k),self.index_cols_update))
        )
        q.prepare(sql_code)
        q.bindValue(":uuid",molecule["uuid"])
        for key in self.index_cols_update:
            val = molecule[key]
            if isinstance(val,str) and val == "":
                continue
            q.bindValue(":%s" % key, val)
        q.exec_()

    def index_del(self,uuid):
        if uuid == None or uuid == "":
            return
        q = QSqlQuery()
        sql_code = 'DELETE FROM molecule_index WHERE uuid=:uuid'
        q.prepare(sql_code)
        q.bindValue(":uuid",uuid)
        q.exec_()
        
    def index_query_all(self):
        return self.query_sql('SELECT * FROM molecule_index')

    def index_query(self,key,val):
        if key == None or val == None or val == "":
            return self.index_query_all()
        res = []
        q = QSqlQuery()
        q.prepare('SELECT * FROM molecule_index WHERE %s=?' % key)
        q.addBindValue(val)
        found = q.exec_()
        if found:
            idx = {}
            record = q.record()
            for key in self.index_cols_query:
                idx[key] = record.indexOf(key)
            while q.next():
                data = {}
                for key in self.index_cols_query:
                    data[key] = q.value(idx[key])
                res.append(data)
        return res

    def index_query_smi(self,smi):
        return self.index_query('smiles',smi)

    def index_query_id(self,id):
        return self.index_query('uuid',id)

    def index_query_name(self,name):
        return self.index_query('name',name)

    def index_query_code(self,code):
        return self.index_query('code',code)

    def index_query_formular(self,formular):
        return self.index_query('formular',formular)

    def index_search(self,str,cols=None):
        if str == None:
            return self.index_query_all()
        keys = str.split()
        if len(keys) == 0:
            return self.index_query_all()
        if cols == None:
            cols = ['name','formular','cas','code','alias','note','tags']
        rule = ') AND ('.join(map(lambda key:like_compile(key,cols),keys))
        sql_code = "SELECT * FROM molecule_index WHERE ({rule})".format(rule=rule)
        return self.query_sql(sql_code)

    def index_search_tags(self,str):
        return self.index_search(str,['tags'])

    def index_search_note(self,str):
        return self.index_search(str,['note'])

    def index_search_name(self,str):
        return self.index_search(str,['name'])

    def index_search_code(self,str):
        return self.index_search(str,['code'])

    def index_search_alias(self,str):
        return self.index_search(str,['alias'])

    def index_search_formular(self,str):
        return self.index_search(str,['formular'])

    def index_search_cas(self,str):
        return self.index_search(str,['cas'])

    def general_add(self,table,info):
        if table == None or info == None:
            return
        keys = list(info.keys())
        sql_code = "INSERT OR REPLACE INTO {table} ({keys}) VALUES (:{values});".format(
            table = table,
            keys = ', '.join(keys),
            values = ', :'.join(keys)
        )
        q = QSqlQuery()
        q.prepare(sql_code)
        for key in keys:
            q.bindValue(":%s" % key, info[key])
        q.exec_()

    def general_update(self,table,info):
        if table == None or info == None:
            return
        keys = list(info.keys())
        sql_code = "UPDATE {table} SET {key_val} WHERE uuid=:uuid;".format(
            table = table,
            key_val = ', '.join(map(lambda k:'%s=:%s' % (key,key),keys))
        )
        q = QSqlQuery()
        q.prepare(sql_code)
        for key in keys:
            q.bindValue(":%s" % key, info[key])
        q.exec_()

    def general_del(self,table,uuid):
        if table == None or uuid == None:
            return
        sql_code = "DELETE FROM {table} WHERE uuid='{uuid}'".format(
            table = table,
            uuid = uuid
        )
        q = QSqlQuery()
        q.exec_(sql_code)

    def general_query(self,table,uuid):
        if table == None or uuid == None:
            return []
        sql_code = "SELECT FROM {table} WHERE uuid='{uuid}'".format(
            table = table,
            uuid = uuid
        )
        return self.query_sql(sql_code)
        
    def summary_init(self):
        q = QSqlQuery()
        q.exec_(self.summary_table)

    def summary_add(self,info):
        return self.general_add('summary',info)

    def summary_update(self,info):
        return self.general_update('summary',info)

    def summary_del(self,uuid):
        return self.general_del('summary',uuid)

    def summary_query(self,uuid):
        pass

    def charge_init(self):
        pass
