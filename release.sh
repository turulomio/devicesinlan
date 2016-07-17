#!/bin/bash
DIR=devicesinlan-`cat libdevicesinlan.py | grep 'version="'| cut --delimiter='"'  -f 2`
FILE=$DIR.tar.gz
echo "Este script crea el fichero $FILE para ser subido al proyecto"

mkdir $DIR
mkdir $DIR/images
mkdir $DIR/i18n
mkdir $DIR/ui

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \
        devicesinlan.py \
        ieee-oui.txt \
        $DIR

cp      images/*.png \
        images/*.ico \
        images/*.qrc \
        $DIR/images

cp      i18n/*.ts \
        $DIR/i18n

cp      ui/*.ui \
        ui/frm*.py \
        $DIR/ui

tar cvz $DIR -f $FILE
rm -R $DIR
