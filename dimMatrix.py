import inspect
import os
import phi4
import sys
import math
import scipy
from time import process_time
from statefuncs import *

k = 1
m = 1.

argv = sys.argv

args = "<L> <ET> <ELmin> <ELmax>"
if len(argv) < 5:
    print("python", argv[0], args)
    sys.exit(-1)

L = float(argv[1])
ET = float(argv[2])
ELmin = float(argv[3])
ELmax = float(argv[4])

ELlist = scipy.linspace(ELmin, ELmax, int(ELmax-ELmin+1))

print(ELlist)

a = phi4.Phi4(m,L)
a.buildBasis(Emax=ET)

subbasis = Basis(k, a.basis[k].stateList[:50], a.basis[k].helper)

print("{Ebar, len(a.VHH[k].M.data), a.nops, a.basisH[k].size, time}")

for EL in ELlist:

    a.genHEBasis(k, subbasis, ET, EL)

    start = process_time()
    a.computeVhh(k, subbasis)
    end = process_time()

    # print("HE basis size", a.basisH[k].size)

    print("{",EL,",", len(a.Vhh[k].M.data),",",a.nops,",",a.basisH[k].size,",",
            end-start,"},")