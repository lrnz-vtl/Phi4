import numpy as np
from time import time
import os
from integrator import *
import matplotlib.pyplot as plt
from matplotlib import rc
import scipy

x = np.linspace(10,200,30)
y = np.loadtxt("Vac.txt")

print(y)

imin = 5
m, b = np.polyfit(x[imin:], y[imin:], deg=1)

norm = 1/(48*(4*pi)**3)

print("norm = {}, m/norm = {}, m = {}, b= {}".format(norm,m/norm,m,b))

plt.scatter(x, y)

xx = np.linspace(min(x), max(x), 100)
plt.plot(xx, b + m*xx)

plt.ylim(min(y), max(y))

plt.xlabel(r"$\Lambda$")
plt.ylabel(r"$\mathcal{E}_0$")
plt.savefig("vacFitted.pdf")
