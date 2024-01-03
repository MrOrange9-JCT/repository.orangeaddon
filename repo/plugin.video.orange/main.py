import sys
import xbmc
import os
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import requests
import urllib
import urllib.parse as urlparse
from modules import movies

xbmcaddon = xbmcaddon.Addon("plugin.video.orange")

class Addon:

    __handle__ = int(sys.argv[1])
    __url__ = sys.argv[0]
    __args__ = urlparse.parse_qs(sys.argv[2][1:])
    __addon_path__ = xbmcvfs.translatePath(xbmcaddon.getAddonInfo('path'))
        
addon = Addon()
__url__ = addon.__url__
__addon_path__ = addon.__addon_path__
__handle__ = addon.__handle__
__args__ = addon.__args__

xbmcplugin.setContent(__handle__, "movies")

def buildUrl(query):
    return __url__ + '?' + urllib.urlencode(query)

def getAddonMedia(media: str = None):
    """Get the path of a media file from the add-on resources folder"""

    if media != None:
        if media != "fanart.png" or media != "icon.png":
            return os.path.join(__addon_path__, "resources", "media", media)
        else:
            return os.path.join(__addon_path__, "resources", media)
    else:
        return None

def mainMenu():
    """Main menu"""
    xbmcplugin.addDirectoryItem(__handle__, __url__ + "?folder=movies", xbmcgui.ListItem("Películas"), isFolder=True)
    xbmcplugin.addDirectoryItem(__handle__, __url__ + "?button=settings", xbmcgui.ListItem("Ajustes"), isFolder=True)

    xbmcplugin.endOfDirectory(__handle__)

if __name__ == "__main__":
    folder = __args__.get("folder", None)
    button = __args__.get("button", None)
    
    """if folder is None:
        mainMenu()
    elif folder == "movies":
        movies.main()

    if button == "settings":
        xbmcaddon.openSettings()"""
    movies._main()