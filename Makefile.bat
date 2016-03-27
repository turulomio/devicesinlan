@ECHO ON
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmAbout.ui -o ui/Ui_frmAbout.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmHelp.ui -o ui/Ui_frmHelp.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmMain.ui -o ui/Ui_frmMain.py
call c:\Python34\Lib\site-packages\PyQt5\pyrcc5.exe  images/devicesinlan.qrc -o images/devicesinlan_rc.py

call c:\Python34\python.exe c:\Python34\Tools\i18n\msgfmt.py -o po/devicesinlan.mo po/es.po

