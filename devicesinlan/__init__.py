
from datetime import date

__version__ ='2.0.1'
__versiondate__=date(2024, 12, 28)


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

author="Turulomio"
epilog=f"If you like this app, please give me a star in https://github.com/turulomio/devicesinlan/\nDeveloped by {author} 2015-{__versiondate__.year} \xa9"
