import bisect
from sys import getsizeof as sizeof
import scipy
from scipy import array, pi, sqrt
from math import floor, factorial
from collections import Counter
from itertools import combinations
import itertools
import numpy as np

tol = 10**-8

# Counter clockwise rotation by 90 degrees
rot = array([[0,-1],[1,0]])
# Reflection wrt x axis
refl = array([[-1,0],[0,1]])




class Helper():
    """ This is just a "helper" class used to conveniently compute energies of
    oscillators and states and so on"""

    def __init__(self, m, L, Emax, Lambda=np.inf):
        self.L = L
        self.m = m
        self.Emax = Emax
        self.Lambda = Lambda

        print(m, L, Emax, Lambda)

        # Maximum of sqrt(nx^2 + ny^2)
        self.nmaxFloat = L/(2*pi)*min(Lambda, sqrt((Emax/2)**2-m**2))
        # Maximum integer wave number
        nmax = floor(self.nmaxFloat)
        self.nmax = nmax

        # Do not shift indices, but use negative indices for slight optimization, which avoids some operations in omega()
        self.omegaMat = np.zeros(shape=(2*nmax+1,2*nmax+1))
        for nx in range(-nmax,nmax+1):
            for ny in range(-nmax,nmax+1):
                self.omegaMat[nx][ny] = self._omega(array([nx,ny]))

        # TODO
        # Dictionary of allowed momenta
        self.allowedWn = set()
        for nx in range(-nmax, nmax+1):
            for ny in range(-nmax, nmax+1):
                if sqrt(nx**2+ny**2) <= self.nmaxFloat:
                    self.allowedWn.add((nx,ny))

        # Set of allowed momenta in first and second quadrants, plus zero momentum
        self.allowedWn12 = set()
        for nx in range(0, nmax+1):
            for ny in range(0, nmax+1):
                if sqrt(nx**2+ny**2) <= self.nmaxFloat:
                    self.allowedWn12.add((nx,ny))

    def torepr2(self, s):
        # XXX Represent the state as sparse vector?
        ret = array([])
        return

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
        return sum(Zn*n for n,Zn in state)

    def _omega(self, n):
        """ Energy corresponding to wavenumber n"""
        m = self.m
        return sqrt(m**2 + self.kSq(n))

    def omega(self, n):
        """ Energy corresponding to wavenumber n"""
        return self.omegaMat[n[0]][n[1]]

    # XXX The use of this function is incorrect in presence of a momentum cutoff. Should replace by a function that
    # finds the minimal energy of state with given total momentum, and single particle momenta smaller than the cutoff
    def minEnergy(self, wn):
        """ Minimal energy to add to a state with total wavenumber WN in order to create a state with total zero momentum """
        if wn[0]==0 and wn[1]==0:
            return 0
        else:
            return self.omega(wn)


    def kSq(self, n):
        """ Squared momentum corresponding to wave number n """
        L = self.L
        return (2*pi/L)**2*np.sum(n**2)

    def occn(self, s):
        """ Occupation number of state """
        return sum([Zn for n,Zn in s])


def reprState(state):
    return [(tuple(n), Zn) for n,Zn in state]

def sortOsc(s):
    """ Sort modes in a state according to momenta """
    return list(sorted(s, key=lambda x: tuple(x[0])))

def rotate(s):
    """ Rotate state counterclockwise by pi/2 """
    return [(np.dot(rot,n),Zn) for n,Zn in s]

def reflect(self, s):
    """ Reflect on state wrt x axis """
    return [(np.dot(refl,n),Zn) for n,Zn in s]


class Basis():
    """ Class used to store and compute a basis of states"""


    def __init__(self, k, stateset, helper):
        """ Standard constructor
        k: parity quantum number
        stateset: set or list of states in representation 1
        helper: Helper object
        """
        self.k = k
        self.helper = helper
        totwn = helper.totwn
        energy = helper.energy
        occn = helper.occn

        self.stateList = sorted(stateset, key=energy)
        self.energyList = [energy(state) for state in self.stateList]

        self.occnList = [occn(state) for state in self.stateList]

        # TODO To implement
        # self.parityList = [int(state==reverse(state)) for state in self.stateList]

        # self.repr2List = [bytes(helper.torepr2(state)) for state in self.stateList]

        self.size = len(self.energyList)
        self.Emax = max(self.energyList)

        # Check assumptions
        el = self.energyList
        assert  all(el[i] <= el[i+1]+tol for i in range(len(el)-1))
        # assert (max(el) <= Emax)
        assert all(sum(totwn(s)**2)==0 for s in self.stateList)
        assert all(1-2*(occn(state)%2)==k for state in self.stateList)


    def irange(self, Emax):
        """ Return max index for states with energy below Emax """
        Emax = Emax + tol
        imax = bisect.bisect_left(self.energyList, Emax)
        return range(imax)


    @classmethod
    def fromScratch(self, m, L, Emax, Lambda=np.inf):
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

        self._occmax = int(floor(Emax/m))

        bases = self.buildBasis(self)
        # Make the representation of each state unique by sorting the oscillators
        bases = {k: [sortOsc(s) for s in bases[k]] for k in (-1,1)}

        return {k: self(k,bases[k],helper) for k in (-1,1)}


    def __len__(self):
        return len(self.stateList)

    def __repr__(self):
        return str([reprState(s) for s in self.stateList])

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
                if tuple(WN) not in allowedWn or E+minEnergy(WN)>Emax:
                    break
                newstate.append(mode)

            ret += self._genNEstatelist(self, newstate, idx+1)

        return ret



    def buildBasis(self):
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

        # XXX Possible optimization: sort first by total wave number, and then by energy?
        NEsl1 = NEstatelist
        NEsl2 = [rotate(s) for s in NEsl1]
        NEsl3 = [rotate(s) for s in NEsl2]
        NEsl4 = [rotate(s) for s in NEsl3]


        # List of energies of the states in quadrants
        NEelist = [energy(s) for s in NEsl1]

        # Lists of total wavenumbers for states in quadrants
        NEwntotlist1 = [totwn(s) for s in NEsl1]
        NEwntotlist2 = [np.dot(rot,wntot) for wntot in NEwntotlist1]
        NEwntotlist3 = [np.dot(rot,wntot) for wntot in NEwntotlist2]
        NEwntotlist4 = [np.dot(rot,wntot) for wntot in NEwntotlist3]

        # Generate dictionary (kx,ky) -> ([idx]) , where idx is an index for the states in the South-East moving quadrant
        SEwnidx = dict()
        for idx, wn in enumerate(NEwntotlist4):
            if tuple(wn) not in SEwnidx.keys():
                SEwnidx[tuple(wn)] = [idx]
            else:
                SEwnidx[tuple(wn)].append(idx)

        ret = {k:[] for k in (-1,1)}

        # Rotate and join NE moving states counterclockwise
        for i1,s1 in enumerate(NEsl1):

            # Keep track of total energy
            E1 = NEelist[i1]
            # Keep track of total wave number
            WN1 = NEwntotlist1[i1]

            # XXX Probably here we can use X (or S) and eliminate some redundancy by choosing i2 >= i1

            for i2,s2 in enumerate(NEsl2):
                E2 = E1 + NEelist[i2]
                WN2 = WN1 + NEwntotlist2[i2]


                # NEstatelist is ordered in energy
                if E2 > Emax:
                    break

                # We need to add at least another particle to have 0 total momentum.
                if tuple(WN2) not in allowedWn or E2+minEnergy(WN2)>Emax:
                    continue

                # XXX Entering this inner cycle is the most expensive part
                # Maybe the checks can be performed in a particular order (do not compute both WN3 and Emax?)
                for i3,s3 in enumerate(NEsl3):
                    E3 = E2 + NEelist[i3]
                    WN3 = WN2 + NEwntotlist3[i3]

                    # NEstatelist is ordered in energy
                    if E3>Emax:
                        break

                    # We need to add at least another particle to have 0 total momentum.
                    # Also, we cannot add anymore negative x momentum or positive y momentum in step 4
                    # XXX omega here is called many times, and it takes a long time in total
                    if WN3[0]>0 or WN3[1]<0 or tuple(WN3) not in allowedWn or E3+minEnergy(WN3)>Emax:
                        continue

                    # There is no states that can cancel the total momentum
                    # XXX is this redundant?
                    if tuple(-WN3) not in SEwnidx.keys():
                        continue

                    for i4 in SEwnidx[tuple(-WN3)]:
                        E4 = E3 + NEelist[i4]
                        WN4 = WN3 + NEwntotlist4[i4]
                        s4 = NEsl4[i4]

                        if E4 > Emax:
                            break

                        if WN4[0]!=0 or WN4[1]!=0:
                            raise RuntimeError("Total momentum should be zero")

                        # Add zero modes
                        for Z0 in itertools.count():
                            Etot = E4 + Z0*m
                            if Etot > Emax:
                                break

                            state = s1+s2+s3+s4
                            if Z0>0:
                                state += [(array([0,0]),Z0)]

                            k = 1-2*(occn(state)%2)
                            ret[k].append(state)

        return {k: ret[k] for k in (-1,1)}