import sys
from PyQt5.QtCore import QThread, pyqtSignal,QObject
from . import API
import requests,re,json,time,traceback

reg_braket = re.compile(r'^\{\s*(\w+)\s*\}$')
reg_double_braket = re.compile(r'^\{\{\s*(\S+)\s*\}\}$')

options = [
    {
        "work": "xtb_calc",
        "name": "xtb_calc_opt",
        "inp": ["opt"]
    },
    {
        "work": "read_xtb_geom",
        "name": "read_xtb_geom",
        "require": ["xtb_calc_opt"],
        "inp":[]
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_opt",
        "require": ["read_xtb_geom"],
        "inp": ["opt"]
    },
    {
        "work": "read_gauss_geom",
        "name": "read_gauss_geom",
        "require": ["gauss_calc_opt"],
        "inp":[]
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_sp",
        "require": ["read_gauss_geom"],
        "inp":["sp"],
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_dipole",
        "require": ["read_gauss_geom"],
        "inp":["dipole"],
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_fukui",
        "require": ["read_gauss_geom"],
        "inp":["fukui"],
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_freq",
        "require": ["read_gauss_geom"],
        "inp":["freq"],
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_nmr",
        "require": ["read_gauss_geom"],
        "inp":["nmr"],
    },
    {
        "work": "gauss_calc",
        "name": "gauss_calc_raman",
        "require": ["read_gauss_geom"],
        "inp":["raman"],
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_surface",
        "require": ["gauss_calc_dipole"],
        "inp":["gauss_surface"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_fukui",
        "require": ["gauss_calc_fukui"],
        "inp":["gauss_fukui"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_cm5_charge",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_cm5_charge"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_adch_charge",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_adch_charge"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_mulliken_charge",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_mulliken_charge"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_resp_charge",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_resp_charge"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_mayer_bo",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_mayer_bo"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_laplacian_bo",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_laplacian_bo"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_mulliken_bo",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_mulliken_bo"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_fuzzy_bo",
        "require": ["gauss_calc_sp"],
        "inp":["gauss_fuzzy_bo"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_ir",
        "require": ["gauss_calc_freq"],
        "inp":["gauss_ir"]
    },
    {
        "work": "mwfn_calc",
        "name": "mwfn_calc_raman",
        "require": ["gauss_calc_raman"],
        "inp":["gauss_raman"]
    },

    {
        "work": "pipline_calc_opt",
        "name": "pipline_calc_opt",
        "text": "结构优化",
        "require": ["gauss_calc_opt"],
        "inp":[]
    },

    {
        "work": "pipline_calc_freq",
        "name": "pipline_calc_freq",
        "text": "振动分析",
        "require": ["gauss_calc_freq"],
        "inp":[]
    },

    {
        "work": "pipline_calc_sp",
        "name": "pipline_calc_sp",
        "text": "单点计算",
        "require": ["gauss_calc_sp"],
        "inp":[]
    },
    {
        "work": "pipline_calc_cdft",
        "name": "pipline_calc_cdft",
        "text": "概念密度泛函",
        "require": ["gauss_calc_fukui", "mwfn_calc_fukui"],
        "inp":[]
    },
    {
        "work": "pipline_calc_mulliken_charge",
        "name": "pipline_calc_mulliken_charge",
        "text": "Mulliken电荷",
        "require": ["mwfn_calc_mulliken_charge"],
        "inp":[]
    },
    {
        "work": "pipline_calc_adch_charge",
        "name": "pipline_calc_adch_charge",
        "text": "ADCH电荷",
        "require": ["mwfn_calc_adch_charge"],
        "inp":[]
    },
    {
        "work": "pipline_calc_cm5_charge",
        "name": "pipline_calc_cm5_charge",
        "text": "CM5电荷",
        "require": ["mwfn_calc_cm5_charge"],
        "inp":[]
    },
    {
        "work": "pipline_calc_resp_charge",
        "name": "pipline_calc_resp_charge",
        "text": "RESP电荷",
        "require": ["mwfn_calc_resp_charge"],
        "inp":[]
    },
    {
        "work": "pipline_calc_mulliken_bo",
        "name": "pipline_calc_mulliken_bo",
        "text": "Mulliken键级",
        "require": ["mwfn_calc_mulliken_bo"],
        "inp":[]
    },
    {
        "work": "pipline_calc_mayer_bo",
        "name": "pipline_calc_mayer_bo",
        "text": "Mayer键级",
        "require": ["mwfn_calc_mayer_bo"],
        "inp":[]
    },
    {
        "work": "pipline_calc_laplacian_bo",
        "name": "pipline_calc_laplacian_bo",
        "text": "拉普拉斯键级",
        "require": ["mwfn_calc_laplacian_bo"],
        "inp":[]
    },
    {
        "work": "pipline_calc_fuzzy_bo",
        "name": "pipline_calc_fuzzy_bo",
        "text": "模糊键级",
        "require": ["mwfn_calc_fuzzy_bo"],
        "inp":[]
    },
    {
        "work": "pipline_calc_dipole",
        "name": "pipline_calc_dipole",
        "text": "分子偶极矩",
        "require": ["gauss_calc_dipole"],
        "inp":[]
    },
    {
        "work": "pipline_calc_surface",
        "name": "pipline_calc_surface",
        "text": "表面静电势",
        "require": ["mwfn_calc_surface"],
        "inp":[]
    },
    {
        "work": "pipline_calc_nmr",
        "name": "pipline_calc_nmr",
        "text": "核磁共振谱",
        "require": ["gauss_calc_nmr"],
        "inp":[]
    },
    {
        "work": "pipline_calc_ir",
        "name": "pipline_calc_ir",
        "text": "红外光谱",
        "require": ["mwfn_calc_ir"],
        "inp":[]
    },
    {
        "work": "pipline_calc_raman",
        "name": "pipline_calc_raman",
        "text": "拉曼光谱",
        "require": ["mwfn_calc_raman"],
        "inp":[]
    },
    # {
    #     "work": "pipline_calc_binding_Li",
    #     "name": "pipline_calc_binding_Li",
    #     "text": "Li+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Li",
    #     "name": "pipline_calc_binding_Li",
    #     "text": "Li+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Na",
    #     "name": "pipline_calc_binding_Na",
    #     "text": "Na+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Mg",
    #     "name": "pipline_calc_binding_Mg",
    #     "text": "Mg2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Mn",
    #     "name": "pipline_calc_binding_Mn",
    #     "text": "Mn2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Co",
    #     "name": "pipline_calc_binding_Co",
    #     "text": "Co2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Ni",
    #     "name": "pipline_calc_binding_Ni",
    #     "text": "Ni2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Fe2",
    #     "name": "pipline_calc_binding_Fe2",
    #     "text": "Fe2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Fe3",
    #     "name": "pipline_calc_binding_Fe3",
    #     "text": "Fe3+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Cu",
    #     "name": "pipline_calc_binding_Cu",
    #     "text": "Cu2+结合能",
    #     "require": [],
    #     "inp":[]
    # },
    # {
    #     "work": "pipline_calc_binding_Zn",
    #     "name": "pipline_calc_binding_Zn",
    #     "text": "Zn2+结合能",
    #     "require": [],
    #     "inp":[]
    # }
]

def select(jobname):
    for job in options:
        if job['name'] == jobname:
            return job

def selectText(text):
    for job in options:
        if 'text' in job and job['text'] == text:
            return job

class Project(QThread):
    processed = pyqtSignal(int)
    finished = pyqtSignal(str)
    terminal = pyqtSignal()
    returned = pyqtSignal(str,str)
    config = {
        "Gauss_Core" : 24,
        "Gauss_Memory" : '60GB',
        "Gauss_Memory" : '60GB'
    }
    gauss_params = {
        #"Method":"PBE1PBE",
        #"Basis":"def2SVP",
        #"Solvent":""
    }
    def __init__(self,parent=None):
        super(Project, self).__init__()
        self.parent = parent
        self.charge = 0
        self.spin = 1
        self.isEnd = False
        self.interval = 10
        self.jobs = []
        self.queue = []
        self.finish = []

    def init_smi(self,smi='C'):
        self.init_geom(API.smi2xyz(self.smi))
        self.set_charge(API.smi2chg(smi))

    def init_mol(self,mol):
        self.init_geom(API.mol2xyz(mol))
        found = re.search(r'M\s+CHG\s+\d+(.*)',mol)
        if found:
            charges = [int(i) for i in found.group(1).split()[1::2]]
            self.set_charge(sum(charges))

    def init_xyz(self,xyz):
        self.init_geom(xyz)

    def init_geom(self,xyz):
        lines = xyz.strip().split('\n')[2:]
        self.geometry = [line.split() for line in lines]

    def set_charge(self,charge=0):
        self.charge = charge

    def set_spin(self,spin=1):
        self.spin = spin

    def parse_input(self,param):
        found = reg_double_braket.search(param)
        if found:
            keys = re.sub(r'\[\s*(-?\d+\s*:?\s*-?\d*)\s*\]',r'.\g<1>',found.group(1)).split('.')
            this = self
            while len(keys):
                key = keys.pop(0)
                if isinstance(this,dict):
                    if not key in this:
                        return None
                    this = this[key]
                elif isinstance(this,list) or isinstance(this,tuple):
                    try:
                        matched = re.search(r'^(-?\d+)\s*:\s*(-?\d+)$',key)
                        if matched:
                            this = this[int(matched.group(1)):int(matched.group(2))]
                        elif re.search(r'^-?\d+$',key):
                            this = this[int(key)]
                        else:
                            return None
                    except:
                        return None
                else:
                    try:
                        this = getattr(this,key)
                    except:
                        return None
            return this
        found = reg_braket.search(param)
        if found:
            return param.format(**self.__dict__)
        return param

    def execute(self):
        jobs = self.jobs
        for job in jobs:
            if self.isEnd == True:
                return
            #反射,获取执行函数
            print(job)
            func = getattr(self, job["work"])
            inp = list(map(self.parse_input,job["inp"]))
            func(*inp)

    def gauss_calc(self,job,**kvargv):
        status = API.read_gauss_status(self.name,job)
        #如果文件不存在或者之前计算失败，则重新提交计算
        if status in ['NonExist','Failed']:
            param = {
                'name':self.name,
                'geometry':self.geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(self.config)
            param.update(self.gauss_params)
            param.update(kvargv)
            res = requests.post('{host}/job/submit/gauss/{job}'.format(host=API.HOST,job=job),json=param)
            id = json.loads(res.text)['data']
        #如果任务正在运行，获取ID
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        #如果文件不存在，监听计算任务
        #计算失败重新提交，累积三次
        for i in range(3):
            if not status == 'Exist':
                while(not self.isEnd):
                    status = API.read_job_status(id)
                    if status == 'Finished':
                        break
                    time.sleep(self.interval)
            status = API.read_gauss_status(self.name,job)

    def xtb_calc(self,job,**kvargv):
        status = API.read_xtb_status(self.name,job)
        if status in ["NonExist","Failed"]:
            param = {
                'name':self.name,
                'geometry':self.geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(self.config)
            param.update(kvargv)
            res = requests.post('{host}/job/submit/xtb/{job}'.format(host=API.HOST,job=job),json=param)
            id = json.loads(res.text)['data']
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        if not status == 'Exist':
            while(not self.isEnd):
                status = API.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(self.interval)
        return self

    def mwfn_calc(self,job,**kvargv):
        status = API.read_mwfn_status(self.name,job)
        if status in ['NonExist','Failed']:
            param = {'name':self.name}
            param.update(self.config)
            param.update(kvargv)
            res = requests.post('{host}/job/submit/mwfn/{job}'.format(host=API.HOST,job=job),json=param)
            id = json.loads(res.text)['data']
        elif re.search(r'Running:(\d+)',status):
            id = re.match(r'Running:(\d+)',status)[1]
        if not status == 'Exist':
            while(not self.isEnd):
                status = API.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(self.interval)
        return self

    def read_gauss_geom(self):
        self.geometry = API.read_gauss_data(self.name,'opt')[0]['Summary']['Geometry']
        info = {
            "uuid":self.name,
            "xyz":API.geom2xyz(self.geometry)
        }
        self.returned.emit('index',json.dumps(info))

    def read_xtb_geom(self):
        self.geometry = API.read_xtb_data(self.name,'opt')["Geometry"]

    def run(self):
        while len(self.queue) > len(self.finish) and not self.isEnd:
            self.processed.emit(int(100 * len(self.finish) / len(self.queue)))
            data = self.queue[len(self.finish)]
            mol = data["mol"]
            uuid = data["uuid"]
            self.name = uuid
            self.init_mol(mol)
            try:
                self.execute()
            except:
                print(traceback.format_exc())
                pass
            self.finish.append(uuid)
            self.finished.emit(uuid)
            self.processed.emit(int(100 * len(self.finish) / len(self.queue)))
        self.terminal.emit()

    def clear(self):
        self.queue = []
        self.finish = []
        self.ndx = 0

    def test(self):
        if not self.isEnd:
            time.sleep(self.interval)

    def onceEnd(self,fn):
        def func(*argv):
            fn(*argv)
            self.terminal.disconnect(func)
        self.terminal.connect(func)

    def end(self):
        self.isEnd = True
        self.interval = 0

    def add_queue(self,data):
        self.queue.append(data)
        self.processed.emit(int(100 * len(self.finish) / len(self.queue)))

    def add_job(self,jobname):
        job = select(jobname)
        if job == None:
            return
        if job in self.jobs:
            return
        if 'require' in job:
            for pre in job['require']:
                self.add_job(pre)
        self.jobs.append(job)

    def add_text_job(self,text):
        job = selectText(text)
        if job == None:
            return
        if job in self.jobs:
            return
        if 'require' in job:
            for pre in job['require']:
                self.add_job(pre)
        self.jobs.append(job)

    def set_text_jobs(self,list):
        self.jobs = []
        for text in list:
            self.add_text_job(text)

    def set_jobs(self,names):
        self.jobs = []
        for name in names:
            self.add_job(name)

    def pipline_calc_opt(self):
        data = API.read_gauss_data(self.name,'opt',info='summary')[0]['Summary']
        info = {
            "uuid":self.name,
            "xyz":API.geom2xyz(data["Geometry"])
        }
        self.returned.emit('index',json.dumps(info))

    def pipline_calc_sp(self):
        data = API.read_gauss_data(self.name,"sp",info='summary')[0]["Summary"]
        orbt = API.read_gauss_data(self.name,"sp",info='oribit')[0]["Oribit"]
        summary = {
            'uuid':self.name,
            'geometry':json.dumps(data["Geometry"]),
            'charge':data["Charge"],
            'spin':data["Spin"],
            'point_group':data["PointGroup"],
            'energy':data["Energy"],
            "homo":orbt[0][-1]*API.ENERGY_eV,
            "lumo":orbt[1][0]*API.ENERGY_eV,
            'dipole_X':data["Dipole"][0],
            'dipole_Y':data["Dipole"][1],
            'dipole_Z':data["Dipole"][2],
            'dipole':API.normalize(data["Dipole"])
        }
        self.returned.emit('summary',json.dumps(summary))

    def pipline_calc_freq(self):
        data = API.read_gauss_data(self.name,"freq",info='thermal')[0]["Thermal"]
        summary = {
            "uuid":self.name,
            'cor_zpe':data['Zero-point correction'],
            'cor_energy':data['Thermal correction to Energy'],
            'cor_enthalpy':data['Thermal correction to Enthalpy'],
            'cor_gibbs':data['Thermal correction to Gibbs Free Energy']
        }
        self.returned.emit('summary',json.dumps(summary))

    def pipline_calc_cdft(self):
        data = API.read_mwfn_data(self.name,job="gauss_fukui")
        cdft = {
            'uuid':self.name,
            'vertical_ip':data['IP'],
            'vertical_ea':data['EA'],
            'electro_negativity':data['EN'],
            'chemical_potential':data['CP'],
            'softness':data['SO'],
            'hardness':data['HD'],
            'electr_index':data['EP'],
            'nucle_index':data['NP'],
            'f_plus':json.dumps(data['f+']),
            'f_minus':json.dumps(data['f-']),
            'f_zero':json.dumps(data['f0']),
            'cdd':json.dumps(data['CDD']),
            'condensed_electr_index':json.dumps(data['CEP']),
            'condensed_nucle_index':json.dumps(data['CNP']),
            'condensed_softness':json.dumps(data['CSO'])
        }
        self.returned.emit('cdft',json.dumps(cdft))

    def pipline_calc_mulliken_charge(self):
        data = API.read_mwfn_data(self.name,job="gauss_mulliken_charge")
        charge = {
            'uuid':self.name,
            'mulliken':json.dumps(data),
        }
        self.returned.emit('charge',json.dumps(charge))

    def pipline_calc_adch_charge(self):
        data = API.read_mwfn_data(self.name,job="gauss_adch_charge")
        charge = {
            'uuid':self.name,
            'adch':json.dumps(data),
        }
        self.returned.emit('charge',json.dumps(charge))

    def pipline_calc_cm5_charge(self):
        data = API.read_mwfn_data(self.name,job="gauss_cm5_charge")
        charge = {
            'uuid':self.name,
            'cm5':json.dumps(data),
        }
        self.returned.emit('charge',json.dumps(charge))

    def pipline_calc_resp_charge(self):
        data = API.read_mwfn_data(self.name,job="gauss_resp_charge")
        charge = {
            'uuid':self.name,
            'resp':json.dumps(data),
        }
        self.returned.emit('charge',json.dumps(charge))

    def pipline_calc_mulliken_bo(self):
        data = API.read_mwfn_data(self.name,job="gauss_mulliken_bo")
        bo = {
            'uuid':self.name,
            'mulliken':json.dumps(data),
        }
        self.returned.emit('bo',json.dumps(bo))

    def pipline_calc_mayer_bo(self):
        data = API.read_mwfn_data(self.name,job="gauss_mayer_bo")
        bo = {
            'uuid':self.name,
            'mayer':json.dumps(data),
        }
        self.returned.emit('bo',json.dumps(bo))

    def pipline_calc_laplacian_bo(self):
        data = API.read_mwfn_data(self.name,job="gauss_laplacian_bo")
        bo = {
            'uuid':self.name,
            'laplacian':json.dumps(data),
        }
        self.returned.emit('bo',json.dumps(bo))

    def pipline_calc_fuzzy_bo(self):
        data = API.read_mwfn_data(self.name,job="gauss_fuzzy_bo")
        bo = {
            'uuid':self.name,
            'fuzzy':json.dumps(data),
        }
        self.returned.emit('bo',json.dumps(bo))

    def pipline_calc_dipole(self):
        data = API.read_gauss_data(self.name,"dipole",info='summary')[0]["Summary"]
        summary = {
            'uuid':self.name,
            'dipole_X':data["Dipole"][0],
            'dipole_Y':data["Dipole"][1],
            'dipole_Z':data["Dipole"][2],
            'dipole':API.normalize(data["Dipole"])
        }
        self.returned.emit('summary',json.dumps(summary))

    def pipline_calc_surface(self):
        data = API.read_mwfn_data(self.name,job="gauss_surface")
        surface = {
            'uuid':self.name,
            'volume':data['Volume'],
            'density':data['Density'],
            'minimal':data['Minimal'],
            'maximal':data['Maximal'],
            'total_area':data['SurfaceArea'],
            'positive_area':data['PositiveSurfaceArea'],
            'negative_area':data['NegativeSurfaceArea'],
            'total_avg':data['SurfaceAvg'],
            'positive_avg':data['PositiveSurfaceAvg'],
            'negative_avg':data['NegativeSurfaceAvg'],
            'total_var':data['SurfaceVar'],
            'positive_var':data['PositiveSurfaceVar'],
            'negative_var':data['NegativeSurfaceVar'],
            'sigma_product':data['SigmaProduct'],
            'charge_balance':data['ChargeBalance'],
            'mpi':data['MPI'],
            'polar_area':data['PolarArea'],
            'nonpolar_area':data['NonPolarArea'],
            'pi':data['Pi']
        }
        self.returned.emit('surface',json.dumps(surface))

    def pipline_calc_nmr(self):
        pass

    def pipline_calc_ir(self):
        pass

    def pipline_calc_raman(self):
        pass

    def pipline_calc_uv(self):
        pass

    def pipline_calc_pl(self):
        pass

    def pipline_calc_binding_Li(self):
        pass

    def pipline_calc_binding_Na(self):
        pass

    def pipline_calc_binding_Mg(self):
        pass

    def pipline_calc_binding_Mn(self):
        pass

    def pipline_calc_binding_Co(self):
        pass

    def pipline_calc_binding_Fe3(self):
        pass

    def pipline_calc_binding_Fe2(self):
        pass

    def pipline_calc_binding_Cu(self):
        pass

    def pipline_calc_binding_Zn(self):
        pass

    def pipline_calc_binding_Ni(self):
        pass

    @staticmethod
    def select(jobname):
        for job in options:
            if job['name'] == jobname:
                return job

    @staticmethod
    def selectText(text):
        for job in options:
            if 'text' in job and job['text'] == text:
                return job
