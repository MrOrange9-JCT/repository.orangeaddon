import sys
import xbmc
import xbmcgui
import xbmcplugin
import requests
import urllib
import urllib.parse as urlparse
from modules import movies

class Addon:

    __handle__ = int(sys.argv[1])
    __url__ = sys.argv[0]
    __args__ = urlparse.parse_qs(sys.argv[2][1:])
        
addon = Addon()
__url__ = addon.__url__
__handle__ = addon.__handle__
__args__ = addon.__args__

xbmcplugin.setContent(__handle__, "movies")

__args__.get("action", None)

def buildUrl(query):
    return __url__ + '?' + urllib.urlencode(query)

def mainMenu():
    """Main menu"""
    xbmcplugin.addDirectoryItem(__handle__, __url__ + "?action=", xbmcgui.ListItem("Películas"), isFolder=True)
    xbmcplugin.addDirectoryItem(__handle__, __url__ + "", xbmcgui.ListItem("Ajustes"), isFolder=True)

    xbmcplugin.endOfDirectory(__handle__)

if __name__ == "__main__":
    movies.main()