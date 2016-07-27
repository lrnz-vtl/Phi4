import scipy
import scipy.sparse.linalg
import scipy.sparse
import scipy.interpolate


# TODO use metaclasses?
class Matrix():
    """ Matrix with specified state bases for row and column indexes.
    This class is useful to easily extract submatrices """
    def __init__(self, basisI, basisJ, M=None):
        self.basisI = basisI
        self.basisJ = basisJ

        if(M == None):
            self.M = scipy.sparse.coo_matrix((basisI.size, 1))
        else:
            self.M = M
            self.check()

    def addColumn(self, newcolumn):
        m = scipy.sparse.coo_matrix(newcolumn).transpose()
        self.M = scipy.sparse.hstack([self.M,m])

    def finalize(self):
        self.M = self.M.tocsc()[:,1:].tocoo()
        self.check()

    def check(self):
        if self.M.shape != (self.basisI.size, self.basisJ.size):
            raise ValueError('Matrix shape inconsistent with given bases')

    def __add__(self, other):
        """ Sum of matrices """
        return Matrix(self.basisI, self.basisJ, self.M+other.M)
    def __sub__(self, other):
        return Matrix(self.basisI, self.basisJ, self.M-other.M)

    def __rmul__(self, other):
        """ Multiplication of matrix with matrix or number"""
        if(other.__class__ == self.__class__):
            return Matrix(other.basisI, self.basisJ, other.M*self.M)
        else:
            return Matrix(self.basisI, self.basisJ, self.M*float(other))

    def __mul__(self, other):
        """ Multiplication of matrix with matrix or number"""
        if(other.__class__ == self.__class__):
            return Matrix(self.basisI, other.basisJ, self.M*other.M)
        else:
            return Matrix(self.basisI, self.basisJ, self.M*float(other))

    def to(self, form):
        """ Format conversion """
        return Matrix(self.basisI, self.basisJ, self.M.asformat(form))

    # XXX inefficient
    def sub(self, subBasisI=None, subBasisJ=None):
        """ This extracts a submatrix given a subspace of
        the initial vector space, both for rows and columns
        """

        if subBasisI != None and subBasisJ != None:
            rows = [self.basisI.lookup(state)[1]  for state in subBasisI]
            columns = [self.basisJ.lookup(state)[1]  for state in subBasisJ]
            return Matrix(subBasisI, subBasisJ,
                    self.M.tocsr()[scipy.array(rows)[:,scipy.newaxis],scipy.array(columns)])

        elif subBasisI != None and subBasisJ == None:
            rows = [self.basisI.lookup(state)[1]  for state in subBasisI]
            return Matrix(subBasisI, self.basisJ, self.M.tocsr()[scipy.array(rows),:])

        elif subBasisI == None and subBasisJ != None:
            columns = [self.basisJ.lookup(state)[1]  for state in subBasisJ]
            return Matrix(self.basisI, subBasisJ, self.M.tocsr()[:,scipy.array(columns)])

        else:
            return self

    def transpose(self):
        return Matrix(self.basisJ, self.basisI, self.M.transpose())
    def inverse(self):
        return Matrix(self.basisJ, self.basisI, scipy.sparse.linalg.inv(self.M.tocsc()))
