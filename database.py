import scipy
import json
import dataset
import datetime

rentypes = ["raw","renloc","rentails"]

#FIXME Feature needed: forbid merging json and non-json data
class Database():
    def __init__(self, dbname="data/spectra.db", tablename="spectra", useJson=False):
        self.db = dataset.connect('sqlite:///'+dbname)
        self.table = self.db[tablename]
        self.useJson = useJson

    def insert(self, k, L, ET, g, spec, eigv, basisSize, neigs, ren,
                eps=0., EL=0., ntails=0., occmax=0., niter=1):

        if(basisSize*neigs != eigv.size):
            # print(eigv.size)
            raise ValueError("basisSize, neigs and eigv dimension don't match")


        self.table.insert(dict(date=datetime.datetime.now(), k=k, L=L, ET=ET, EL=EL,
                g=g, ren=ren, eigv=eigv.tostring(), spec=spec.tostring(), eps=eps,
                basisSize=basisSize, neigs=neigs, occmax=occmax, ntails=ntails,
                niter=niter))

    # Get a list of all objects satisfying the query
    def getObjList(self, obj, exactQuery={}, approxQuery={}, boundQuery={}, orderBy=None):
        t1 = [e for e in self.table.find(**exactQuery)]
        listRes = []
        for e in t1:
            if all([abs(e[key]-value)<10.**(-12.)
                for key,value in approxQuery.items()]) and \
                    all([value[0]<=e[key]<value[1] for key,value in boundQuery.items()]):
                if obj=='eigv':
                    listRes.append(scipy.fromstring(e[obj]).reshape(
                        e['neigs'], e['basisSize']))
                elif obj=='spec':
                    listRes.append(scipy.fromstring(e[obj]))
                else:
                    listRes.append(e[obj])

        if orderBy==None:
            return listRes
        else:
            return [y for (x,y) in sorted(zip(orderBy, listRes))]
