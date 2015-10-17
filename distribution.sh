#!/bin/bash
rm -Rf build
rm -Rf dist
mkdir -p build/src dist

VERSION=`cat devicesinlan.py | grep 'version="'| cut --delimiter='"'  -f 2`
TIME=`date +%Y%m%d%H%M%S`
CWD=`pwd`
touch build/$VERSION-$TIME dist/$VERSION-$TIME   #Genera fichero con versión y hora de distribución
DIRSRCLINUX=build/src # Se instala con un makefile
PYTHONVERSION=3.4

echo "Este script crea el fichero $FILE para ser subido a sourceforge"
echo "Debe tener instalado una versión de wine y sobre el haber instalado"
echo "  - Python (ultima version)"
echo "  - PyQt4 (ultima version serie 5)"


mkdir $DIRSRCLINUX
mkdir $DIRSRCLINUX/po

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \                                                                                                                                                                        
        devicesinlan.py \                                                                                                                                                                     
        devicesinlan.jpg \
        known.txt.dist \
        ieee-oui.txt \
        $DIRSRCLINUX

cp      po/es.po \
        po/devicesinlan.pot\
        $DIRSRCLINUX/po

tar cvz $DIRSRCLINUX -f $FILE
rm -R $DIRSRCLINUX


echo "  * Comprimiendo codigo fuente linux..."
cd build/src
tar cvz  -f $CWD/dist/devicesinlan-src-linux-$VERSION.tar.gz * -C $CWD/build/src > /dev/null
cd $CWD

####### binaries linux
python3 setup.py build
cd build/exe.linux-x86_64-$PYTHONVERSION
tar cvz  -f $CWD/dist/devicesinlan-bin-linux-$VERSION.tar.gz * -C $CWD/build/exe.linux-x86_64-$PYTHONVERSION > /dev/null
cd $CWD

###### binaries windows
DIR=build/exe.win32-$PYTHONVERSION
mkdir -p $DIR
cp glparchis.iss $DIR
#sed -i -e "s:XXXXXXXX:$VERSION:" build/exe.win32-$PYTHONVERSION/glparchis.iss #Se copia para que el setup.bat funcione bien
wine $HOME/.wine/drive_c/python34/python.exe setup.py bdist_msi
cd $DIR
wine $HOME/.wine/drive_c/Program\ Files\ \(x86\)/Inno\ Setup\ 5/ISCC.exe /o$CWD/dist /DVERSION_NAME=$VERSION glparchis.iss

