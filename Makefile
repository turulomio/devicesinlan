DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/devicesinlan
PREFIXSHARE=$(DESTDIR)/usr/share/devicesinlan
PREFIXPIXMAPS=$(DESTDIR)/usr/share/pixmaps/
PREFIXAPPLICATIONS=$(DESTDIR)/usr/share/applications/

install:

	pyuic5 ui/frmAbout.ui > ui/Ui_frmAbout.py
	pyuic5 ui/frmHelp.ui > ui/Ui_frmHelp.py
	pyuic5 ui/frmMain.ui > ui/Ui_frmMain.py
	pyuic5 ui/frmSettings.ui > ui/Ui_frmSettings.py
	pyuic5 ui/frmInterfaceSelector.ui > ui/Ui_frmInterfaceSelector.py
	pyuic5 ui/frmDeviceCRUD.ui > ui/Ui_frmDeviceCRUD.py
	pyrcc5 images/devicesinlan.qrc > images/devicesinlan_rc.py

	pylupdate5 -noobsolete devicesinlan.pro
	lrelease -qt5 devicesinlan.pro

	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXPIXMAPS)
	install -o root -d $(PREFIXAPPLICATIONS)
	install -m 644 -o root ui/*.py $(PREFIXLIB)
	install -m 644 -o root images/*.py $(PREFIXLIB)
	install -m 644 -o root images/devicesinlan.png $(DESTDIR)/usr/share/pixmaps/
	install -m 644 -o root devicesinlan.desktop $(DESTDIR)/usr/share/applications/

	install -m 755 -o root devicesinlan.py $(PREFIXBIN)/devicesinlan
	install -m 755 -o root libdevicesinlan.py $(PREFIXLIB)
	install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt INSTALL.txt ieee-oui.txt $(PREFIXSHARE)
	install -m 644 -o root i18n/*.qm $(PREFIXSHARE)

uninstall:
	rm $(PREFIXBIN)/devicesinlan
	rm $(PREFIXAPPLICATIONS)/devicesinlan.desktop
	rm $(PREFIXPIXMAPS)/devicesinlan.png
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)



