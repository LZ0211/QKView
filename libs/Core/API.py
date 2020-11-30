import requests
import json,base64,re,os,platform

HOST = 'http://172.16.11.164'

JSON_HEADERS = {'Content-Type': 'application/json'}

TIMEOUT = 5

SketcherURL = HOST + "/static/sketcher/"

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

def mol2png(mol):
    url = HOST + '/job/submit/obabel/mol2png'
    data = {'mol':mol}
    res = requests.post(url,json=data,headers=JSON_HEADERS, timeout=TIMEOUT)
    pdb = json.loads(res.text)["data"]

def pdb2can(pdb):
    url = HOST + '/job/submit/obabel/pdb2can'
    res = requests.post(url,json={'pdb': pdb},headers=JSON_HEADERS, timeout=TIMEOUT)
    smi = json.loads(res.text)["data"]
    return smi

def pdb2mol(pdb):
    url = HOST + '/job/submit/obabel/convert'
    res = requests.post(url,json={'inp': 'pdb','out':'mol','data':pdb},headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def pdb2xyz(pdb):
    url = HOST + '/job/submit/obabel/convert'
    res = requests.post(url,json={'inp': 'pdb','out':'xyz','data':pdb},headers=JSON_HEADERS, timeout=TIMEOUT)
    xyz = json.loads(res.text)["data"]
    return xyz

def xyz2can(xyz):
    url = HOST + '/job/submit/obabel/xyz2can'
    res = requests.post(url,json={'xyz': xyz},headers=JSON_HEADERS, timeout=TIMEOUT)
    smi = json.loads(res.text)["data"]
    return smi

def xyz2mol(xyz):
    url = HOST + '/job/submit/obabel/convert'
    res = requests.post(url,json={'inp': 'xyz','out':'mol','data':xyz},headers=JSON_HEADERS, timeout=TIMEOUT)
    mol = json.loads(res.text)["data"]
    return mol

def xyz2pdb(xyz):
    url = HOST + '/job/submit/obabel/convert'
    res = requests.post(url,json={'inp': 'xyz','out':'pdb','data':xyz},headers=JSON_HEADERS, timeout=TIMEOUT)
    pdb = json.loads(res.text)["data"]
    return pdb

def smi2mol2D(smi):
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

def base64ToImage(string):
    return base64.b64decode(string.split(';base64,')[1])

Periodic_Table={
    #No. Symbol, Mass, Electronegativity, Orbits
    "H":(1,"H",1.008,2.20,((1))),
    "He":(2,"He",4.0026,None,((2))),
    "Li":(3,"Li",6.94,0.98,((2),(1))),
    "Be":(4,"Be",9.0122,1.57,((2),(2))),
    "B":(5,"B",10.81,2.04,((2),(2,1))),
    "C":(6,"C",12.011,2.55,((2),(2,2))),
    "N":(7,"N",14.007,3.04,((2),(2,3))),
    "O":(8,"O",15.999,3.44,((2),(2,4))),
    "F":(9,"F",18.998,3.90,((2),(2,5))),
    "Ne":(10,"Ne",20.18,None,((2),(2,6))),
    "Na":(11,"Na",22.99,0.93,((2),(2,6),(1))),
    "Mg":(12,"Mg",24.305,1.31,((2),(2,6),(2))),
    "Al":(13,"Al",26.982,1.61,((2),(2,6),(2,1))),
    "Si":(14,"Si",28.085,1.90,((2),(2,6),(2,2))),
    "P":(15,"P",30.974,2.19,((2),(2,6),(2,3))),
    "S":(16,"S",32.06,2.58,((2),(2,6),(2,4))),
    "Cl":(17,"Cl",35.45,3.16,((2),(2,6),(2,5))),
    "Ar":(18,"Ar",39.95,None,((2),(2,6),(2,6))),
    "K":(19,"K",39.098,0.82,((2),(2,6),(2,6),(1))),
    "Ca":(20,"Ca",40.078,1.00,((2),(2,6),(2,6),(2))),
    "Sc":(21,"Sc",44.956,1.36,((2),(2,6),(2,6,1),(2))),
    "Ti":(22,"Ti",47.867,1.54,((2),(2,6),(2,6,2),(2))),
    "V":(23,"V",50.942,1.63,((2),(2,6),(2,6,3),(2))),
    "Cr":(24,"Cr",51.996,1.66,((2),(2,6),(2,6,5),(1))),
    "Mn":(25,"Mn",54.938,1.55,((2),(2,6),(2,6,5),(2))),
    "Fe":(26,"Fe",55.845,1.83,((2),(2,6),(2,6,6),(2))),
    "Co":(27,"Co",58.933,1.88,((2),(2,6),(2,6,7),(2))),
    "Ni":(28,"Ni",58.693,1.91,((2),(2,6),(2,6,8),(2))),
    "Cu":(29,"Cu",63.546,1.90,((2),(2,6),(2,6,10),(1))),
    "Zn":(30,"Zn",65.38,1.65,((2),(2,6),(2,6,10),(2))),
    "Ga":(31,"Ga",69.723,1.81,((2),(2,6),(2,6,10),(2,1))),
    "Ge":(32,"Ge",72.63,2.01,((2),(2,6),(2,6,10),(2,2))),
    "As":(33,"As",74.922,2.18,((2),(2,6),(2,6,10),(2,3))),
    "Se":(34,"Se",78.971,2.55,((2),(2,6),(2,6,10),(2,4))),
    "Br":(35,"Br",79.901,2.96,((2),(2,6),(2,6,10),(2,5))),
    "Kr":(36,"Kr",83.798,None,((2),(2,6),(2,6,10),(2,6))),
    "Rb":(37,"Rb",85.468,0.82,((2),(2,6),(2,6,10),(2,6),(1))),
    "Sr":(38,"Sr",87.62,0.95,((2),(2,6),(2,6,10),(2,6),(2))),
    "Y":(39,"Y",88.906,1.22,((2),(2,6),(2,6,10),(2,6,1),(2))),
    "Zr":(40,"Zr",91.224,1.33,((2),(2,6),(2,6,10),(2,6,2),(2))),
    "Nb":(41,"Nb",92.906,1.60,((2),(2,6),(2,6,10),(2,6,3),(2))),
    "Mo":(42,"Mo",95.95,2.16,((2),(2,6),(2,6,10),(2,6,5),(1))),
    "Tc":(43,"Tc",98,2.10,((2),(2,6),(2,6,10),(2,6,5),(2))),
    "Ru":(44,"Ru",101.07,2.20,((2),(2,6),(2,6,10),(2,6,7),(1))),
    "Rh":(45,"Rh",102.91,2.28,((2),(2,6),(2,6,10),(2,6,8),(1))),
    "Pd":(46,"Pd",106.42,2.20,((2),(2,6),(2,6,10),(2,6,10))),
    "Ag":(47,"Ag",107.87,1.93,((2),(2,6),(2,6,10),(2,6,10),(1))),
    "Cd":(48,"Cd",112.41,1.69,((2),(2,6),(2,6,10),(2,6,10),(2))),
    "In":(49,"In",114.82,1.78,((2),(2,6),(2,6,10),(2,6,10),(2,1))),
    "Sn":(50,"Sn",118.71,1.96,((2),(2,6),(2,6,10),(2,6,10),(2,2))),
    "Sb":(51,"Sb",121.76,2.05,((2),(2,6),(2,6,10),(2,6,10),(2,3))),
    "Te":(52,"Te",127.6,2.10,((2),(2,6),(2,6,10),(2,6,10),(2,4))),
    "I":(53,"I",126.9,2.66,((2),(2,6),(2,6,10),(2,6,10),(2,5))),
    "Xe":(54,"Xe",131.29,None,((2),(2,6),(2,6,10),(2,6,10),(2,6))),
    "Cs":(55,"Cs",132.91,0.79,((2),(2,6),(2,6,10),(2,6,10),(2,6),(1))),
    "Ba":(56,"Ba",137.33,0.89,((2),(2,6),(2,6,10),(2,6,10),(2,6),(2))),
    "La":(57,"La",138.91,1.10,((2),(2,6),(2,6,10),(2,6,10),(2,6,1),(2))),
    "Ce":(58,"Ce",140.12,1.12,((2),(2,6),(2,6,10),(2,6,10),(2,6),(1),(1),(2))),
    "Pr":(59,"Pr",140.91,1.13,((2),(2,6),(2,6,10),(2,6,10),(2,6),(3),(2))),
    "Nd":(60,"Nd",144.24,1.14,((2),(2,6),(2,6,10),(2,6,10),(2,6),(4),(2))),
    "Pm":(61,"Pm",145,1.15,((2),(2,6),(2,6,10),(2,6,10),(2,6),(5),(2))),
    "Sm":(62,"Sm",150.36,1.17,((2),(2,6),(2,6,10),(2,6,10),(2,6),(6),(2))),
    "Eu":(63,"Eu",151.96,1.18,((2),(2,6),(2,6,10),(2,6,10),(2,6),(7),(2))),
    "Gd":(64,"Gd",157.25,1.20,((2),(2,6),(2,6,10),(2,6,10),(2,6),(7),(1),(2))),
    "Tb":(65,"Tb",158.93,1.21,((2),(2,6),(2,6,10),(2,6,10),(2,6),(9),(2))),
    "Dy":(66,"Dy",162.5,1.22,((2),(2,6),(2,6,10),(2,6,10),(2,6),(10),(2))),
    "Ho":(67,"Ho",164.93,1.23,((2),(2,6),(2,6,10),(2,6,10),(2,6),(11),(2))),
    "Er":(68,"Er",167.26,1.24,((2),(2,6),(2,6,10),(2,6,10),(2,6),(12),(2))),
    "Tm":(69,"Tm",168.93,1.25,((2),(2,6),(2,6,10),(2,6,10),(2,6),(13),(2))),
    "Yb":(70,"Yb",173.05,1.26,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(2))),
    "Lu":(71,"Lu",174.97,1.0,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(1),(2))),
    "Hf":(72,"Hf",178.49,1.3,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(2),(2))),
    "Ta":(73,"Ta",180.95,1.5,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(3),(2))),
    "W":(74,"W",183.84,1.7,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(4),(2))),
    "Re":(75,"Re",186.21,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(5),(2))),
    "Os":(76,"Os",190.23,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(6),(2))),
    "Ir":(77,"Ir",192.22,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(7),(2))),
    "Pt":(78,"Pt",195.08,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(9),(1))),
    "Au":(79,"Au",196.97,2.4,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(1))),
    "Hg":(80,"Hg",200.59,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2))),
    "Tl":(81,"Tl",204.38,1.8,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,1))),
    "Pb":(82,"Pb",207.2,1.8,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,2))),
    "Bi":(83,"Bi",208.98,1.9,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,3))),
    "Po":(84,"Po",209,2.0,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,4))),
    "At":(85,"At",210,2.2,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,5))),
    "Rn":(86,"Rn",222,None,((2),(2,6),(2,6,10),(2,6,10),(2,6),(14),(10),(2,2)))
}

Organic_Elements = ['B','Si','C','P','N','H','S','O','F','Cl','Br','I']

Element_Patterm = re.compile(r'([a-zA-Z]{1,2})(\d+)')
def calcFormularMass(formular):
    elements = Element_Patterm.findall(formular)
    sum = 0
    for pair in elements:
        k,v = tuple(pair)
        sum += Periodic_Table[k][2] * int(v)
    return sum

def calcFormular(xyz):
    lines = xyz.split('\n')
    count = int(lines[0])
    records = {}
    for line in lines[2:2+count]:
        symbol = line.split()[0]
        if symbol in records:
            records[symbol] += 1
        else:
            records[symbol] = 1
    elements = list(records.keys())
    for element in elements:
        if not element in Organic_Elements:
            elements.sort(key=lambda x:Periodic_Table[x][3])
            return "".join(map(lambda k:k+str(records[k]),elements))
    elements.sort(key=lambda x:Organic_Elements.index(x))
    return "".join(map(lambda k:k+str(records[k]),elements))

def calcXYZMass(xyz):
    return calcFormularMass(calcFormular(xyz))

def download(url,file):
    res = requests.get(url, stream=True)
    with open(file, "wb") as hander:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                hander.write(chunk)
    
def getLanguages(dirname):
    files = os.listdir(os.path.join(dirname,"languages"))
    langs = filter(lambda file:os.path.splitext(file)[1]==".lang",files)
    return list(map(lambda file:os.path.splitext(file)[0],langs))

SYSTEM = platform.system()
PATH_SEG = '\\' if SYSTEM == 'Windows' else '/'

def formatPath(path):
    return path.replace('/','\\').replace('\\',PATH_SEG)