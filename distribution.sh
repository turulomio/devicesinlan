#!/bin/bash
rm -Rf build
mkdir -p build/src

VERSION=`cat libdevicesinlan.py | grep 'version="'| cut --delimiter='"'  -f 2`
TIME=`date +%Y%m%d%H%M%S`
CWD=`pwd`
touch build/$VERSION-$TIME dist/$VERSION-$TIME   #Genera fichero con versión y hora de distribución
DIRSRCLINUX=build/src # Se instala con un makefile
FILE=devicesinlan-src-$VERSION.tar.gz


echo "Este script crea el fichero $FILE para ser subido a sourceforge"

mkdir $DIRSRCLINUX/i18n
mkdir $DIRSRCLINUX/images
mkdir $DIRSRCLINUX/ui

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \
        devicesinlan.py \
        libdevicesinlan.py \
        known.txt.dist \
        ieee-oui.txt \
        devicesinlan.desktop \
        $DIRSRCLINUX

cp      i18n/*.ts \
        $DIRSRCLINUX/i18n

cp      images/*.png \
        images/*.qrc \
        $DIRSRCLINUX/images

cp      ui/frm* \
        $DIRSRCLINUX/ui

echo "  * Comprimiendo codigo fuente linux..."
cd build/src
tar cvz  -f $CWD/build/$FILE * -C $CWD/build/src > /dev/null
cd $CWD

####### binaries linux
python3 setup.py build

