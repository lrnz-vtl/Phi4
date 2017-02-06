##cython: profile=True
##cython: linetrace=True
##distutils: define_macros=CYTHON_TRACE_NOGIL=1
import gc
from sys import getsizeof as sizeof
import scipy, numpy
from math import factorial, floor, sqrt
import statefuncs
from statefuncs import Basis
import itertools
from statefuncs import Helper
from itertools import combinations, islice, permutations
from scipy import exp, pi
from scipy.special import binom
import bisect
from oscillators import *
cimport cython
from cpython cimport array as array
import array

cdef double tol = 0.000000001

parityFactors = [[1, sqrt(2)],[1/sqrt(2),1]]

def filterDlist(dlist, nd, ntot, nmax):
    # TODO This can be sped up with the n-SUM algorithm
    if nd==ntot:
        return sum(dlist)==0
    elif nd==ntot-1:
        return abs(sum(dlist))<=nmax
    else:
        return True


# TODO The speed optimization resulting from using the N-Sum algorithm could be important
def gendlists(state, nd, ntot, nmax):
    """ Generates a list of all the possible combinations of momenta in the state that
    can be annihilated
    state: input state in representation 1
    nd: number of annihilation operators (number of modes to annihilate)
    ntot: total number of annihilation and creation operators
    nmax: maximal wavenumber of the "lookup" basis
    """

    x = itertools.chain.from_iterable(([n]*Zn for n,Zn in state))

    dlists = set(tuple(y) for y in combinations(x,nd))
    return (dlist for dlist in dlists if filterDlist(dlist, nd, ntot, nmax))


def computeME(basis, i, lookupbasis, helper, statePos, Erange,
    ignKeyErr, nd, nc, dlistPos, oscFactors, oscList, oscEnergies):
        """ Compute the matrix elements by applying all the oscillators in the operator
        to an element in the basis
        basis: set of states on which the operator acts
        i: index of the state in the basis
        lookupbasis: basis of states corresponding to the column indexes of the matrix
        helper: Helper instance
        statePos: dictionary where the keys are states in representation 2 (in tuple form)
        and the values are their position in the basis
        ignKeyErr: this must be set to True if the action of an oscillators on an input state
        can generate a state not in lookupbasis. This applies only in the computation of Vhh.
        Otherwise it should be set to False
        """

        cdef double x
        cdef array.array statevec, newstatevec
        cdef char *cstatevec
        cdef char *cnewstatevec
        cdef char[:,:] osc
        cdef float[:] oscFactorsSub
        cdef char Zc, Zd, nmax
        cdef int z, ii, jjj
        cdef double[:,:,:] normFactors

        # List of columns indices of generated basis elements
        col = []
        # List of partial matrix elements
        data = []

        # I define these local variables outside the loops for performance reasons
        e = basis.energyList[i]
        p = basis.parityList[i]
        state = basis.stateList[i]

        statevec = array.array('b', helper.torepr2(state))
        cstatevec = statevec.data.as_chars
        
        parityList = lookupbasis.parityList
        nmax = helper.nmax
        normFactors = helper.normFactors
        Emin, Emax = Erange

        # cycle over all the sets of momenta that can be annihilated
# XXX Check: we replaced lookupbasis.helper.nmax with helper.nmax
        for dlist in gendlists(state, nd, nd+nc, nmax):

            k = dlistPos[dlist]

# Only select the oscillators such that the sum of the state and oscillator energies
# lies within the bounds of the lookupbasis energies
            imin = bisect.bisect_left(oscEnergies[k], Emin-e-tol)
            imax = bisect.bisect_left(oscEnergies[k], Emax-e+tol)

            if imax <= imin:
                continue

            oscFactorsSub = array.array('f', oscFactors[k][imin:imax])
            oscListSub = oscList[k][imin:imax]

            for z in range(len(oscListSub)):
                osc = oscListSub[z]

                newstatevec = array.copy(statevec)
                cnewstatevec = newstatevec.data.as_chars

                x = oscFactorsSub[z]

                for ii in range(osc.shape[0]):
                    Zc = osc[ii, 1]
                    Zd = osc[ii, 2]
                    jj = osc[ii, 0]+nmax
                    cnewstatevec[jj] += Zc-Zd
                    x *= normFactors[Zc, Zd, cstatevec[jj]]

                if ignKeyErr:
                    try:
                        j = statePos[bytes(newstatevec)]
                    except KeyError:
                        continue
                else:
                    j = statePos[bytes(newstatevec)]

                x *= parityFactors[p][parityList[j]]
                data.append(x)
                col.append(j)

        return col, data


