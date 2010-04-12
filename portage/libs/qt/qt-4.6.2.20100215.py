# -*- coding: utf-8 -*-
import base
import utils
from utils import die
import os
import info
import portage

from Package.QMakePackageBase import *

# ok we need something more here
# dbus-lib
# openssl-lib
# we can't use kde-root/include because we get conflicting includes then
# we have to make sure that the compiler picks up the correct ones!
# --> fetch the two libs above, unpack them into a separate folder

class subinfo(info.infoclass):
    def setTargets( self ):
        # the static version uses one of the stable versions
        self.svnTargets['static'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.5.2-patched|"
        # this is the upcoming 4.7 version with the KDE patches.
        self.svnTargets['master'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git"
        # this version contains the patches against the 4.5.3 release and is recommended for KDE 4.3.X
        self.svnTargets['4.5.3'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.5.3-patched|"
        # this branch contains all the patches and follows the 4.6-stable branch on qt.git - it updates daily
        self.svnTargets['4.6'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6-stable-patched|"
        # those are the stable releases with the KDE patches applied on top
        self.svnTargets['4.6.0'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.0-patched|"
        self.svnTargets['4.6.1'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.1-patched|"
        self.svnTargets['4.6.2'] = "git://gitorious.org/+kde-developers/qt/kde-qt.git|4.6.2-patched|"
        self.svnTargets['4.6.2-mingw-x64'] = "git://gitorious.org/+qt-mingw-w64/qt/qt-mingw-w64-qt.git|4.6_jjc|"
        self.targetSrcSuffix['4.6.2-mingw-x64'] = "x64"
        if (COMPILER == "mingw" or COMPILER == "mingw4") and os.getenv("EMERGE_ARCHITECTURE") == 'x64':
            self.defaultTarget = '4.6.2-mingw-x64'
        else:
            self.defaultTarget = '4.6.2'
        
        ## \todo this is prelimary  and may be changed 
        self.options.package.packageName = 'qt'
        self.options.package.specialMode = True

    def setDependencies( self ):
        self.hardDependencies['virtual/base'] = 'default'
        self.hardDependencies['dev-util/perl'] = 'default'
        self.hardDependencies['testing/mysql-server'] = 'default'
        if os.getenv("EMERGE_ARCHITECTURE") == 'x64':
            self.hardDependencies['win32libs-sources/dbus-src'] = 'default'
            self.hardDependencies['testing/openssl_beta-src'] = 'default'
        elif  COMPILER == "msvc2008":
            self.hardDependencies['win32libs-sources/dbus-src'] = 'default'
            self.hardDependencies['win32libs-bin/openssl'] = 'default'
        else:
            self.hardDependencies['win32libs-bin/dbus'] = 'default'
            self.hardDependencies['win32libs-bin/openssl'] = 'default'

class Package(PackageBase,GitSource, QMakeBuildSystem, KDEWinPackager):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        PackageBase.__init__(self)
        GitSource.__init__(self)
        QMakeBuildSystem.__init__(self)
        KDEWinPackager.__init__(self)
        # get instance of dbus and openssl package
        if os.getenv("EMERGE_ARCHITECTURE") == 'x64':
            self.dbus = portage.getPackageInstance('win32libs-sources','dbus-src')
            self.openssl = portage.getPackageInstance('testing','openssl_beta-src')
        elif COMPILER == "msvc2008":
            self.dbus = portage.getPackageInstance('win32libs-sources','dbus-src')
            self.openssl = portage.getPackageInstance('win32libs-bin','openssl')
        else:
            self.dbus = portage.getPackageInstance('win32libs-bin','dbus')
            self.openssl = portage.getPackageInstance('win32libs-bin','openssl')

        self.mysql_server = portage.getPackageInstance('testing','mysql-server')

    def configure( self, unused1=None, unused2=""):
        self.enterBuildDir()
        self.setPathes()

        os.environ[ "USERIN" ] = "y"
        userin = "y"

        incdirs =  " -I \"" + os.path.join( self.dbus.installDir(), "include" ) + "\""
        libdirs =  " -L \"" + os.path.join( self.dbus.installDir(), "lib" ) + "\""
        incdirs += " -I \"" + os.path.join( self.openssl.installDir(), "include" ) + "\""
        libdirs += " -L \"" + os.path.join( self.openssl.installDir(), "lib" ) + "\""
        incdirs += " -I \"" + os.path.join( self.mysql_server.installDir(), "include" ) + "\""
        libdirs += " -L \"" + os.path.join( self.mysql_server.installDir(), "lib" ) + "\""
        libdirs += " -l libmysql "
        
        configure = os.path.join( self.sourceDir(), "configure.exe" ).replace( "/", "\\" )
        command = r"echo %s | %s -opensource -platform %s -prefix %s " \
          "-qt-gif -qt-libpng -qt-libjpeg -qt-libtiff -plugin-sql-mysql -plugin-sql-odbc " \
          "-no-phonon -qdbus -openssl -dbus-linked " \
          "-fast -ltcg -no-vcproj -no-dsp " \
          "-nomake demos -nomake examples " \
          "%s %s" % ( userin, configure, self.platform, self.installDir(), incdirs, libdirs)
        if self.buildType() == "Debug":
          command += " -debug "
        else:
          command += " -release "
        print "command: ", command
        utils.system( command )
        return True        
        
    def make(self, unused=''):
        libtmp = os.getenv( "LIB" )
        inctmp = os.getenv( "INCLUDE" )

        incdirs =  ";" + os.path.join( self.dbus.installDir(), "include" )
        libdirs =  ";" + os.path.join( self.dbus.installDir(), "lib" )
        incdirs += ";" + os.path.join( self.openssl.installDir(), "include" )
        libdirs += ";" + os.path.join( self.openssl.installDir(), "lib" )
        incdirs += ";" + os.path.join( self.mysql_server.installDir(), "include" )
        libdirs += ";" + os.path.join( self.mysql_server.installDir(), "lib" )
        os.environ[ "INCLUDE" ] = "%s%s" % (inctmp, incdirs)
        os.environ[ "LIB" ] = "%s%s" % (libtmp, libdirs)
        
        QMakeBuildSystem.make(self)
        
        if not libtmp:
            libtmp = ""
        if not libtmp:
            inctmp = ""
        os.environ[ "LIB" ] = libtmp
        os.environ[ "INCLUDE" ] = inctmp
        return True
      

    def install( self ):
        if not QMakeBuildSystem.install(self):
            return False

        # create qt.conf 
        utils.copyFile( os.path.join( self.packageDir(), "qt.conf" ), os.path.join( self.installDir(), "bin", "qt.conf" ) )
        
        # install msvc debug files if available
        if self.buildType() == "Debug" and (self.compiler() == "msvc2005" or self.compiler() == "msvc2008"):
            srcdir = os.path.join( self.buildDir(), "lib" )
            destdir = os.path.join( self.installDir(), "lib" )

            filelist = os.listdir( srcdir )
            
            for file in filelist:
                if file.endswith( ".pdb" ):
                    utils.copyFile( os.path.join( srcdir, file ), os.path.join( destdir, file ) )
                
        return True

if __name__ == '__main__':
    Package().execute()
