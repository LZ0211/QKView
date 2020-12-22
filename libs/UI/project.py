import requests
import json as JSON
import time,re,threading
from urllib.parse import quote
from uuid import uuid3,uuid4
from uuid import UUID

NAMESPACE = UUID('63e816118377ae5a4387d7b18820752a')
reg_braket = re.compile(r'^\{\s*(\w+)\s*\}$')
reg_double_braket = re.compile(r'^\{\{\s*(\S+)\s*\}\}$')

def md5(string):
    return str(uuid3(NAMESPACE,string))

class Project:
    gauss_setting = {}
    xtb_setting = {}
    options = [
        {
            "work":"search_pubchem",
            "name": "search_pubchem",
            "selected": False,
            "inp":["{{smi}}"]
        },
        {
            "work":"xtb_opt",
            "name":"xtb_opt_geometry",
            "selected": True,
            "inp":["{{name}}","{{geometry}}"]
        },
        {
            "work":"gauss_opt",
            "name":"gauss_opt_geometry",
            "selected": True,
            "inp":["{{name}}","{{geometry}}"]
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_sp",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","sp","{{geometry}}"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_dipole",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","dipole","{{geometry}}"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_fukui",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","fukui","{{geometry}}"],
        },
        {
            "work":"gauss_calc_gibbs",
            "name":"gauss_calc_gibbs",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","{{geometry}}"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_freq",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","freq","{{geometry}}"],
        },
        {
            "work":"gauss_calc",
            "name":"gauss_calc_raman",
            "require":"gauss_opt_geometry",
            "selected": False,
            "inp":["{{name}}","raman","{{geometry}}"],
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_surface",
            "require":"gauss_calc_dipole",
            "selected": False,
            "inp":["{{name}}","gauss_surface"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_fukui",
            "require":"gauss_calc_fukui",
            "selected": False,
            "inp":["{{name}}","gauss_fukui"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_cm5_charge",
            "require":"gauss_calc_sp",
            "selected": False,
            "inp":["{{name}}","gauss_cm5_charge"]
        },
        {
            "work":"mwfn_calc",
            "name":"mwfn_calc_adch_charge",
            "require":"gauss_calc_sp",
            "selected": False,
            "inp":["{{name}}","gauss_adch_charge"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_fukui",
            "require":"mwfn_calc_fukui",
            "selected": False,
            "inp":["{{name}}","gauss_fukui"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_surface",
            "require":"mwfn_calc_surface",
            "selected": False,
            "inp":["{{name}}","gauss_surface"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_adch_charge",
            "require":"mwfn_calc_adch_charge",
            "selected": False,
            "inp":["{{name}}","gauss_adch_charge"]
        },
        {
            "work":"read_mwfn_data",
            "name":"read_cm5_charge",
            "require":"mwfn_calc_cm5_charge",
            "selected": False,
            "inp":["{{name}}","gauss_cm5_charge"]
        },
        {
            "work":"geometry_convert",
            "name":"xyz2pdb",
            "require":"xtb_opt_geometry",
            "selected": False,
            "inp":["pdb"],
        },
        {
            "work":"geometry_convert",
            "name":"xyz2mol",
            "require":"xtb_opt_geometry",
            "selected": False,
            "inp":["mol"],
        },
        {
            "work":"get_oplas_ff",
            "name":"get_oplas_ff",
            "require":"read_cm5_charge",
            "selected": False,
            "inp":["{{smi}}"]
        }
    ]
    def __init__(self,jobs=[]):
        self.host = 'http://172.16.11.164/'
        self.setup(jobs)
        self.datas = {
            "obabel":{},
            "gauss":{},
            "mwfn":{},
            "xtb":{},
            "gromacs":{}
        }
        self.charge = 0
        self.spin = 1

    def setup(self,jobs):
        self.jobs = jobs

    def alias(self,name):
        self.code = name

    def init_smi(self,smi='C'):
        self.smi = smi
        self.name = md5(smi)
        self.init_geom(self.smi2xyz(self.smi))
        charge = len(smi.split('+')) - len(smi.split('-'))
        self.set_charge(charge)

    def init_mol(self,mol):
        self.smi = self.mol2smi(mol)
        self.name = md5(self.smi)
        self.init_geom(self.smi2xyz(self.smi))
        found = re.search(r'M\s+CHG\s+\d+(.*)',mol)
        if found:
            charges = [int(i) for i in found.group(1).split()[1::2]]
            self.set_charge(sum(charges))

    def init_xyz(self,xyz):
        self.smi = self.xyz2smi(xyz)
        self.name = md5(self.smi)
        self.init_geom(xyz)

    def init_gjf(self,gjf):
        xyz = ''
        charge = ''
        spin = ''
        self.init_geom(xyz)
        self.set_charge(charge)
        self.set_spin(spin)
        self.smi = self.xyz2smi(xyz)
        self.name = md5(self.smi)

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
            #反射,获取执行函数
            func = getattr(self, job["work"])
            inp = list(map(self.parse_input,job["inp"]))
            func(*inp)
            this = job
            #深度优先
            while "next" in job:
                job = job["next"]
                self.execute(job)
            this['finished'] = 1

    def mol2smi(self,mol):
        res = requests.post(self.host+'job/submit/obabel/mol2can',json={"mol":mol})
        json = JSON.loads(res.text)
        return json['data']

    def xyz2smi(self,xyz):
        res = requests.post(self.host+'job/submit/obabel/xyz2can',json={"xyz":xyz})
        json = JSON.loads(res.text)
        return json['data']

    def smi2xyz(self,smi):
        res = requests.post(self.host+'job/submit/obabel/smi2xyz',json={"smi":smi})
        json = JSON.loads(res.text)
        return json['data']

    def geometrytoXYZ(self):
        return '''%s

        %s
        ''' % (len(self.geometry),'\n'.join(list(map(lambda x:'%s\t%s\t%s\t%s'% tuple(x),self.geometry))))

    def geometry_convert(self,cmd):
        xyz = self.geometrytoXYZ()
        res = requests.post(self.host+'job/submit/obabel/convert',json={"inp":'xyz',"out":cmd,"data":xyz})
        json = JSON.loads(res.text)
        self.datas["obabel"][cmd] = json['data']
        return json['data']

    def search_pubchem(self,smi):
        print(smi)
        properties = ['MolecularFormula','MolecularWeight','InChI','InChIKey','IUPACName','XLogP','TPSA','Charge','Volume3D']
        res = requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/'+smi+'/property/'+','.join(properties)+'/json')
        json = JSON.loads(res.text)
        self.properties = json['PropertyTable']['Properties'][0]
        #res = requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/'+smi+'/synonyms/txt')
        #text = res.text

    def debug(self,*argv):
        print(*argv)

    def gauss_calc(self,name,job,geometry,**kvargv):
        found = self.read_gauss_status(name,job)
        #如果文件不存在或者之前计算失败，则重新提交计算
        if found == 'NonExist' or found == 'Failed':
            param = {
                'name':name,
                'geometry':geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(kvargv)
            param.update(self.gauss_setting)
            res = requests.post(self.host+'job/submit/gauss/'+job,json=param)
            json = JSON.loads(res.text)
            id = json['data']
        #如果任务正在运行，获取ID
        
        elif re.search(r'Running:(\d+)',found):
            id = re.match(r'Running:(\d+)',found)[1]
        #如果文件不存在，监听计算任务
        if not found == 'Exist':
            while(True):
                status = self.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(30)
        return self

    def xtb_calc(self,name,job,geometry,**kvargv):
        found = self.read_xtb_status(name,job)
        if found == 'NonExist' or found == 'Failed':
            param = {
                'name':name,
                'geometry':geometry,
                'charge':self.charge,
                'multiplicity':self.spin,
            }
            param.update(kvargv)
            param.update(self.gauss_setting)
            res = requests.post(self.host+'job/submit/xtb/'+job,json=param)
            json = JSON.loads(res.text)
            id = json['data']
        elif re.search(r'Running:(\d+)',found):
            id = re.match(r'Running:(\d+)',found)[1]
        if not found == 'Exist':
            while(True):
                status = self.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(10)
        return self

    def mwfn_calc(self,name,job,**kvargv):
        found = self.read_mwfn_status(name,job)
        if found == 'NonExist' or found == 'Failed':
            param = {'name':name}
            param.update(kvargv)
            res = requests.post(self.host+'job/submit/mwfn/'+job,json=param)
            json = JSON.loads(res.text)
            id = json['data']
        elif re.search(r'Running:(\d+)',found):
            id = re.match(r'Running:(\d+)',found)[1]
        if not found == 'Exist':
            while(True):
                status = self.read_job_status(id)
                if status == 'Finished':
                    break
                time.sleep(10)
        return self

    def read_job_status(self,id):
        res = requests.get(self.host+'job/status?id=' + id)
        json = JSON.loads(res.text)
        return json['data']

    def read_gauss_status(self,name,job):
        res = requests.post(self.host+'job/search/gauss/'+job,json={
            'name':name
        })
        json = JSON.loads(res.text)
        print(json['data'])
        return json['data']

    def read_mwfn_status(self,name,job):
        res = requests.post(self.host+'job/search/mwfn/'+job,json={
            'name':name
        })
        json = JSON.loads(res.text)
        print(json['data'])
        return json['data']

    def read_xtb_status(self,name,job):
        res = requests.post(self.host+'job/search/xtb/'+job,json={
            'name':name
        })
        json = JSON.loads(res.text)
        print(json['data'])
        return json['data']

    def read_gauss_data(self,name,job,info='summary'):
        res = requests.post(self.host+'job/data/gauss/'+job,json={
            'name':name,
            'info':info
        })
        json = JSON.loads(res.text)
        self.datas["gauss"][job] = json['data']
        return json['data']

    def read_mwfn_data(self,name,job):
        res = requests.post(self.host+'job/data/mwfn/'+job,json={
            'name':name
        })
        json = JSON.loads(res.text)
        self.datas["mwfn"][job] = json['data']
        return json['data']

    def read_xtb_data(self,name,job):
        res = requests.post(self.host+'job/data/xtb/'+job,json={
            'name':name
        })
        json = JSON.loads(res.text)
        self.datas["xtb"][job] = json['data']
        return json['data']

    def gauss_opt(self,name,geometry):
        self.gauss_calc(name,'opt',geometry)
        self.geometry = self.read_gauss_data(name,'opt')[0]['Summary']['Geometry']
        return self

    def xtb_opt(self,name,geometry):
        self.xtb_calc(name,'opt',geometry)
        self.geometry = self.read_xtb_data(name,'opt')["Geometry"]
        return self

    def gauss_calc_gibbs(self,name,geometry):
        self.gauss_calc(name,'opt',geometry)
        geometry = self.read_gauss_data(name,'opt')[0]['Summary']['Geometry']
        self.gauss_calc(name,'gibbs',geometry,Guess='read',OldChk='OPT')
        infos = self.read_gauss_data(name,'gibbs',['summary','thermal'])
        gibbs_correct = infos[0]['Thermal']['Thermal correction to Gibbs Free Energy']
        electric_energy = infos[1]['Summary']['Energy']
        self.datas["gauss"]['gibbs'] = gibbs_correct + electric_energy
        return gibbs_correct + electric_energy

    def get_oplas_ff(self,smi):
        charges = self.datas['mwfn']['gauss_cm5_charge']
        for i in range(1,len(charges)):
            charges[i] = round(1.2 * charges[i],3)
        charges[0] = round(self.charge * 1.2 - sum(charges[1:]),3)
        boundary = uuid4().hex
        linesep = '\r\n'
        header={'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)}
        data = {
            "smiData":smi,
            "molpdbfile":('', ''),
            "checkopt":"0",
            "chargetype": "cm1a",# cm1abcc
            "dropcharge": "0" # -2,-1,0,1,2
        }
        string = ''
        for (k,v) in data.items():
            if type(v) == str:
                string += '--{0}{1}Content-Disposition: form-data; name="{2}";{1}{1}{3}{1}'.format(boundary,linesep, k, v)
            if type(v) == tuple:
                string += '--{0}{1}Content-Disposition: form-data; name="{2}"; filename="{3}"{1}Content-Type: application/octet-stream{1}{1}{4}{1}'.format(boundary,linesep, k, v[0], v[1])
        string += '--{0}--{1}'.format(boundary,linesep)
        res = requests.post('http://zarbi.chem.yale.edu/cgi-bin/results_lpg.py',headers=header, data=string)
        #print(res.text)
        id = re.search(r'/tmp/(.*)\.gro',res.text).group(1)
        res = requests.post('http://zarbi.chem.yale.edu/cgi-bin/download_lpg.py',data={"go":"TOP","fileout":"/tmp/"+id+".pdb"})
        self.datas["gromacs"]["pdb"] = re.sub('UNK','   ',str(res.content, encoding = "utf-8"))
        res = requests.post('http://zarbi.chem.yale.edu/cgi-bin/download_lpg.py',data={"go":"TOP","fileout":"/tmp/"+id+".itp"})
        itp = re.sub('UNK',self.code,str(res.content, encoding = "utf-8"))
        itp = re.sub('opls_',self.code+'_oplas_',itp)
        itp = re.sub(r';.*\n','',itp)
        atomStr = re.search(r'\[\s*atoms\s*\]\n([\s\S]*)\n\[\s*bonds\s*\]',itp).group(1)
        atoms = atomStr.split('\n')
        string = ''
        for i in range(len(atoms)):
            atom = atoms[i]
            arr = atom.split()
            arr[6] = charges[i]
            string += '{0:>6s}   {1}{2:>6s} {3:>8s} {4:>6s} {5:>6s} {6:>-8.4f} {7:>12s}\n'.format(*arr)
        self.datas["gromacs"]["itp"] = itp.replace(atomStr,string)
        pdb = self.datas["gromacs"]["pdb"]
        itp = self.datas["gromacs"]["itp"]
        open('%s.pdb' % self.code,'w+').write(pdb)
        open('%s_ATP.itp' % self.code,'w+').write(re.split(r'\[\s*moleculetype\s*\]',itp)[0])
        open('%s.itp' % self.code,'w+').write('[ moleculetype ]'+re.split(r'\[\s*moleculetype\s*\]',itp)[1])

    def select_options(self,jobname):
        job = Project.select(jobname)
        if job in self.jobs:
            return
        if 'require' in job:
            self.select_options(job['require'])
        self.jobs.append(job)

    @staticmethod
    def select(jobname):
        for job in Project.options:
            if job['name'] == jobname:
                return job

    @staticmethod
    def hash(smi):
        return md5(smi)

    @staticmethod
    def smi2skt(smi):
        res = requests.get('http://121.42.137.238/chemmol/src/server/smiToMol.php?smiles='+quote(smi))
        json = JSON.loads(res.text)
        return json['data']['mol']
