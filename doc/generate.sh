#en
cp -R sphinx sphinx-en
cd sphinx-en
sed -i 's%= build%= ../en/%g' Makefile
make  html
sed -i "s%master_doc = 'index'%master_doc = 'guide'%g" source/conf.py
make  man
cd ..
rm -Rf sphinx-en

##es
cd sphinx
make gettext
sphinx-intl update -p build/gettext -l es
cd ..

cp -R sphinx sphinx-es
cd sphinx-es
sed -i 's%= build%= ../es/%g' Makefile
make -e SPHINXOPTS="-D language='es'" html
sed -i "s%master_doc = 'index'%master_doc = 'guide'%g" source/conf.py
make -e SPHINXOPTS="-D language='es'" man
cd ..
rm -Rf sphinx-es

