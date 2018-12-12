import bisect
from sys import getsizeof as sizeof
import scipy
from scipy import array, pi, sqrt
from math import floor, factorial
from collections import Counter
from itertools import combinations
import itertools
import numpy as np
from symmetry import *

tol = 10**-10

def sortOsc(s):
    """ Sort modes in a state according to momenta """
    return list(sorted(s, key=lambda x: tuple(x[0])))


# XXX Is this necessary?
def toCanonical(state):
    """ Transorm the state in representation 1 to canonical ordering of the momenta """
    return list(sorted(((tuple(n), Zn) for n,Zn in state), key=lambda x: x[0]))


class Helper():
    """ This is just a "helper" class used to conveniently compute energies of
    oscillators and states and so on"""

    def __init__(self, m, L, Emax, Lambda=np.inf, noscmax=8):
        """ noscmax: max number of oscillators """

        self.L = L
        self.m = m
        self.Emax = Emax
        self.Lambda = Lambda

        # Maximum of sqrt(nx^2 + ny^2)
        self.nmaxFloat = L/(2*pi)*min(Lambda, sqrt((Emax/2)**2-m**2))+tol
        # Maximum integer wave number
        nmax = floor(self.nmaxFloat)
        self.nmax = nmax

        # Do not shift indices, but use negative indices for slight optimization, which avoids some operations in omega()
        self.omegaMat = np.zeros(shape=(2*nmax+1,2*nmax+1))
        for nx in range(-nmax,nmax+1):
            for ny in range(-nmax,nmax+1):
                self.omegaMat[nx][ny] = self._omega(array([nx,ny]))

        # Dictionary of allowed momenta ((kx,ky) -> idx), where idx is used as index of states in representation 2
        self.allowedWn = dict()
        idx = 0
        for nx in range(-nmax, nmax+1):
            for ny in range(-nmax, nmax+1):
                if sqrt(nx**2+ny**2) <= self.nmaxFloat:
                    self.allowedWn[(nx,ny)] = idx
                    idx += 1

        # Set of allowed momenta in first and second quadrants, plus zero momentum
        self.allowedWn12 = set()
        for nx in range(-nmax, nmax+1):
            if nx < 0:
                nymin = 1
            else:
                nymin = 0
            for ny in range(nymin, nmax+1):
                if sqrt(nx**2+ny**2) <= self.nmaxFloat:
                    self.allowedWn12.add((nx,ny))

        occmax = floor(Emax/m+tol)
        self.normFactors = scipy.zeros(shape=(noscmax+1,noscmax+1,occmax+1))
        for c in range(noscmax+1):
            for d in range(noscmax+1):
                for n in range(occmax+1):
                    if d <= n:
                        self.normFactors[c,d,n] = \
                            sqrt(factorial(n)*factorial(n-d+c)/factorial(n-d)**2)
                    else:
                        self.normFactors[c,d,n] = scipy.nan

    def torepr2(self, s):
        ret = [0]*len(self.allowedWn)
        for n,Zn in s:
            ret[self.allowedWn[tuple(n)]] = Zn
        return ret


    def oscEnergy(self, wnlist):
        """ Energy of an oscillator (ordered tuple of momenta) """
        return sum(self.omega(n) for n in wnlist)

    # XXX This is slow
    def energy(self, state):
        """ Computes energy of state in Repr1 """
        return sum(Zn*self.omega(n) for n,Zn in state)

    def totwn(self, state):
        if state==[]:
            return array([0,0])
        return sum([Zn*np.array(n) for n,Zn in state])

    def _omega(self, n):
        """ Energy corresponding to wavenumber n"""
        m = self.m
        return sqrt(m**2 + self.kSq(n))

    def omega(self, n):
        """ Energy corresponding to wavenumber n"""
        return self.omegaMat[n[0]][n[1]]

    # XXX The use of this function is incorrect in presence of a momentum cutoff. Should replace by a function that
    # finds the minimal energy of state with given total momentum, and single particle momenta smaller than the cutoff
    # XXX Incorrect !!
    def minEnergy(self, wn, z0min=0):
        """ Minimal energy to add to a state with total wavenumber "wn" in order
        to create a state with total zero momentum
        z0min: minimum number of particles that must be added """

        m = self.m

        if wn[0]==0 and wn[1]==0:
            return m*z0min
        else:
            # return self.omega(wn) + m*(z0min-1)
            # XXX Bugged
            return self.omega(wn)

    def kSq(self, n):
        """ Squared momentum corresponding to wave number n """
        L = self.L
        return (2*pi/L)**2*np.sum(n**2)

    def occn(self, s):
        """ Occupation number of state """
        return sum([Zn for n,Zn in s])


class Basis():
    """ Class used to store and compute a basis of states"""


    def __init__(self, k, stateList, statePos, helper, sym=False, ncomp=None):
        """ Standard constructor
        k: parity quantum number
        stateset: set or list of states in representation 1
        helper: Helper object
        sym: take symmetries into account, and project out singlet states
        """
        self.k = k
        self.helper = helper
        totwn = helper.totwn
        energy = helper.energy
        occn = helper.occn
        self.Emax = helper.Emax
        self.sym = sym

        self.size = len(stateList)

        # Retrieve the transformation of the indices to get lists sorted in energy
        energyList = [energy(state) for state in stateList]
        idx = np.argsort(np.array(energyList))
        # Reverse indices
        idx2 = {j:i for i,j in enumerate(idx) }

        # Remap the indices
        self.stateList = [stateList[idx[i]] for i in range(self.size)]
        self.energyList = [energyList[idx[i]] for i in range(self.size)]
        self.statePos = {state: idx2[i] for state,i in statePos.items()}

        # Symmetry types
        if sym:
            self.ncomp = [ncomp[idx[i]] for i in range(self.size)]


        self.occnList = [occn(state) for state in self.stateList]

        # Check assumptions
        el = self.energyList
        assert  all(el[i] <= el[i+1]+tol for i in range(len(el)-1))
        assert (max(el) <= self.Emax+tol)
        assert all(sum(totwn(s)**2)==0 for s in self.stateList)
        assert all(1-2*(occn(state)%2)==k for state in self.stateList)


    def irange(self, Emax):
        """ Return max index for states with energy below Emax """
        Emax = Emax + tol
        imax = bisect.bisect_left(self.energyList, Emax)
        return range(imax)


    @classmethod
    def fromScratch(self, m, L, Emax, Lambda=np.inf, sym=False):
        """ Builds the truncated Hilbert space up to cutoff Emax from scratch, in repr1
        m: mass
        L: side of the torus
        Emax: maximal energy of the states
        """

        self.helper = Helper(m, L, Emax, Lambda)
        helper = self.helper
        occn = helper.occn
        m = helper.m
        energy = helper.energy
        self.sym = sym

        self._occmax = int(floor(Emax/m)+tol)

        self._buildBasis(self)

        # Make the representation of each state unique by sorting the oscillators
        self.bases = {k: [sortOsc(s) for s in self.bases[k]] for k in (-1,1)}

        if sym:
            return {k: self(k, self.bases[k], self.statePos[k],  helper, sym=sym, ncomp=self.ncomp[k]) for k in (-1,1)}
        else:
            return {k: self(k, self.bases[k], self.statePos[k],  helper, sym=sym) for k in (-1,1)}


    def __len__(self):
        return len(self.stateList)

    def __repr__(self):
        return str([toCanonical(s) for s in self.stateList])

    def _genNEwnlist(self, Emax, Lambda):
        """ Generate list of North-East moving wave numbers momenta, nx > ny >= 0,
        sorted in energy, below cutoffs Emax and Lambda """

        helper = self.helper
        omega = helper.omega
        allowedWn = helper.allowedWn

        self.NEwnlist = []

        for ny in itertools.count():
            for nx in itertools.count(1):

                n = array([nx,ny])

                if tuple(n) not in allowedWn:

                    if nx==1:
                        self.NEwnlist.sort(key=lambda n: omega(n))
                        return
                    else:
                        break

                self.NEwnlist.append(n)

        raise RuntimeError("Shouldn't get here")


    def _genNEstatelist(self, NEstate=[], idx=0):
        """ Recursive function generating all North-East moving states in Repr 1 starting from NEstate, by adding
        any number of particles with momentum self.NEwnlist[idx] """

        helper = self.helper
        m = helper.m
        Emax = helper.Emax
        omega = helper.omega
        allowedWn = helper.allowedWn
        energy = helper.energy
        totwn = helper.totwn
        minEnergy = helper.minEnergy

        if idx == len(self.NEwnlist):
            # TODO Could Sort oscillators inside state here
            return [NEstate]

        # Two-dimensional NE-moving wave number
        n = self.NEwnlist[idx]

        # Keep track of current energy
        E = energy(NEstate)
        # Keep track of current total wave number
        WN = totwn(NEstate)

        ret = []

        for Zn in itertools.count():
            newstate = NEstate[:]

            if Zn>0:
                mode = (n, Zn)
                E += omega(n)
                WN += n
                # We need to add at least another particle to have 0 total momentum.
                # XXX Check
                if tuple(WN) not in allowedWn or E+minEnergy(WN)>Emax+tol:
                    break
                newstate.append(mode)

            ret += self._genNEstatelist(self, newstate, idx+1)

        return ret


    def _buildBasis(self):
        """ Generates the basis starting from the list of RM states, in repr1 """

        helper = self.helper
        omega = helper.omega

        m = helper.m
        energy = helper.energy
        totwn = helper.totwn
        Emax = helper.Emax
        Lambda = helper.Lambda
        allowedWn = helper.allowedWn
        minEnergy = helper.minEnergy
        occn = helper.occn

        # Generate list of all NE moving momenta
        self._genNEwnlist(self, Emax, Lambda)

        # Generate list of all NE moving states, and sort them by energy
        NEstatelist = self._genNEstatelist(self)
        NEstatelist.sort(key=lambda s: energy(s))
        # List of energies of the states in quadrants
        NEelist = [energy(s) for s in NEstatelist]

        NEsl1 = NEstatelist
        NEsl2 = [rotate(s) for s in NEsl1]

        # Lists of total wavenumbers for states in quadrants
        NEwntotlist1 = [totwn(s) for s in NEsl1]
        NEwntotlist2 = [np.dot(rot,wntot) for wntot in NEwntotlist1]

        # North-moving states in first and second quadrants
        Nsl12 = {}

        # Rotate and join NE moving states counterclockwise
        for i1,s1 in enumerate(NEsl1):

            # Keep track of total energy
            E1 = NEelist[i1]
            # Keep track of total wave number
            WN1 = NEwntotlist1[i1]

            # XXX The commented part is wrong. Can we save any more time?
            # for i2 in range(i1, len(NEsl2)):
                # s2 = NEsl2[i2]
            for i2,s2 in enumerate(NEsl2):

                E2 = E1 + NEelist[i2]
                WN2 = WN1 + NEwntotlist2[i2]

                # NEstatelist is ordered in energy
                if E2 > Emax+tol:
                    break

                # We need to add at least another particle to have 0 total momentum.
                if tuple(WN2) not in allowedWn or E2+minEnergy(WN2)>Emax+tol:
                    continue

                s12 = s1+s2

                if tuple(WN2) not in Nsl12.keys():
                    Nsl12[tuple(WN2)] = [s12]
                else:
                    Nsl12[tuple(WN2)].append(s12)

        # Create states moving north or south, and join them pairwise
        Nsl12 = [list(sorted(states, key=energy)) for states in Nsl12.values()]
        N12elist = [[energy(s) for s in states] for states in Nsl12]
        N12occlist = [[occn(s) for s in states] for states in Nsl12]

        # List of states in Representation 1, which are not related by symmetries when self.sym = False
        self.bases = {k:[] for k in (-1,1)}
        idx = {k:0 for k in (-1,1)}
        # Dictionary of indices for states in Representation 2, modded by symmetry
        self.statePos = {k:{} for k in (-1,1)}
        # Number of Fock states in the singlet representation of state. This is used to compute the appropriate normalization
        # factors
        self.ncomp = {k:[] for k in (-1,1)}

        for i, states in enumerate(Nsl12):

            for j1, s in enumerate(states):
                s34 = rotate(rotate(s))
                e34 = N12elist[i][j1]
                o34 = N12occlist[i][j1]

                # Save some time by using reflection
                for j2 in range(j1, len(states)):
                    s12 = states[j2]
                    e = e34 + N12elist[i][j2]
                    o = o34 + N12occlist[i][j2]

                    if e > Emax+tol:
                        break

                    state = s34 + s12
                    # The state already exists (for every Z0), when taking symmetries into account
                    k = 1-2*(o%2)
                    if bytes(helper.torepr2(state)) in self.statePos[k]:
                        continue
                    transStates = genTransformed(state, helper)
                    # Number of Fock space states in the singlet state
                    self.ncomp[k].append(len(transStates))
                    self.bases[k].append(toCanonical(state))
                    for rs in transStates:
                        self.statePos[k][bytes(rs)] = idx[k]
                    idx[k] += 1

                    # Add zero modes
                    for Z0 in range(1, int(floor((Emax-e)/m+tol))+1):
                        state = s34 + s12 + [(array([0,0]),Z0)]
                        occtot = o + Z0
                        k = 1-2*(occtot%2)
                        self.ncomp[k].append(len(transStates))
                        self.bases[k].append(toCanonical(state))

                        for rs in transStates:
                            # Add zero modes for each of the transformed states
                            rs[allowedWn[(0,0)]] = Z0
                            self.statePos[k][bytes(rs)] = idx[k]

                        idx[k] += 1


        return
