#!/bin/bash
DIR=devicesinlan-`cat libdevicesinlan.py | grep 'version = "'| cut --delimiter='"'  -f 2`
BUILDDIR=build/$DIR
FILE=$DIR.tar.gz
echo "Este script crea el fichero $FILE para ser subido al proyecto"

rm -Rf $BUILDDIR

mkdir -p $BUILDDIR
mkdir $BUILDDIR/images
mkdir $BUILDDIR/i18n
mkdir $BUILDDIR/ui
mkdir $BUILDDIR/doc

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \
        libdevicesinlan.py \
        devicesinlan.py \
        devicesinlan.pro \
        devicesinlan.html \
        devicesinlan.desktop \
        ieee-oui.txt \
        $BUILDDIR

cp      doc/*.1 \
        doc/*.html
        $BUILDDIR/doc

cp      images/*.png \
        images/*.ico \
        images/*.qrc \
        $BUILDDIR/images

cp      i18n/*.ts \
        $BUILDDIR/i18n

cp      ui/*.ui \
        ui/frm*.py \
        $BUILDDIR/ui

cd build
tar cvz $DIR -f $FILE
cd ..

## BIN LINUX
python3 setup.py build