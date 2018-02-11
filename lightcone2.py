import statefuncs
import phi4
import matplotlib.pyplot as plt
from matplotlib import rc
from cycler import cycler
import renorm
import sys
import scipy
import math
import numpy as np


# Chabysheva prescription for comparing LC and ET data
nval = 70

gLClist = np.array([0., 0.0120368, 0.0240735, 0.0361103, 0.048147, 0.0601838, 0.0722205, 0.0842573, 0.096294, 0.108331, 0.120368, 0.132404, 0.144441, 0.156478, 0.168515, 0.180551, 0.192588, 0.204625, 0.216662, 0.228698, 0.240735, 0.252772, 0.264809, 0.276845, 0.288882, 0.300919, 0.312956, 0.324992, 0.337029, 0.349066, 0.361103, 0.373139, 0.385176, 0.397213, 0.40925, 0.421286, 0.433323, 0.44536, 0.457397, 0.469433, 0.48147, 0.493507, 0.505544, 0.51758, 0.529617, 0.541654, 0.553691, 0.565727, 0.577764,
0.589801, 0.601838, 0.613874, 0.625911, 0.637948, 0.649985, 0.662021, 0.674058, 0.686095, 0.698132, 0.710168, 0.722205, 0.734242, 0.746279, 0.758315, 0.770352, 0.782389, 0.794426, 0.806462, 0.818499, 0.830536, 0.842573, 0.854609, 0.866646, 0.878683, 0.89072, 0.902757, 0.914793, 0.92683, 0.938867, 0.950904, 0.96294, 0.974977, 0.987014, 0.999051, 1.01109, 1.02312, 1.03516, 1.0472, 1.05923, 1.07127, 1.08331, 1.09534, 1.10738, 1.11942, 1.13145, 1.14349, 1.15553, 1.16757, 1.1796, 1.19164, 1.20368,
1.21571, 1.22775, 1.23979, 1.25182, 1.26386, 1.2759, 1.28793, 1.29997, 1.31201, 1.32404, 1.33608, 1.34812, 1.36015, 1.37219, 1.38423, 1.39626, 1.4083, 1.42034, 1.43237, 1.44441, 1.45645, 1.46848, 1.48052, 1.49256, 1.50459, 1.51663, 1.52867, 1.5407, 1.55274, 1.56478, 1.57681, 1.58885, 1.60089, 1.61292, 1.62496, 1.637, 1.64904, 1.66107, 1.67311, 1.68515, 1.69718, 1.70922, 1.72126, 1.73329, 1.74533, 1.75737, 1.7694, 1.78144, 1.79348, 1.80551, 1.81755, 1.82959, 1.84162, 1.85366, 1.8657,
1.87773, 1.88977, 1.90181, 1.91384, 1.92588, 1.93792, 1.94995, 1.96199, 1.97403, 1.98606, 1.9981, 2.01014, 2.02217, 2.03421, 2.04625, 2.05828, 2.07032, 2.08236, 2.0944])[:nval]


msqLClist = np.array([1., 0.999788, 0.999168, 0.998165, 0.996796, 0.99508, 0.993031, 0.990661, 0.987982, 0.985002, 0.981731, 0.978176, 0.974345, 0.970242, 0.965873, 0.961243, 0.956356, 0.951217, 0.945827, 0.940191, 0.934311, 0.928189, 0.921827, 0.915227, 0.908391, 0.901319, 0.894014, 0.886476, 0.878705, 0.870703, 0.862469, 0.854004, 0.845309, 0.836383, 0.827225, 0.817837, 0.808217, 0.798365, 0.78828, 0.777962, 0.76741, 0.756623, 0.745601, 0.734341, 0.722843, 0.711106, 0.699128, 0.686908, 0.674444,
0.661734, 0.648778, 0.635573, 0.622117, 0.608408, 0.594444, 0.580224, 0.565744, 0.551003, 0.535997, 0.520725, 0.505184, 0.489371, 0.473283, 0.456917, 0.440269, 0.423338, 0.40612, 0.38861, 0.370806, 0.352703, 0.334299, 0.315588, 0.296568, 0.277233, 0.257579, 0.237601, 0.217295, 0.196656, 0.175678, 0.154356, 0.132685, 0.110659, 0.088271, 0.0655154, 0.0423854, 0.0188742, -0.00502548, -0.0293212, -0.0540208, -0.0791326, -0.104665, -0.130628, -0.157031, -0.183883, -0.211197, -0.238982,
-0.267252, -0.296019, -0.325297, -0.3551, -0.385446, -0.416351, -0.447833, -0.479914, -0.512617, -0.545967, -0.587201, -0.745183, -0.904438, -1.06499, -1.22688, -1.39016, -1.55488, -1.72111, -1.88892, -2.05839, -2.22965, -2.40279, -2.57797, -2.75535, -2.93511, -3.11745, -3.30261, -3.49084, -3.68239, -3.87752, -4.07648, -4.27949, -4.48674, -4.69837, -4.91448, -5.13511, -5.36028, -5.59, -5.82424, -6.063, -6.30625, -6.554, -6.80623, -7.06295, -7.32415, -7.58984, -7.85999, -8.13461,
-8.41368, -8.69718, -8.9851, -9.27741, -9.57412, -9.8752, -10.1806, -10.4905, -10.8046, -11.1232, -11.446, -11.7733, -12.1049, -12.4408, -12.7809, -13.1254, -13.4741, -13.8269, -14.1839, -14.5448, -14.9098, -15.2786, -15.6512, -16.0276, -16.4076, -16.7911, -17.1781, -17.5685, -17.9621, -18.3591, -18.7592])[:nval]


msqLClistExtr = np.array([1., 0.999787, 0.999167, 0.998162, 0.996792, 0.995073, 0.993018, 0.990642, 0.987954, 0.984962, 0.981676, 0.9781, 0.974241, 0.970104, 0.965701, 0.96102, 0.95607, 0.950869, 0.945388, 0.939641, 0.93366, 0.927384, 0.920888, 0.914078, 0.906991, 0.899713, 0.892074, 0.88427, 0.876059, 0.867718, 0.858909, 0.850018, 0.840578, 0.831118, 0.821002, 0.81095, 0.800617, 0.789999, 0.779093, 0.767896, 0.756405, 0.744616, 0.732526, 0.720131, 0.707427, 0.694409, 0.681075, 0.667419, 0.653437,
0.639124, 0.624475, 0.609486, 0.594152, 0.578466, 0.562424, 0.54602, 0.529248, 0.512103, 0.494577, 0.476665, 0.458361, 0.439657, 0.420546, 0.401022, 0.381077, 0.360704, 0.339894, 0.31864, 0.296933, 0.274765, 0.252127, 0.229009, 0.205404, 0.1813, 0.156687, 0.131556, 0.105896, 0.0796944, 0.0529413, 0.0256242, -0.00226926, -0.0307518, -0.0598369, -0.0895382, -0.11987, -0.150848, -0.182486, -0.214803, -0.247814, -0.281536, -0.31599, -0.351194, -0.387169, -0.423936, -0.461518,
-0.499939, -0.539223, -0.579399, -0.620494, -0.66254, -0.705567, -0.749612, -0.794712, -0.840908, -0.888246, -0.936774, -0.991022, -1.11862, -1.31174, -1.5683, -1.86286, -2.20153, -2.56296, -2.95981, -3.37537, -3.80286, -4.2454, -4.69567, -5.15299, -5.61393, -6.07406, -6.53904, -6.99382, -7.45283, -7.91143, -8.35523, -8.80465, -9.22485, -9.65204, -10.0876, -10.5113, -10.915, -11.3279, -11.7499, -12.1394, -12.5182, -12.9069, -13.3058, -13.7151, -14.1347, -14.5649, -15.0057, -15.4569,
-15.9185, -16.3906, -16.8728, -17.3652, -17.8676, -18.3799, -18.9019, -19.4336, -19.9749, -20.5258, -21.0861, -21.6559, -22.2351, -22.8236, -23.4215, -24.0285, -24.6447, -25.2699, -25.9041, -26.547, -27.1985, -27.8585, -28.5267, -29.203, -29.8872, -30.5791, -31.2785, -31.9852, -32.6991, -33.4199, -34.1475, -34.8817])[:nval]


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
neigs = 2

# Perturbative mass to order g^3
def mpert(g):
    return np.sqrt(1-1.5*g**2 + 2.86460*g**3)

argv = sys.argv
if len(argv) < 3:
    print(argv[0], " <L> <ET>")
    sys.exit(-1)

L = float(argv[1])
ET = float(argv[2])


print("L, ET", L, ET)


def main():

    # Compute VEVs
    a = phi4.Phi4(m, L, 1)
    a.buildBasis(Emax=ET)
    a.computePotential()
    a.setglist(glist=gLClist)
    a.computeEigval(ET, "raw", neigs=neigs)
    E0raw = {g: a.eigenvalues[g]["raw"][0] for g in gLClist}
    a.computeEigval(ET, "renloc", neigs=neigs, eps=E0raw)
    vevrenlist = np.array([a.vev[g]["renloc"] for g in gLClist])

    # Compute effective mass squared
    meffsqList = 1/(1-12*gLClist*vevrenlist)

    # Effective ET coupling (in units where bare ET mass=1)
    gETeff = gLClist*meffsqList


    # Compute gap in Equal time
    a = phi4.Phi4(m, L, 1)
    a.buildBasis(Emax=ET)
    a.computePotential()
    a.setglist(glist=gETeff)
    b = phi4.Phi4(m, L, -1)
    b.buildBasis(Emax=ET)
    b.computePotential()
    b.setglist(glist=gETeff)

    a.computeEigval(ET, "raw", neigs=neigs)
    b.computeEigval(ET, "raw", neigs=neigs)
    E0raw = {g: a.eigenvalues[g]["raw"][0] for g in gETeff}
    E1raw = {g: b.eigenvalues[g]["raw"][0] for g in gETeff}
    gapETraw = np.array([E1raw[g] - E0raw[g] for g in gETeff])
    a.computeEigval(ET, "renloc", neigs=neigs, eps=E0raw)
    b.computeEigval(ET, "renloc", neigs=neigs, eps=E1raw)
    E0ren = {g: a.eigenvalues[g]["renloc"][0] for g in gETeff}
    E1ren = {g: b.eigenvalues[g]["renloc"][0] for g in gETeff}
    gapETren = np.array([E1ren[g] - E0ren[g] for g in gETeff])

# Naive lightcone gap
    gapLCnaive = np.sqrt(np.interp(gETeff, gLClist, msqLClistExtr))

# Light cone mass gap, normalized to appropriate units
    gapLCnorm = np.sqrt(msqLClist*meffsqList)
# Extrapolated Light cone mass gap, normalized to appropriate units
    gapLCnormExtr = np.sqrt(msqLClistExtr*meffsqList)


    plt.figure(1)
    plt.plot(gETeff, gapETraw, label="ET raw")
    plt.plot(gETeff, gapETren, label="ET ren")
    plt.plot(gETeff, gapLCnorm, label=r"$LC, \Delta_{\rm max}=34$")
    plt.plot(gETeff, gapLCnormExtr, label=r"$LC, \Delta_{\rm max}=\infty$")
    plt.plot(gETeff, gapLCnaive, label="LC naive")
    plt.plot(gETeff, mpert(gETeff), label=r"$o(g^3)$", color='y', linestyle="--", marker='o', markersize=1)

    # plt.figure(2)
    # vevrawlist = np.array([vevraw[g] for g in glist])
    # vevrenlist = np.array([vevren[g] for g in glist])
    # plt.plot(glist, gLCeffNorm, label="LC eff coupling")
    # plt.plot(glist, vevrenlist, label="VEV ren")
    # plt.xlim(xmin, xmax)

    plt.figure(1)
    plt.xlim(0.01,1.01)
    plt.ylim(0.8,1.01)
    plt.xlabel(r"$g$")
    plt.ylabel(r"$M$")
    plt.title(r"$E_T$ = {} , $L$ = {}".format(ET, L))
    plt.legend()
    fname = ".{0}".format(output)
    s = "gapvsG_prescr2_ET={}_L={}".format(ET,L)
    # plt.savefig(s+fname, bbox_inches='tight')
    plt.savefig(s+fname)

    # plt.figure(2)
    # plt.xlim(0.1,1.01)
    # plt.ylim(0.1,0.7)
    # plt.xlabel("g")
    # # plt.ylabel(r"$\langle\phi^2\rangle$")
    # plt.ylabel(r"$g_{\rm eff}$")
    # plt.title(r"$E_T$ = {} , $L$ = {}".format(ET, L))
    # plt.legend()
    # fname = ".{0}".format(output)
    # s = "VEV_ET={}_L={}".format(ET,L)
    # # plt.savefig(s+fname, bbox_inches='tight')
    # plt.savefig(s+fname)


main()
