@ECHO ON
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmAbout.ui -o ui/Ui_frmAbout.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmHelp.ui -o ui/Ui_frmHelp.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmMain.ui -o ui/Ui_frmMain.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmSettings.ui -o ui/Ui_frmSettings.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmInterfaceSelector.ui -o ui/Ui_frmInterfaceSelector.py
call c:\Python34\Lib\site-packages\PyQt5\pyuic5.bat ui/frmDeviceCRUD.ui -o ui/Ui_frmDeviceCRUD.py
call c:\Python34\Lib\site-packages\PyQt5\pyrcc5.exe  images/devicesinlan.qrc -o images/devicesinlan_rc.py

