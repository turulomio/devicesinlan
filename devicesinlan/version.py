## @brief Package with xulpymoney version information
import datetime

__version__ ='1.9.2'
__versiondate__=datetime.date(2022,7, 13)


## This function expectss __version__= 'VERSION' file
## @return String removeversion or None if it couln't be found
def get_remote(path):
    from urllib.request import urlopen
    try:
        web=urlopen(path).read().decode("UTF-8")
    except:
        return None
    if web==None:
        return None
    for line in web.split("\n"):
        if line.find("__version__")!=-1:
            return web.split("'")[1]
    return None
