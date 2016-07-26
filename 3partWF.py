import sys
import matplotlib.pyplot as plt
import scipy
import math
import json
from scipy import pi, log, array, sqrt
from math import factorial
from matplotlib import rc
import database
from statefuncs import Basis
import itertools

occmax = 3
output = "pdf"

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


""" Takes the a coefficient of the discretized wafe functions and renormalizes it
    according to the basis element.
    Works for general particle number """
# XXX possible mistakes here
def normalizeWF(c, v):
    # Bose symmetry
    c *= scipy.prod([factorial(n) for n in v.occs])/factorial(v.occ)
    # Normalization of Fock space states
    c *= 1/sqrt(scipy.prod([factorial(n) for n in v.occs]))
    # Spatial parity symmetry
    if v.isParityEigenstate() == False:
        c *= 1/sqrt(2)

    return c

def main(argv):
    args = " <L> <Emax> <g>"
    if len(argv) < 4:
        print(argv[0], args)
        return -1

    L = float(argv[1])
    Emax = float(argv[2])
    g = float(argv[3])

    plt.figure(1)
    params = {'legend.fontsize': 8}
    plt.rcParams.update(params)

    db = database.Database()
    exactQuery = {"ren":"raw", "k":-1, "occmax":occmax}
    approxQuery = {"g":g, "Emax":Emax, "L":L}
    eigv = db.getObjList("eigv", exactQuery=exactQuery, approxQuery=approxQuery)[0]

    basis = Basis.fromScratch(m=1, L=L, Emax=Emax, k=-1, occmax=occmax)
    # Select only 3 particles basis states
    indexList = [i for i in range(len(basis)) if basis[i].occ==3]
    basis3p = [basis[i] for i in indexList]

    # Select only coefficients of 3 particle basis states
    wf = [eigv[0][i] for i in indexList]

    # Renormalize wave function
    wf = array([normalizeWF(c,v) for c,v in zip(wf, basis3p)])

    # Construct variables in the form [k1,k2,f(k1,k2,k3)]
    data = []
    for c, v in zip(wf, basis3p):
        # List of momenta of wavenumbers in the state
        wavenumbers = list(itertools.chain(*[[wn]*v[wn] for wn in v.wnList()]))

        # Take all possible inequivalent pairs of wave numbers, including symmetrization
        s = set(itertools.combinations(wavenumbers,2))
        s |= set((b,a) for a,b in s)
        s |= set((-a,-b) for a,b in s)

        for a,b in s:
            data.append(array([a*2*pi/L,b*2*pi/L,c]))

    data = array(data)
    scipy.savetxt("data/wf3p_g={0:g}_L={1:g}_E={2:g}_nmax={3:d}.csv"
            .format(g,L,Emax,occmax),
            data.reshape(1,data.size),delimiter=",")


if __name__ == "__main__":
    main(sys.argv)
