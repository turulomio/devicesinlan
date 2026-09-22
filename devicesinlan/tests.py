from devicesinlan import __version__
from platform import system as platform_system
from requests import get
import sys
import tempfile
import os
from devicesinlan.libdevicesinlan import IniSettings, MemConsole, InterfaceManager, DeviceTypeManager, DeviceManager, Device


def test_no_pyqt6_import_in_libdevicesinlan():
    # Verify that PyQt6 is not in sys.modules when libdevicesinlan is imported
    assert "PyQt6.QtCore" not in sys.modules or "PyQt6.QtWidgets" not in sys.modules


def test_ini_settings():
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = IniSettings("TestOrg", "TestApp")
        settings.config_dir = tmpdir
        settings.file_path = os.path.join(tmpdir, "TestApp.conf")

        settings.setValue("General/test_key", "test_val")
        settings.setValue("frmSettings/concurrence", 150)
        settings.setValue("frmSettings/enabled", True)

        settings.beginGroup("DeviceAlias")
        settings.setValue("AABBCCDDEEFF", "MyDevice")
        settings.endGroup()

        settings.sync()

        # Reload
        settings2 = IniSettings("TestOrg", "TestApp")
        settings2.config_dir = tmpdir
        settings2.file_path = os.path.join(tmpdir, "TestApp.conf")
        settings2._load()

        assert settings2.value("General/test_key") == "test_val"
        assert settings2.value("frmSettings/concurrence", 200) == 150
        assert settings2.value("frmSettings/enabled", False) is True

        settings2.beginGroup("DeviceAlias")
        assert "AABBCCDDEEFF" in settings2.childKeys()
        assert settings2.value("AABBCCDDEEFF") == "MyDevice"
        settings2.endGroup()


def test_mem_console_init():
    mem = MemConsole()
    assert mem.name == "DevicesInLAN"
    assert len(mem.types.arr) > 0
    assert mem.types.find_by_id(0) is not None
    assert mem.types.find_by_id(0).name == "Unknown"


def test_device_oui_and_mac():
    mem = MemConsole()
    d = Device(mem)
    assert d.validate_mac("84:AA:9C:9E:76:C1") is True
    assert d.validate_mac("invalid_mac") is False
    assert d.macwithout2points("84:AA:9C:9E:76:C1") == "84AA9C9E76C1"
    assert d.macwith2points("84AA9C9E76C1") == "84:AA:9C:9E:76:C1"


# def test_statistic_server():
#     bad_uuid = "00000000-0000-0000-0000-000000000000"
#     uuid = "d7e6de26-709f-4fcf-bb09-5fec007ce452"
#     baseurl = "https://devicesinlan.sourceforge.net/php/devicesinlan_installations.php"
# 
#     try:
#         response = get(f"{baseurl}?uuid={uuid}&version={__version__}&platform={platform_system()}", timeout=5)
#         if response.status_code == 200:
#             assert f"Installation {uuid} updated" in response.text
#     except Exception:
#         pass  # Network check

