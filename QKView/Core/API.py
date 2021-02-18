import requests
import json,base64,re,os,platform,urllib,math
import datetime
import time
from random import randint
from urllib import parse
from uuid import uuid3,uuid4
from uuid import UUID

NAMESPACE = UUID('63e816118377ae5a4387d7b18820752a')
reg_braket = re.compile(r'^\{\s*(\w+)\s*\}$')
reg_double_braket = re.compile(r'^\{\{\s*(\S+)\s*\}\}$')

FTP = 'ftp://172.16.11.164:21'
HOST = 'http://172.16.11.164'
PUBCHEM_HOST = 'https://pubchem.ncbi.nlm.nih.gov'

JSON_HEADERS = {'Content-Type': 'application/json'}

TIMEOUT = 5

SketcherURL = HOST + "/static/sketcher/"
IndrawURL = HOST + "/static/indraw/index.html"
_3DMOLURL = HOST + "/static/3dmol/" + "?t=" + str(time.time())
_3DViewURL = HOST + "/static/3dview/"

def mol2can(mol):
    url = HOST + '/job/submit/obabel/mol2can'
    data = {'mol': mol}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    smi = json.loads(res.text)["data"]
    return smi

def mol2xyz(mol):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'mol',
        'out':'xyz',
        'data':mol,
        'other':'--gen3d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    xyz = json.loads(res.text)["data"]
    return xyz

def mol2pdb(mol):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'mol',
        'out':'pdb',
        'data':mol,
        'other':'--gen3d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    pdb = json.loads(res.text)["data"]
    return pdb

def mol2smi(mol):
    url = HOST + 'job/submit/obabel/mol2can'
    data = {"mol":mol}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    return json.loads(res.text)["data"]

def mol2png(mol):
    url = HOST + '/job/submit/obabel/mol2png'
    data = {'mol':mol}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    str = json.loads(res.text)["data"]
    return str

def mol2mol2D(mol):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'mol',
        'out':'mol',
        'data':mol,
        'other':'--gen2d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def pdb2can(pdb):
    url = HOST + '/job/submit/obabel/pdb2can'
    res = requests.post(url,json={'pdb': pdb},headers=JSON_HEADERS, timeout=TIMEOUT)
    smi = json.loads(res.text)["data"]
    return smi

def pdb2mol(pdb):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'pdb',
        'out':'mol',
        'data':pdb
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def pdb2xyz(pdb):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'pdb',
        'out':'xyz',
        'data':pdb
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    xyz = json.loads(res.text)["data"]
    return xyz

def pdb2smi(pdb):
    url = HOST + 'job/submit/obabel/pdb2can'
    data = {"pdb":pdb}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    return json.loads(res.text)["data"]

def pdb2png(pdb):
    url = HOST + '/job/submit/obabel/pdb2png'
    data = {'pdb':pdb}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    str = json.loads(res.text)["data"]
    return str

def pdb2mol2D(pdb):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'pdb',
        'out':'mol',
        'data':pdb,
        'other':'--gen2d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def xyz2can(xyz):
    url = HOST + '/job/submit/obabel/xyz2can'
    res = requests.post(url,json={'xyz': xyz},headers=JSON_HEADERS, timeout=TIMEOUT)
    smi = json.loads(res.text)["data"]
    return smi

def xyz2mol(xyz):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'xyz',
        'out':'mol',
        'data':xyz
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def xyz2pdb(xyz):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'xyz',
        'out':'pdb',
        'data':xyz
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    pdb = json.loads(res.text)["data"]
    return pdb

def xyz2smi(xyz):
    url = HOST + 'job/submit/obabel/xyz2can'
    data = {"xyz":xyz}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    return json.loads(res.text)["data"]

def xyz2png(xyz):
    url = HOST + '/job/submit/obabel/xyz2png'
    data = {'xyz':xyz}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    str = json.loads(res.text)["data"]
    return str

def xyz2mol2D(xyz):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'xyz',
        'out':'mol',
        'data':xyz,
        'other':'--gen2d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def smi2mol2D1(smi):
    url = 'http://121.42.137.238/chemmol/src/server/smiToMol.php?smiles='+parse.quote(smi)
    res = requests.get(url,timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]["mol"]
    return mol

def smi2mol2D2(smi):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'smi',
        'out':'mol',
        'data':smi,
        'other':'--gen2d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def smi2mol(smi):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'smi',
        'out':'mol',
        'data':smi,
        'other':'--gen3d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def smi2xyz(smi):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'smi',
        'out':'xyz',
        'data':smi,
        'other':'--gen3d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    xyz = json.loads(res.text)["data"]
    return xyz

def smi2pdb(smi):
    url = HOST + '/job/submit/obabel/convert'
    data = {
        'inp': 'smi',
        'out':'pdb',
        'data':smi,
        'other':'--gen3d'
    }
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    pdb = json.loads(res.text)["data"]
    return pdb

def smi2png(smi):
    url = HOST + '/job/submit/obabel/smi2png'
    data = {'smi':smi}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    str = json.loads(res.text)["data"]
    return str

def base64ToImage(string):
    arr = string.split(';base64,')
    if len(arr) == 2:
        string = arr[1]
    return base64.b64decode(string)

Periodic_Table={
    #No. Symbol, Mass, Electronegativity, Orbits, Radius, UFF_radius
    "Ghost":(0,"Ghost",1,None,(()),0.3,0.4),

    "H":(1,"H",1.008,2.20,((1)),1.2,1.443),
    "He":(2,"He",4.0026,None,((2)),1.4,1.181),

    "Li":(3,"Li",6.94,0.98,((2),(1)),1.82,1.2255),
    "Be":(4,"Be",9.0122,1.57,((2),(2)),1.77,1.3725),
    "B":(5,"B",10.81,2.04,((2),(2,1)),1.74,2.0415),
    "C":(6,"C",12.011,2.55,((2),(2,2)),1.70,1.9255),
    "N":(7,"N",14.007,3.04,((2),(2,3)),1.55,1.83),
    "O":(8,"O",15.999,3.44,((2),(2,4)),1.52,1.75),
    "F":(9,"F",18.998,3.90,((2),(2,5)),1.47,1.682),
    "Ne":(10,"Ne",20.18,None,((2),(2,6)),1.54,1.6215),

    "Na":(11,"Na",22.99,0.93,((2),(2,6),(1)),2.27,1.4915),
    "Mg":(12,"Mg",24.305,1.31,((2),(2,6),(2)),1.73,1.5105),
    "Al":(13,"Al",26.982,1.61,((2),(2,6),(2,1)),1.73,2.2495),
    "Si":(14,"Si",28.085,1.90,((2),(2,6),(2,2)),2.10,2.1475),
    "P":(15,"P",30.974,2.19,((2),(2,6),(2,3)),1.80,2.0735),
    "S":(16,"S",32.06,2.58,((2),(2,6),(2,4)),1.80,2.0175),
    "Cl":(17,"Cl",35.45,3.16,((2),(2,6),(2,5)),1.75,1.9735),
    "Ar":(18,"Ar",39.95,None,((2),(2,6),(2,6)),1.88,1.934),

    "K":(19,"K",39.098,0.82,((2),(2,6),(2,6),(1)),2.00,1.906),
    "Ca":(20,"Ca",40.078,1.00,((2),(2,6),(2,6),(2)),2.00,1.6995),
    "Sc":(21,"Sc",44.956,1.36,((2),(2,6),(2,6,1),(2)),2.00,1.6475),
    "Ti":(22,"Ti",47.867,1.54,((2),(2,6),(2,6,2),(2)),2.00,1.5875),
    "V":(23,"V",50.942,1.63,((2),(2,6),(2,6,3),(2)),2.00,1.572),
    "Cr":(24,"Cr",51.996,1.66,((2),(2,6),(2,6,5),(1)),2.00,1.5115),
    "Mn":(25,"Mn",54.938,1.55,((2),(2,6),(2,6,5),(2)),2.00,1.4805),
    "Fe":(26,"Fe",55.845,1.83,((2),(2,6),(2,6,6),(2)),2.00,1.456),
    "Co":(27,"Co",58.933,1.88,((2),(2,6),(2,6,7),(2)),2.00,1.436),
    "Ni":(28,"Ni",58.693,1.91,((2),(2,6),(2,6,8),(2)),1.63,1.417),
    "Cu":(29,"Cu",63.546,1.90,((2),(2,6),(2,6,10),(1)),1.40,1.7475),
    "Zn":(30,"Zn",65.38,1.65,((2),(2,6),(2,6,10),(2)),1.39,1.3815),
    "Ga":(31,"Ga",69.723,1.81,((2),(2,6),(2,6,10),(2,1)),1.87,2.1915),
    "Ge":(32,"Ge",72.63,2.01,((2),(2,6),(2,6,10),(2,2)),2.00,2.14),
    "As":(33,"As",74.922,2.18,((2),(2,6),(2,6,10),(2,3)),1.85,2.115),
    "Se":(34,"Se",78.971,2.55,((2),(2,6),(2,6,10),(2,4)),1.90,2.1025),
    "Br":(35,"Br",79.901,2.96,((2),(2,6),(2,6,10),(2,5)),1.85,2.0945),
    "Kr":(36,"Kr",83.798,None,((2),(2,6),(2,6,10),(2,6)),2.02,2.0705),

    "Rb":(37,"Rb",85.468,0.82,((2),(2,6),(2,6,10),(2,6),(1)),2.00,2.057),
    "Sr":(38,"Sr",87.62,0.95,((2),(2,6),(2,6,10),(2,6),(2)),2.00,1.8205),
    "Y":(39,"Y",88.906,1.22,((2),(2,6),(2,6,10),(2,6,1),(2)),2.00,1.6725),
    "Zr":(40,"Zr",91.224,1.33,((2),(2,6),(2,6,10),(2,6,2),(2)),2.00,1.562),
    "Nb":(41,"Nb",92.906,1.60,((2),(2,6),(2,6,10),(2,6,3),(2)),2.00,1.5825),
    "Mo":(42,"Mo",95.95,2.16,((2),(2,6),(2,6,10),(2,6,5),(1)),2.00,1.526),
    "Tc":(43,"Tc",98,2.10,((2),(2,6),(2,6,10),(2,6,5),(2)),2.00,1.499),
    "Ru":(44,"Ru",101.07,2.20,((2),(2,6),(2,6,10),(2,6,7),(1)),2.00,1.4815),
    "Rh":(45,"Rh",102.91,2.28,((2),(2,6),(2,6,10),(2,6,8),(1)),2.00,1.4645),
    "Pd":(46,"Pd",106.42,2.20,((2),(2,6),(2,6,10),(2,6,10)),1.63,1.4495),
    "Ag":(47,"Ag",107.87,1.93,((2),(2,6),(2,6,10),(2,6,10),(1)),1.72,1.574),
    "Cd":(48,"Cd",112.41,1.69,((2),(2,6),(2,6,10),(2,6,10),(2)),1.58,1.424),
    "In":(49,"In",114.82,1.78,((2),(2,6),(2,6,10),(2,6,10),(2,1)),1.93,2.2315),
    "Sn":(50,"Sn",118.71,1.96,((2),(2,6),(2,6,10),(2,6,10),(2,2)),2.17,2.196),
    "Sb":(51,"Sb",121.76,2.05,((2),(2,6),(2,6,10),(2,6,10),(2,3)),2.00,2.21),
    "Te":(52,"Te",127.6,2.10,((2),(2,6),(2,6,10),(2,6,10),(2,4)),2.06,2.235),
    "I":(53,"I",126.9,2.66,((2),(2,6),(2,6,10),(2,6,10),(2,5)),1.98,2.25),
    "Xe":(54,"Xe",131.29,None,((2),(2,6),(2,6,10),(2,6,10),(2,6)),2.16,2.202),

    "Cs":(55,"Cs",132.91,0.79,((2),(2,6),(2,6,10),(2,6,10),(2,6),(1)),2.00,2.2585),
    "Ba":(56,"Ba",137.33,0.89,((2),(2,6),(2,6,10),(2,6,10),(2,6),(2)),2.00,1.8515),
    "La":(57,"La",138.91,1.10,((2),(2,6),(2,6,10),(2,6,10),(2,6,1),(2)),2.00,1.761),
    "Ce":(58,"Ce",140.12,1.12,((2),(2,6),(2,6,10),(2,6,10),(2,6),(1),(1),(2)),2.00,1.778),
    "Pr":(59,"Pr",140.91,1.13,((2),(2,6),(2,6,10),(2,6,10),(2,6),(3),(2)),2.00,1.803),
    "Nd":(60,"Nd",144.24,1.14,((2),(2,6),(2,6,10),(2,6,10),(2,6),(4),(2)),2.00,1.7875),
    "Pm":(61,"Pm",145,1.15,((2),(2,6),(2,6,10),(2,6,10),(2,6),(5),(2)),2.00,1.7735),
    "Sm":(62,"Sm",150.36,1.17,((2),(2,6),(2,6,10),(2,6,10),(2,6),(6),(2)),2.00,1.76),
    "Eu":(63,"Eu",151.96,1.18,((2),(2,6),(2,6,10),(2,6,10),(2,6),(7),(2)),2.00,1.7465),
    "Gd":(64,"Gd",157.25,1.20,((2),(2,6),(2,6,10),(2,6,10),(2,6),(7),(1),(2)),2.00,1.684),
    "Tb":(65,"Tb",158.93,1.21,((2),(2,6),(2,6,10),(2,6,10),(2,6),(9),(2)),2.00,1.7255),
    "Dy":(66,"Dy",162.5,1.22,((2),(2,6),(2,6,10),(2,6,10),(2,6),(10),(2)),2.00,1.714),
    "Ho":(67,"Ho",164.93,1.23,((2),(2,6),(2,6,10),(2,6,10),(2,6),(11),(2)),2.00,1.7045),
    "Er":(68,"Er",167.26,1.24,((2),(2,6),(2,6,10),(2,6,10),(2,6),(12),(2)),2.00,1.6955),
    "Tm":(69,"Tm",168.93,1.25,((2),(2,6),(2,6,10),(2,6,10),(2,6),(13),(2)),2.00,1.687),
    "Yb":(70,"Yb",173.05,1.26,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(2)),2.00,1.6775),
    "Lu":(71,"Lu",174.97,1.0,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(1),(2)),2.00,1.82),
    "Hf":(72,"Hf",178.49,1.3,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(2),(2)),2.00,1.5705),
    "Ta":(73,"Ta",180.95,1.5,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(3),(2)),2.00,1.585),
    "W":(74,"W",183.84,1.7,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(4),(2)),2.00,1.5345),
    "Re":(75,"Re",186.21,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(5),(2)),2.00,1.477),
    "Os":(76,"Os",190.23,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(6),(2)),2.00,1.56),
    "Ir":(77,"Ir",192.22,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(7),(2)),2.00,1.42),
    "Pt":(78,"Pt",195.08,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(9),(1)),1.72,1.377),
    "Au":(79,"Au",196.97,2.4,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(1)),1.66,1.6465),
    "Hg":(80,"Hg",200.59,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2)),1.55,1.3525),
    "Tl":(81,"Tl",204.38,1.8,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,1)),1.96,2.1735),
    "Pb":(82,"Pb",207.2,1.8,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,2)),2.02,2.1485),
    "Bi":(83,"Bi",208.98,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,3)),2.00,2.185),
    "Po":(84,"Po",209,2.0,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,4)),2.00,2.3545),
    "At":(85,"At",210,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,5)),2.00,2.375),
    "Rn":(86,"Rn",222,None,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,2)),2.00,2.3825)
}

Organic_Elements = ['B','Si','C','H','O','N','P','S','F','Cl','Br','I']
Metal_Elements = ['Li','Be','Na','Mg','Al','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn']

Element_Patterm = re.compile(r'([A-Z][a-z]?)(\d*)')
def calcAtomList(xyz):
    lines = xyz.split('\n')
    count = int(lines[0])
    atoms = []
    for line in lines[2:2+count]:
        symbol = line.split()[0]
        atoms.append(symbol)
    return atoms

def calcFormularMass(formular):
    elements = Element_Patterm.findall(formular)
    sum = 0
    for pair in elements:
        k,v = tuple(pair)
        sum += Periodic_Table[k][2] * int(v or 1)
    return sum

def calcFormular(atoms):
    records = {}
    for symbol in atoms:
        if symbol in records:
            records[symbol] += 1
        else:
            records[symbol] = 1
    elements = list(records.keys())
    for element in elements:
        if not element in Organic_Elements:
            elements.sort(key=lambda x:Periodic_Table[x][3])
            return "".join(map(lambda k:k+str(records[k] if records[k] > 1 else ""),elements))
    elements.sort(key=lambda x:Organic_Elements.index(x))
    formular = "".join(map(lambda k:k+str(records[k] if records[k] > 1 else ""),elements))
    special = {#无机物
        "H3N":"NH3",
        "H3P":"PH3",
        "CH2O3":"H2CO3",
        "H2O4S":"H2SO4",
        "HO3N":"HNO3",
        "H3O4P":"H3PO4",
        "BH3O3":"H3BO3",
        "SiH4O4":"H4SiO4",
    }
    if formular in special:
        return special[formular]
    return formular   

def calcXYZMass(xyz):
    return calcFormularMass(calcFormular(xyz))

def download(url,file):
    res = requests.get(url, stream=True)
    with open(file, "wb") as hander:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                hander.write(chunk)
    
def getLanguages(dirname):
    files = os.listdir(dirname)
    langs = filter(lambda file:os.path.splitext(file)[1]==".lang",files)
    return list(map(lambda file:os.path.splitext(file)[0],langs))

SYSTEM = platform.system()
PATH_SEG = '\\' if SYSTEM == 'Windows' else '/'

def formatPath(path):
    return path.replace('/','\\').replace('\\',PATH_SEG)

PubChem_Properties = ['MolecularFormula','MolecularWeight','InChI','InChIKey','IUPACName','XLogP','TPSA','Charge','Volume3D']
def searchPubchem(smi):
    properties = ",".join(PubChem_Properties)
    smiles = parse.quote(smi)
    res = requests.get('%s/rest/pug/compound/smiles/%s/property/%s/json' % (PUBCHEM_HOST,smiles,properties))
    dict = json.loads(res.text)["PropertyTable"]["Properties"][0]
    dict["CAS"] = ""
    #搜索CAS号
    res = requests.get('%s/rest/pug/compound/smiles/%s/synonyms/txt' % (PUBCHEM_HOST,smiles))
    reg = re.compile(r'\d{2,7}-\d{2}-\d')
    found = reg.findall(res.text)
    if len(found) >= 1:
        #found.sort(key=lambda x:len(x))
        dict["CAS"] = found[0]
    return dict

def md5(string):
    return str(uuid3(NAMESPACE,string))

def smi2chg(smi):
    return len(smi.split('+')) - len(smi.split('-'))

def pubChemURI(smi):
    try:
        res = requests.get('%s/rest/pug/compound/smiles/cids/json?smiles=%s' % (PUBCHEM_HOST,parse.quote(smi)))
        data = json.loads(res.text)
        cid = data['IdentifierList']['CID'][0]
        return '%s/compound/%s' % (PUBCHEM_HOST,cid)
    except:
        return PUBCHEM_HOST

def getKey(dict,key):
    if key in dict and dict[key] != "":
        return dict[key]
    return None

def hashReplace(hash,dict):
    for key in dict:
        if key in hash:
            val = hash[key]
            del hash[key]
            hash[dict[key]] = val
    return hash
validFiles = ["log","out","gjf","fchk","chg","txt","bo","cube","cub","wfn","pdb","xyz","mol"]
invalidFiles = ["Fukui.fchk"]
def getFiles(uuid):
    res = requests.get('{host}/files/{uuid}/gauss'.format(host=HOST,uuid=uuid))
    text = res.text
    array = text.strip().split("\n")
    files = []
    for line in array:
        arr = line.split()
        if arr[0] == "<a":
            filename = re.match(r'href="(.*)?"',arr[1]).group(1)
            filename = urllib.parse.unquote(filename)
            #%d-%m-%Y %H:%M
            time = datetime.datetime.strptime(arr[2] + " " +arr[3], "%d-%b-%Y %H:%M")
            time = datetime.datetime.strftime(time, '%Y/%m/%d %H:%M:%S')
            size = arr[4]
            types = filename.split(".")[-1].lower()
            if types in validFiles and not filename in invalidFiles:
                files.append([filename,size,types,time])
    return files

def downloadFile(uuid,file):
    dir = os.path.dirname(file)
    if not os.path.exists(dir):
        os.makedirs(dir)
    res = requests.get("{host}/files/{uuid}/gauss/{file}".format(host=HOST,uuid=uuid,file=os.path.basename(file)))
    f = open(file,'wb+')
    f.write(res.content)
    f.close()

#print(getFiles("28895e8a-02ab-3149-a3e6-78d0b4dd304f"))

def read_job_status(id):
    res = requests.get('{host}/job/status?id={id}'.format(host=HOST,id=id))
    return json.loads(res.text)['data']

def read_gauss_status(name,job):
    res = requests.post('{host}/job/search/gauss/{job}'.format(host=HOST,job=job),
        json={'name':name}
    )
    return json.loads(res.text)['data']

def read_mwfn_status(name,job):
    res = requests.post('{host}/job/search/mwfn/{job}'.format(host=HOST,job=job),
        json={'name':name}
    )
    return json.loads(res.text)['data']

def read_xtb_status(name,job):
    res = requests.post('{host}/job/search/xtb/{job}'.format(host=HOST,job=job),
        json={'name':name}
    )
    return json.loads(res.text)['data']

def read_gauss_data(name,job,info='summary'):
    res = requests.post('{host}/job/data/gauss/{job}'.format(host=HOST,job=job),
        json={
            'name':name,
            'info':info
        }
    )
    return json.loads(res.text)['data']

def read_mwfn_data(name,job):
    res = requests.post('{host}/job/data/mwfn/{job}'.format(host=HOST,job=job),
        json={'name':name}
    )
    return json.loads(res.text)['data']

def read_xtb_data(name,job):
    res = requests.post('{host}/job/data/xtb/{job}'.format(host=HOST,job=job),
        json={'name':name}
    )
    return json.loads(res.text)['data']


def geom2xyz(geom):
    xyz = '%s\nOptimized Molecule Structure\n' % len(geom)
    for line in geom:
        xyz += " {symbol:>2s} {x:>-15.8f} {y:>-15.8f} {z:>-15.8f}\n".format(symbol=line[0],x=line[1],y=line[2],z=line[3])
    return xyz

def normalize(array):
    return math.sqrt(sum(map(lambda x:x*x,array)))

ENERGY_Hartree = 1.00
ENERGY_eV = 27.211399
ENERGY_kJ = 2625.5002
ENERGY_kcal = 627.5096
ENERGY_cm = 219474.63
ENERGY_V = 2625.5002/96484.6

def xyz2geom(xyz):
    lines = xyz.split('\n')
    atomCount = int(lines[0])
    geom = []
    for line in lines[2:2+atomCount]:
        symbol, x, y, z = line.split()[:4]
        geom.append([symbol,float(x),float(y),float(z)])
    return geom

def geom2xyz(geom):
    xyz = "%s\n\n" % len(geom)
    for line in geom:
        symbol,x,y,z = tuple(line)
        xyz += " {symbol:>2} {x:>-13.8f} {y:>-13.8f} {z:>-13.8f}\n".format(symbol=symbol,x=x,y=y,z=z)
    return xyz

def chg2pdb(xyz,charges):
    geometry = xyz2geom(xyz)
    pdb = 'TITLE\n'
    for i in range(len(geometry)):
        symbol,x,y,z = tuple(geometry[i])
        dict = {
            "index":i+1,
            "symbol":symbol,
            "x":x,
            "y":y,
            "z":z,
            "charge":charges[i],
            "radius":Periodic_Table[symbol][5]
        }
        #'HETATM{index:>5} {symbol:>2}   MOL A   1    {x:>-8.3f}{y:>-8.3f}{z:>-8.3f}{charge:>-13.8f}{radius:>9.4f}{symbol:>2}\n'.format(**dict)
        pdb += 'HETATM{index:>5} {symbol:>2}   MOL A   1    {x:>-8.3f}{y:>-8.3f}{z:>-8.3f}{charge:>-8.3f}     {radius:>8.3f} {symbol:>2}\n'.format(**dict)
    pdb += 'END\n'
    return pdb

def chg2pqr(xyz,charges):
    geometry = xyz2geom(xyz)
    pdb = 'TITLE\n'
    for i in range(len(geometry)):
        symbol,x,y,z = tuple(geometry[i])
        dict = {
            "index":i+1,
            "symbol":symbol,
            "x":x,
            "y":y,
            "z":z,
            "charge":charges[i],
            "radius":Periodic_Table[symbol][5]
        }
        pdb += 'HETATM{index:>5} {symbol:>2}   MOL A   1    {x:>-8.3f}{y:>-8.3f}{z:>-8.3f}{charge:>-13.8f}{radius:>9.4f}{symbol:>2}\n'.format(**dict)
    pdb += 'END\n'
    return pdb

def geomchg2pdb(geometry,charges):
    pdb = 'TITLE\n'
    for i in range(len(geometry)):
        symbol,x,y,z = tuple(geometry[i])
        dict = {
            "index":i+1,
            "symbol":symbol,
            "x":x,
            "y":y,
            "z":z,
            "charge":charges[i],
            "radius":Periodic_Table[symbol][5]
        }
        #'HETATM{index:>5} {symbol:>2}   MOL A   1    {x:>-8.3f}{y:>-8.3f}{z:>-8.3f}{charge:>-13.8f}{radius:>9.4f}{symbol:>2}\n'.format(**dict)
        pdb += 'HETATM{index:>5} {symbol:>2}   MOL A   1    {x:>-8.3f}{y:>-8.3f}{z:>-8.3f}{charge:>-8.3f}     {radius:>8.3f} {symbol:>2}\n'.format(**dict)
    pdb += 'END\n'
    return pdb
#data = read_gauss_data("77900ec4-d390-30f0-8a4e-79feccde6a21",job="sp",info="oribit")
#print(data)

# data = read_mwfn_data("5e74c28a-11fa-3ae4-b78b-1a9f23b2f033","gauss_surface")
# print(data)
# data = read_mwfn_data("fe5730aa-a27a-363f-9d0c-56123eca9e25",job="gauss_fukui")
# print(data)
# print(data[0]["Oribit"][0][-1]*ENERGY_eV)

#print(read_mwfn_data("d5e9a42c-3fc1-39a7-a4a0-e1154d123fdb","gauss_surface"))
