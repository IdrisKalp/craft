import base
import utils
from utils import die
import sys
import info

# see http://eigen.tuxfamily.org/ for more informations

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.hardDependencies['virtual/base'] = 'default'

    def setTargets( self ):
        self.svnTargets['2.0.0'] = 'tags/eigen/2.0.0'
        self.svnTargets['2.0.1'] = 'tags/eigen/2.0.1'
        self.svnTargets['svnHEAD'] = 'trunk/kdesupport/eigen2'
        for i in ['4.3.0', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3']:
            self.svnTargets[ i ] = 'tags/kdesupport-for-4.3/eigen2'
        self.defaultTarget = 'svnHEAD'

class subclass(base.baseclass):
    def __init__( self, **args ):
        base.baseclass.__init__( self, args=args )
        # header-only package
        self.createCombinedPackage = True
        self.subinfo = subinfo()

    def unpack( self ):
        return self.kdeSvnUnpack()

    def compile( self ):
        self.kdeCustomDefines = "-DBUILD_TESTS=OFF"
        return self.kdeCompile()

    def install( self ):
        return self.kdeInstall()

    def make_package( self ):
        if self.buildTarget == "svnHEAD":
            return self.doPackaging( "eigen2" )
        else:
            return self.doPackaging( "eigen2", self.buildTarget, True )

if __name__ == '__main__':
    subclass().execute()
