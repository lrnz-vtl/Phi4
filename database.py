import scipy
import json
import dataset
import datetime

class Database():
    def __init__(self, dbname="spectra.db", tablename="spectra"):
        self.db = dataset.connect('sqlite:///'+dbname)
        self.table=self.db[tablename]

    def insert(self, k, L, Emax, g, spec, basisSize, neigs, m, ren, ordMass=1, cutoff=5):
        L = float(L)
        k = int(k)
        Emax = float(Emax)
        g = float(g)
        m = float(m)
        basisSize = int(basisSize)
        neigs = int(neigs)

        self.table.insert(dict(date=datetime.datetime.now(), k=k, L=L, m=m, Emax=Emax, g=g, ren=ren,  \
                                ordMass=ordMass, cutoff=cutoff, spec=json.dumps(spec.tolist()), basisSize=basisSize, neigs=neigs))

    # Get a list of all objects satisfying the query
    def getObjList(self, obj, exactQuery, approxQuery, boundQuery, orderBy=None):
        t1 = [e for e in self.table.find(**exactQuery)]
        listRes = []
        for e in t1:
            if all([abs(e[key]-value)<10.**(-12.) for key,value in approxQuery.iteritems()]) and \
                all([value[0]<=e[key]<value[1] for key,value in boundQuery.iteritems()]):
                try:
                    listRes.append(json.loads(e[obj]))
                except TypeError:
                    listRes.append(e[obj])
        if listRes == []:
            raise ValueError('Value not found:')

        if orderBy==None:
            return listRes
        else:
            return [y for (x,y) in sorted(zip(orderBy, listRes))]

    # Get an object satisfying the query. If multiple are found, the one with maximum attribute "maxAttr"
    def getObj(self, obj, exactQuery, approxQuery, boundQuery, maxAttr):
        t1 = [e for e in self.table.find(**exactQuery)]
        listRes = []
        for e in t1:
            if all([abs(e[key]-value)<10.**(-12.) for key,value in approxQuery.iteritems()]) and \
                all([value[0]<=e[key]<value[1] for key,value in boundQuery.iteritems()]):
                try:
                    listRes.append((e[maxAttr], json.loads(e[obj])))
                except TypeError:
                    listRes.append((e[maxAttr], e[obj]))
        if listRes == []:
            raise ValueError('Value not found')

        return max(listRes, key=lambda x:x[0])[1]


