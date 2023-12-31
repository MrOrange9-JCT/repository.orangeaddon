import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import requests
import main

addon = main.Addon()
xbmcaddon = xbmcaddon.Addon()
__url__ = addon.__url__ #+ "?action=movies"
__addon_path__ = addon.__addon_path__
__handle__ = addon.__handle__
__args__ = addon.__args__

def getMovieMetadata(movie_title, requested_metadata = None):
    """Get the metadata of a movie from TMDB"""

    tmdb_id = movie_list[movie_title][0]
    api_key = "-706d6c75628138ee3084133305f15bf6-ee30841333e3084133305f15bf6"

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=es-ES&api_key={api_key.split('-')[1]}"
    response = requests.get(url)
    r = response.json()

    try:
        genres = [r["genres"][0]["name"], r["genres"][1]["name"], r["genres"][2]["name"]]
    except:
        try:
            genres = [r["genres"][0]["name"], r["genres"][1]["name"]]
        except:
            genres = [r["genres"][0]["name"]]

    

    metadata = {"title": r["title"],
                "year": int(r["release_date"].split("-")[0]),
                "aired": r["release_date"],
                "genres": genres,
                "rating": r["vote_average"],
                "duration": r["runtime"] * 60,
                "tagline": r["tagline"],
                "plot": r["overview"],
                "poster": "https://www.themoviedb.org/t/p/original" + r["poster_path"],
                "fanart": "https://www.themoviedb.org/t/p/original" + r["backdrop_path"]}
    
    if requested_metadata != None:
        return metadata[requested_metadata]
    else:
        return metadata

def getMovieList():
    """"Get the updated movie list from Rentry.co"""
    url = "https://rentry.co/OrangeAddon_movie_list/raw"
    response = requests.get(url)

    return response.json()

def getMovieUrl(movie):
    """Get the URL of a movie"""

    url_list = [movie_list[movie][1][0], movie_list[movie][2][0]]
    movie_available = getMovieAvailability(url_list)
    ask_everytime = xbmcaddon.getSettingBool("ask_everytime")
    preffered_host = xbmcaddon.getSetting("preffered_host")

    if movie_available == True:
        if ask_everytime == True:
            preffered_host = None
            dialog = xbmcgui.Dialog()
            list_items = []

            for host in url_list:
                if host.startswith("https://pixeldrain"):
                    list_item = xbmcgui.ListItem("[COLOR darkseagreen]Pixeldrain[/COLOR]")
                    list_item.setArt({"thumb": main.getAddonMedia("pixeldrain.png")})
                    list_item.setInfo("video", {"plot": f"{movie_list[movie][1][1]}"})
                elif host.startswith("https://qiwi"):
                    list_item = xbmcgui.ListItem(f"[COLOR mediumpurple]Qiwi[/COLOR]")
                    list_item.setArt({"thumb": main.getAddonMedia("qiwi.png")})
                    list_item.setInfo("video", {"plot": f"{movie_list[movie][2][1]}"})

                list_items.append(list_item)

            ret = dialog.select("Selecciona un host", list_items, preselect=0, useDetails = True)
        
        if preffered_host == 0 or (ask_everytime == True and ret == 0):
            return url_list[0]
        elif preffered_host == 1 or (ask_everytime == True and ret == 1):
            return url_list[1]
    
    elif movie_available == "Pixeldrain":
        return url_list[0]
    elif movie_available == "Qiwi":
        return url_list[1]
    else:
        return None

def getMovieAvailability(url_list):
    """Check if a movie is available"""

    response_pixeldrain = requests.get(url_list[0] + "/info")
    response_qiwi = requests.get(url_list[1].replace("lol", "gg/file")[:-4])
    
    available = []

    if response_pixeldrain.status_code == 404:
        available.append(False)
    else:
        available.append(True)

    if response_qiwi.status_code == 404:
        available.append(False)
    else:
        available.append(True)

    if available == [True, True]:
        available = True
    elif available == [True, False]:
        available = "Pixeldrain"
    elif available == [False, True]:
        available = "Qiwi"
    else:
        available = False

    return available

def sendUnavailableNotification(movie_title, movie_url):
    """Send a notification to Discord when a movie is unavailable"""

    url = "https://discord.com/api/webhooks/1190607394124877946/oHVLcPbfqm9dBYXPGFz-uzNXwNHNygvy8cG-gULW-VcRHe2QspYqpBNMT9TSaPeTz0dF"

    data = { 
    "content": "<@449992158729076746>",
    "embeds": [
        {
        "title": "⛔ New unavailable link detected!",
        "description": f"Movie: `{movie_title}`\nURL: `{movie_url}`",
        "color": 16711680,
        "author": {
            "name": "OrangeAddon"
        }
        }
    ],
    "attachments": []
    }

    requests.post(url, json = data)

    pass

def updateMovieList():
    """Update the movie list on Rentry.co"""
    url = "https://rentry.co/OrangeAddon_movie_list/raw"
    response = requests.get(url)

    global movie_list
    movie_list = response.json()

    return __url__ + "/update"

def listMovies():
    """List the movies"""
    list_items = []
    progress = xbmcgui.DialogProgress()
    current_movie = 0

    progress.create("Orange Add-on", f"Procesando películas... 0/{len(movie_list)}")
    for movie in movie_list:

        movie_available = getMovieAvailability([movie_list[movie][1][0], movie_list[movie][2][0]])
        url = getMovieUrl(movie)
        movie_metadata = getMovieMetadata(movie)
        current_movie += 1

        print("Processing movie: " + movie_metadata['title'] + " - Available: " + str(movie_available))

        if movie_available == True:
            list_item = xbmcgui.ListItem(f"{movie_metadata['title']} [COLOR blue]({movie_metadata['year']})[/COLOR]")
        elif movie_available == "Pixeldrain":
            list_item = xbmcgui.ListItem(f"{movie_metadata['title']} [COLOR blue]({movie_metadata['year']})[/COLOR][COLOR darkseagreen] [Pixeldrain][/COLOR]")
        elif movie_available == "Qiwi":
            list_item = xbmcgui.ListItem(f"{movie_metadata['title']} [COLOR blue]({movie_metadata['year']})[/COLOR][COLOR mediumpurple] [Qiwi][/COLOR]")
        else:
            list_item = xbmcgui.ListItem(f"[COLOR silver]{movie_metadata['title']}[/COLOR] [COLOR steelblue]({movie_metadata['year']})[/COLOR][COLOR red][B] [NO DISPONIBLE][/B][/COLOR]")
            
        list_item.setInfo("video", {"genre": movie_metadata['genres'],
                                    "rating": movie_metadata['rating'],
                                    "duration": movie_metadata['duration'],
                                    "sorttitle": movie,
                                    "plotoutline": movie_metadata['tagline'],
                                    "plot": f"[COLOR lime]{movie_metadata['rating']}[/COLOR] - [COLOR silver]{str(movie_metadata['genres'])[1:-1]}[/COLOR]\n[I]{movie_metadata['tagline']}[/I]\n\n{movie_metadata['plot']}"})

        list_item.setArt({"poster": getMovieMetadata(movie, 'poster'), 
                    "fanart": getMovieMetadata(movie, 'fanart')})
    
        if not movie_available:
            list_item.setProperties({"IsPlayable": "false"})
            sendUnavailableNotification(movie_metadata['title'], movie_list[movie][1])

        list_items.append((url, list_item, False))

        print("Finished processing movie: " + movie_metadata['title'])

        progress_percent = round(current_movie*100/len(movie_list))
        progress.update(progress_percent, f"Procesando películas... [COLOR blue]{current_movie}/{len(movie_list)} - {progress_percent}%[/COLOR]\n[COLOR silver][I]{movie_metadata['title']} procesada...[/I][/COLOR]")

    progress.close()
    
    xbmcplugin.addDirectoryItems(__handle__, list_items, len(list_items))
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

    print("ALL MOVIES PROCESSED") 


def _main(): 
    update_list = xbmcgui.ListItem("[COLOR lime] - Actualizar lista de películas - [/COLOR]")
    update_icon = main.getAddonMedia("iconRefresh.png")
    update_list.setArt({"thumb": update_icon, "icon": update_icon, "fanart": main.getAddonMedia("fanart.png")})
    print("Fanart: " + xbmcaddon.getAddonInfo('fanart'))

    xbmcplugin.addDirectoryItem(handle=__handle__, url=updateMovieList(), listitem=update_list, isFolder=True)

    listMovies()

    xbmcplugin.endOfDirectory(__handle__)