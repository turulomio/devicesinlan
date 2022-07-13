# DevicesInLan [![PyPI - Downloads](https://img.shields.io/pypi/dm/devicesinlan?label=Pypi%20downloads)](https://pypi.org/project/devicesinlan/) [![Github - Downloads](https://shields.io/github/downloads/turulomio/devicesinlan/total?label=Github%20downloads )](https://github.com/turulomio/devicesinlan/)

Snapshots
=========

![Snapshot](https://github.com/turulomio/devicesinlan/blob/master/doc/devicesinlan_snapshots_01.png)

Links
=====
Doxygen documentation:
  * http://turulomio.users.sourceforge.net/doxygen/devicesinlan/
  
Main developer web page:
  * https://github.com/turulomio

App statistics
  * http://devicesinlan.sourceforge.net/php/devicesinlan_statistics.php

Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* https://pypi.org/project/PyQt5/, as the main library.
* https://pypi.org/project/pywin32/, to create shortcuts.
* https://github.com/secdev/scapy, for Scapy scan methods.

Install in Linux
================
If you use Gentoo you can find a ebuild in https://github.com/Turulomio/myportage/tree/master/net-analyzer/devicesinlan

If you use other distribution compatible con pip, you need to install PyQt5 and devicesinlan with the following commands:

`pip install PyQt5`

`pip install devicesinlan`

You need to install PyQt5 first, because is not in Linux setup.py dependencies due to it doesn't use standard setup tools. So for compatibility reasons with distributions like Gentoo, we use this additional step.

Install in Windows as a python module
=====================================
You need to install Python from https://www.python.org and add it to the PATH

You must open a console with Administrator privileges and type:

`pip install devicesinlan`

If you want to create a Desktop shortcut to launch Xulpymoney you must write in a console:

`devicesinlan_shortcut.exe`

Install in Windows as a standalone application
==============================================
You need to download devicesinlan-X.X.X.exe to use console script or devicesinlan_gui-X.X.X.exe to use gui app, from github release

Just execute it. It's an standalone application, it took some time to launch due to it uncompress code first ;)

Authors
=======

* Turulomio (<turulomio@yahoo.es>). Idea and spanish translation

Changelog
=========

devicesinlan 0.1.0 20150519
---------------------------
- Basic funcionality
- Spanish translation

devicesinlan 0.2.0 20150519
---------------------------
- Improved class developing
- Add argument to select net interfaz
- MAC address matching is now case insensitive

devicesinlan 0.3.0 20150519
---------------------------
- Catched exception with arp-scan

devicesinlan 0.4.0 20150524
---------------------------
- Known devices are now sorted by alias and listed
- Net devices are now sorted by IP address
- You can add and remove Known devices from command line
- Net devices list doesn't show duplicates

devicesinlan 0.5.0 20150617
---------------------------
- Console output shows the number of devices in the lan

devicesinlan 0.6.0 20150819
---------------------------
- Added ping search support
- Made my own arp-scanner
- Added ieee-oui.txt database with get-oui from arp-scan

devicesinlan 0.7.0 20160717
---------------------------
- Added UI.
- First Windows verion

devicesinlan 0.8.0 20170118
---------------------------
- Added more device types
- Works -a, -r, -l again
- Improved apps dependencies

devicesinlan 0.9.0 20170205
---------------------------
- Pretty list in console
- Device type added to lists

devicesinlan 0.10.0 20170206
----------------------------
- Replaced Color class by colorama package
- There is Color in Windows console reports

devicesinlan 0.11.0 20170207
----------------------------
- Replaced Thread with PoolThreadExecutor
- Added setting to set concurrence
- Improved console reports

devicesinlan 1.0.0 20170208
---------------------------
- Project man page created
- Save/load xml lists
- Check for updates
- Gets installation statistcs

devicesinlan 1.0.1 20170209
---------------------------
- Improved statistics system
- Fix little bugs

devicesinlan 1.0.2 20170222
---------------------------
- Added logging system
- Statistics work now in console mode
- Add a Device can input the type now
- Add to console mode --load --save --reset

devicesinlan 1.1.0 20170226
---------------------------
- Logging is deactivated by default
- Statistics system now sends platform

devicesinlan 1.2.0 20171228
---------------------------
- Now, You don't need to be superuser to run DevicesInLan
- Improved documentation and spanish translation
- Netifaces removed
- Removed buggy shortcut
- Added faster socket to check arp
- Changed distribution system from innoreader to setup

devicesinlan 1.3.0 20180121
---------------------------
- Solved translation path bug in linux
- Current device is showed in blue
- Now there is an executable for console and other for ui
- Created documentation for both executables
- Removed man2html dependency

devicesinlan 1.4.0 20181116
---------------------------
- Changed Makefile.py to setuptools
- Now setup.py pyinstaller generates a standalone windows executable

devicesinlan 1.4.1 20181116
---------------------------
- Fix little bugs with windows installation

devicesinlan 1.5.0 20181119
---------------------------
- Improved code quality

devicesinlan 1.6.0 20181126
---------------------------
- Added desktop files in Linux
- arp command removes its absolut path to work in all Linux distributions
- Fixed detection of new versions

devicesinlan 1.7.0 20190803
---------------------------
- Fixed mixed colors in console outputs.
- Added windows console and gui distributions.

devicesinlan 1.8.0 20191230
---------------------------
- Added scapy methods.
- Fix bug loading unescaped data from XML.
- Addapting code to reusing project.
- Improved doc and translations

devicesinlan 1.9.0 20190109
---------------------------
- Added 'Report issue' action.
- Windows console version now ask for a key to end app.
- Added used software information in about dialog.

devicesinlan 1.9.2 20220713
---------------------------
- Updated to last qt5

