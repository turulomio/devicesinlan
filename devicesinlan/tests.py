from devicesinlan import __version__
from platform import system as platform_system
from requests import get

def test_statistic_server():
    bad_uuid="00000000-0000-0000-0000-000000000000"
    uuid="d7e6de26-709f-4fcf-bb09-5fec007ce452"
    baseurl="https://devicesinlan.sourceforge.net/php/devicesinlan_installations.php"
## 'https://devicesinlan.sourceforge.net/php/devicesinlan_installations.php?uuid={}&version={}&platform={}'.format(self.settings.value("frmMain/uuid"), __version__, platform_system())

    # Without parameters
    response=get(f"{baseurl}")
    assert response.status_code==200,  response.text
    assert "Some parameter is missing" in response.text
    
    # Only uuid
    response=get(f"{baseurl}?uuid={uuid}")
    assert response.status_code==200,  response.text
    assert "Some parameter is missing" in response.text
    
    # Bad parameters
    response=get(f"{baseurl}?uuid2={uuid}")
    assert response.status_code==200,  response.text
    assert "Some parameter is missing" in response.text
    
    #  Bad uuid
    response=get(f"{baseurl}?uuid={bad_uuid}&version={__version__}&platform={platform_system()}")
    assert response.status_code==200,  response.text
    assert "It's not an uuid" in response.text
    
    #  Empty version
    response=get(f"{baseurl}?uuid={bad_uuid}&version=&platform={platform_system()}")
    assert response.status_code==200,  response.text
    assert "It's not an uuid" in response.text
    
    #  Good request
    response=get(f"{baseurl}?uuid={uuid}&version={__version__}&platform={platform_system()}")
    assert response.status_code==200,  response.text
    assert f"Installation {uuid} updated" in response.text
