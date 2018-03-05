import statefuncs
from scipy import stats
import phi4
import matplotlib.pyplot as plt
from matplotlib import rc
from cycler import cycler
import renorm
import sys
import scipy
import math
import numpy as np
from numpy import pi, sqrt, log, exp
import gc


output = "pdf"

plt.style.use('ggplot')
plt.rc('axes', prop_cycle=(cycler('color', ['r', 'g', 'b', 'y'])))
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

params = {'legend.fontsize': 8, 'lines.markersize':2.5, 'lines.marker':"o"}
plt.rcParams.update(params)

plt.rc('axes', prop_cycle=(
    cycler('marker', ['x', 'o', 'v','x','o'])
    +cycler('linestyle', ['-', '--', ':','-','--'])
    +cycler('markersize', [4.,2.,2.,2.,2.])
    +cycler('color', ['r','b','g','k','c'])
    ))


m = 1
# Number of eigenvalues to compute per sector
neigs = 2


argv = sys.argv
if len(argv) < 2:
    print(argv[0], " <L>")
    sys.exit(-1)

L = float(argv[1])

print("L", L)

# glist = np.linspace(1, 1.5, 30)
glist = np.linspace(0.1, 2, 20)
# glist = np.linspace(0, 0.1, 2)
print("glist", glist)

xmax = max(glist)+0.03
xmin = 0

ETlist = [15, 20, 24]

vevrawlist = {ET:[] for ET in ETlist}
vevrenlist = {ET:[] for ET in ETlist}
Lambda = {ET:[] for ET in ETlist}
phi01 = {ET:[] for ET in ETlist}

for ET in ETlist:

    print("ET: ", ET)

    a = phi4.Phi4(m, L, 1)
    b = phi4.Phi4(m, L, -1)
    a.buildBasis(Emax=ET)
    b.buildBasis(Emax=ET)
    a.computePotential(other=b.basis)
    b.computePotential()
    a.setglist(glist=glist)
    b.setglist(glist=glist)

    print("Basis size even:", len(a.basis.stateList))
    print("Basis size odd:", len(b.basis.stateList))


    a.computeEigval(ET, "raw", neigs=neigs)
    b.computeEigval(ET, "raw", neigs=neigs)
    E0raw = {g: a.eigenvalues[g]["raw"][0] for g in glist}
    E1raw = {g: b.eigenvalues[g]["raw"][0] for g in glist}
    massraw = {g:E1raw[g] - E0raw[g] for g in glist}

    a.computeEigval(ET, "renloc", neigs=neigs, eps=E0raw)
    b.computeEigval(ET, "renloc", neigs=neigs, eps=E1raw)
    E0ren = {g: a.eigenvalues[g]["renloc"][0] for g in glist}
    E1ren = {g: b.eigenvalues[g]["renloc"][0] for g in glist}
    massren = {g:E1ren[g] - E0ren[g] for g in glist}
    Lambda[ET] = np.array([E0ren[g] for g in glist])/L

    # print([(a.V[1]/a.L).dot(b.eigenvectors[g]["renloc"][0]) for g in glist])

    phi01[ET] = np.array([(np.inner(a.eigenvectors[g]["renloc"][0],(a.V[1]/L).dot(b.eigenvectors[g]["renloc"][0]))*sqrt(2*L*massren[g]))**2
        for g in glist])

    gc.collect()


plt.figure(1)
for ET in ETlist:
    plt.plot(glist, phi01[ET], label=r"$\langle 0 \mid \phi \mid 1 \rangle$ , Emax={}".format(ET))


plt.figure(1)
plt.xlim(0,max(glist))
plt.xlabel("g")
plt.ylabel(r"$\langle 0 \mid \phi \mid 1 \rangle$")
s = "phi01vsG_L={}".format(L)
plt.title(r"$L$ = {}".format(L))
plt.legend()
fname = ".{0}".format(output)
# plt.savefig(s+fname, bbox_inches='tight')
plt.savefig(s+fname)

