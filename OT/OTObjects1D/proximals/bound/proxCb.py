#==================================================
#__________________________________________________

# Copyrigth 2016 A. Farchi and M. Bocquet
# CEREA, joint laboratory Ecole des Ponts ParisTech and EDF R&D

# Code for the paper: Using the Wasserstein distance to compare fields of pollutants:
# Application to the radionuclide atmospheric dispersion of the Fukushima-Daiichi accident
# by A. Farchi, M. Bocquet, Y. Roustan, A. Mathieu and A. Querel

#__________________________________________________
#==================================================

##############
# Class ProxCb
##############
#
# Projector on the boundary condition constrain
#

import time as tm
from .. import projector as proj
from ...grid import grid

class ProxCb( proj.Projector ):
    '''
    Projector on the boundary condition constrain
    '''
    
    def __init__( self ,
                  N , P ,
                  kernel=None ):
        if kernel is None:
            kernel = grid.Boundaries(N,P)

        proj.Projector.__init__( self ,
                                 N , P ,
                                 kernel )

    def __repr__(self):
        return ( 'Projector on the boundary contion constrain space.' )

    def __call__(self, field, overwrite=True):
        if overwrite:
            field.m[0,:]        = self.kernel.spatialBoundaries.bx0[:]
            field.m[self.N+1,:] = self.kernel.spatialBoundaries.bx1[:]
            field.f[:,0]        = self.kernel.temporalBoundaries.bt0[:]
            field.f[:,self.P+1] = self.kernel.temporalBoundaries.bt1[:]
            return field
        else:
            return self(field.copy(), True)

    def test(self,nTest,overwrite=True):
        e = 0.
        for i in xrange(nTest):
            field = grid.StaggeredField.random(self.N, self.P)
            field = self(field,overwrite)
            e += ( field.boundaries() - self.kernel ).LInftyNorm() 
        return e/nTest

    def timing(self,nTiming,overwrite=True):
        t = 0.
        for i in xrange(nTiming):
            field = grid.StaggeredField.random(self.N, self.P)
            time_start = tm.time()
            field = self(field,overwrite)
            t += tm.time() - time_start
        return t
