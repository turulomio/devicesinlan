DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/devicesinlan
PREFIXETC=$(DESTDIR)/etc/devicesinlan
PREFIXSHARE=$(DESTDIR)/usr/share/devicesinlan
PREFIXLOCALE=$(DESTDIR)/usr/share/locale/


install:

	pyuic5 ui/frmAbout.ui > ui/Ui_frmAbout.py
	pyuic5 ui/frmHelp.ui > ui/Ui_frmHelp.py
	pyuic5 ui/frmMain.ui > ui/Ui_frmMain.py
	pyuic5 ui/frmSettings.ui > ui/Ui_frmSettings.py

	pyrcc5 images/devicesinlan.qrc > images/devicesinlan_rc.py

	pylupdate5 -noobsolete devicesinlan.pro
	lrelease devicesinlan.pro

	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXETC)
	install -m 644 -o root ui/*.py $(PREFIXLIB)
	install -m 644 -o root images/*.py $(PREFIXLIB)

	install -m 755 -o root devicesinlan.py $(PREFIXBIN)/devicesinlan
	install -m 755 -o root libdevicesinlan.py $(PREFIXLIB)
	install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt INSTALL.txt ieee-oui.txt $(PREFIXSHARE)
	install -m 644 -o root known.txt.dist $(PREFIXETC)

#es
	install -o root -d $(PREFIXLOCALE)/es/LC_MESSAGES/
	xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o po/devicesinlan.pot *.py
	msgmerge -N --no-wrap -U po/es.po po/devicesinlan.pot
	msgfmt -cv -o $(PREFIXLOCALE)/es/LC_MESSAGES/devicesinlan.mo po/es.po

uninstall:
	rm $(PREFIXBIN)/devicesinlan
	rm $(PREFIXETC)/known.txt.dist
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)
	rm $(PREFIXLOCALE)/es/LC_MESSAGES/devicesinlan.mo



