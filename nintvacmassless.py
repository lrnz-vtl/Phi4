import numpy as np
from time import time
import os
from numpy import log, e
from integrator import *

nitn = 20
neval = 1000000

# nitn = 10
# neval = 20000


# print("Computing O(VV) vacuum diagram...")
print("Computing O(g^2) vacuum energy with m=0 ...")

print("nitn={}, neval={}".format(nitn, neval))

start = time()

# It's the only scale
lam = 1

integ = Phi0_1_m0(nitn, neval)

norm = 1/(48*(4*pi)**3)
res = integ.do(lam)
print("Result: {}, res/norm: {}".format(res,res/norm))

end = time()
print("Time passed: {}".format(end-start))
