import base
import utils
import os
import sys
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['4.0.0'] = 'tags/KDE/4.0.0/kdenetwork'
        self.svnTargets['svnHEAD'] = 'trunk/KDE/kdenetwork'
        for ver in ['61', '62', '63', '64']:
          self.targets['4.0.' + ver] = 'ftp://ftp.rz.uni-wuerzburg.de/pub/unix/kde/unstable/4.0.' + ver + '/src/kdenetwork-4.0.' + ver + '.tar.bz2'
          self.targetInstSrc['4.0.' + ver] = 'kdenetwork-4.0.' + ver
        self.defaultTarget = 'svnHEAD'
    
    def setDependencies( self ):
        self.hardDependencies['kde/kdebase-runtime'] = 'default'
        self.hardDependencies['kdesupport/qca'] = 'default'
        
class subclass(base.baseclass):
    def __init__(self):
        base.baseclass.__init__( self, "" )
        self.subinfo = subinfo()

    def unpack( self ):
        return self.kdeSvnUnpack()

    def compile( self ):
        return self.kdeCompile()

    def install( self ):
        return self.kdeInstall()

    def make_package( self ):
        if not self.buildTarget == 'svnHEAD':
            return self.doPackaging( "kdenetwork", self.buildTarget, True )
        else:
            return self.doPackaging( "kdenetwork", os.path.basename(sys.argv[0]).replace("kdenetwork-", "").replace(".py", ""), True )

if __name__ == '__main__':
    subclass().execute()
