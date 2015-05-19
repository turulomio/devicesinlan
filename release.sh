#!/bin/bash
DIR=spoken-uptime-`cat spoken-uptime.py | grep 'version="'| cut --delimiter='"'  -f 2`
FILE=$DIR.tar.gz
echo "Este script crea el fichero $FILE para ser subido al proyecto"

mkdir $DIR
mkdir $DIR/po

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \
        spoken-uptime.py \
        $DIR

cp      po/es.po \
        po/spoken-uptime.pot\
        $DIR/po

tar cvz $DIR -f $FILE
rm -R $DIR
