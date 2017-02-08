DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/devicesinlan
PREFIXSHARE=$(DESTDIR)/usr/share/devicesinlan
PREFIXPIXMAPS=$(DESTDIR)/usr/share/pixmaps/
PREFIXAPPLICATIONS=$(DESTDIR)/usr/share/applications/
PREFIXMAN=$(DESTDIR)/usr/share/man/

install:
	pyuic5 ui/frmAbout.ui > ui/Ui_frmAbout.py
	pyuic5 ui/frmHelp.ui > ui/Ui_frmHelp.py
	pyuic5 ui/frmMain.ui > ui/Ui_frmMain.py
	pyuic5 ui/frmSettings.ui > ui/Ui_frmSettings.py
	pyuic5 ui/frmInterfaceSelector.ui > ui/Ui_frmInterfaceSelector.py
	pyuic5 ui/frmDeviceCRUD.ui > ui/Ui_frmDeviceCRUD.py
	pyrcc5 images/devicesinlan.qrc > images/devicesinlan_rc.py

	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXPIXMAPS)
	install -o root -d $(PREFIXAPPLICATIONS)
	install -o root -d $(PREFIXMAN)/man1
	install -o root -d $(PREFIXMAN)/es/man1
	install -o root -d $(PREFIXMAN)/fr/man1
	install -o root -d $(PREFIXMAN)/ro/man1
	install -o root -d $(PREFIXMAN)/ru/man1
	install -m 644 -o root ui/*.py $(PREFIXLIB)
	install -m 644 -o root images/*.py $(PREFIXLIB)
	install -m 644 -o root images/devicesinlan.png $(DESTDIR)/usr/share/pixmaps/
	install -m 644 -o root devicesinlan.desktop $(DESTDIR)/usr/share/applications/

	install -m 755 -o root devicesinlan.py $(PREFIXBIN)/devicesinlan
	install -m 755 -o root libdevicesinlan.py libmangenerator.py $(PREFIXLIB)
	install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt INSTALL.txt ieee-oui.txt doc/devicesinlan*.html $(PREFIXSHARE)
	install -m 644 -o root i18n/*.qm $(PREFIXSHARE)
	install -m 644 -o root doc/devicesinlan.en.1 $(PREFIXMAN)/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.es.1 $(PREFIXMAN)/es/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.fr.1 $(PREFIXMAN)/fr/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.ro.1 $(PREFIXMAN)/ro/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.ru.1 $(PREFIXMAN)/ru/man1/devicesinlan.1

uninstall:
	rm $(PREFIXBIN)/devicesinlan
	rm $(PREFIXAPPLICATIONS)/devicesinlan.desktop
	rm $(PREFIXPIXMAPS)/devicesinlan.png
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)
	rm -Rf $(PREFIXMAN)/man1/devicesinlan.1
	rm -Rf $(PREFIXMAN)/es/man1/devicesinlan.1
	rm -Rf $(PREFIXMAN)/fr/man1/devicesinlan.1
	rm -Rf $(PREFIXMAN)/ro/man1/devicesinlan.1
	rm -Rf $(PREFIXMAN)/ru/man1/devicesinlan.1

man:
	install -o root -d $(PREFIXMAN)/man1
	install -o root -d $(PREFIXMAN)/es/man1
	install -o root -d $(PREFIXMAN)/fr/man1
	install -o root -d $(PREFIXMAN)/ro/man1
	install -o root -d $(PREFIXMAN)/ru/man1
	pylupdate5 -noobsolete devicesinlan.pro
	lrelease -qt5 devicesinlan.pro
	python3 mangenerator.py --language en
	python3 mangenerator.py --language fr
	python3 mangenerator.py --language ro
	python3 mangenerator.py --language ru
	python3 mangenerator.py --language es
	install -m 644 -o root doc/devicesinlan.en.1 $(PREFIXMAN)/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.es.1 $(PREFIXMAN)/es/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.fr.1 $(PREFIXMAN)/fr/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.ro.1 $(PREFIXMAN)/ro/man1/devicesinlan.1
	install -m 644 -o root doc/devicesinlan.ru.1 $(PREFIXMAN)/ru/man1/devicesinlan.1
