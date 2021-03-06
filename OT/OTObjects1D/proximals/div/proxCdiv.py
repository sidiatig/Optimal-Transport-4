#==================================================
#__________________________________________________

# Copyrigth 2016 A. Farchi and M. Bocquet
# CEREA, joint laboratory Ecole des Ponts ParisTech and EDF R&D

# Code for the paper: Using the Wasserstein distance to compare fields of pollutants:
# Application to the radionuclide atmospheric dispersion of the Fukushima-Daiichi accident
# by A. Farchi, M. Bocquet, Y. Roustan, A. Mathieu and A. Querel

#__________________________________________________
#==================================================

################
# Class ProxCdiv
################
#
# Projector on the divergence constrain
#

import time as tm
import numpy as np
import scipy.fftpack as fft
from .. import projector as proj
from ...grid import grid

class ProxCdiv( proj.Projector ):
    '''
    Projector on the divergence constrain
    '''
    
    def __init__( self ,
                  N , P ,
                  kernel=None ):
        if kernel is None:
            kernel = grid.Divergence(N,P)

        proj.Projector.__init__( self ,
                                 N , P ,
                                 kernel )

        x = np.arange(N+1)
        t = np.arange(P+1)

        X,T = np.meshgrid(x,t,indexing='ij')
        self.eigvalues = ( 2. * (N**2) * ( 1. - np.cos( np.pi * ( X + 1. ) / ( N + 2. ) ) ) +
                           2. * (P**2) * ( 1. - np.cos( np.pi * ( T + 1. ) / ( P + 2. ) ) ) )


    def __repr__(self):
        return ( 'Projector on the divergence constrain space.' )

    def A(self, field):
        return field.divergence()

    def TA(self, div):
        return div.Tdivergence()

    def inverseATA(self, divergence):
        div = divergence.div

        div = 0.5*fft.dst(div, type=1, axis=0)
        div = 0.5*fft.dst(div, type=1, axis=1)

        div = div / self.eigvalues

        div = fft.dst(div, type=1, axis=0) / ( self.N + 2. )
        div = fft.dst(div, type=1, axis=1) / ( self.P + 2. )

        divergence.div = div
        return divergence

    def testInverse(self,nTest):
        e = 0.

        for i in xrange(nTest):
            div1 = grid.Divergence.random(self.N, self.P)

            div2 = div1.copy()
            div2 = self.inverseATA(div2)
            div2 = self.ATA(div2)
            e += ( div1 - div2 ).LInftyNorm()

            div2 = div1.copy()
            div2 = self.ATA(div2)
            div2 = self.inverseATA(div2)
            e += ( div1 - div2 ).LInftyNorm()

        return e/nTest

    def test(self,nTest):
        e = 0.
        for i in xrange(nTest):
            field = grid.StaggeredField.random(self.N, self.P)
            field = self(field)
            e += ( self.A(field) - self.kernel ).LInftyNorm()
        return e/nTest

    def timing(self,nTiming):
        t = 0.
        for i in xrange(nTiming):
            field = grid.StaggeredField.random(self.N, self.P)
            time_start = tm.time()
            field = self(field)
            t += tm.time() - time_start
        return t
