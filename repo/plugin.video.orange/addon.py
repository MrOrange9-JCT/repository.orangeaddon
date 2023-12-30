import sys
import xbmc
import xbmcgui
import xbmcplugin
import requests

__handle__ = int(sys.argv[1])
__url__ = sys.argv[0]

xbmcplugin.setContent(__handle__, "movies")

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

def getMovieAvailability(movie_url):
    """Check if a movie is available"""

    response = requests.get(movie_url + "/info")

    if response.status_code == 404:
        return False
    else:
        return True


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

# Movies along with their TMDB ID
movie_list = getMovieList()

update_list = xbmcgui.ListItem("[COLOR lime] - Actualizar lista de películas - [/COLOR]")
xbmcplugin.addDirectoryItem(handle=__handle__, url=updateMovieList(), listitem=update_list, isFolder=True)

for movie in movie_list:

    url = movie_list[movie][1]
    movie_metadata = getMovieMetadata(movie)
    movie_available = getMovieAvailability(url)

    print("Processing movie: " + movie_metadata['title'] + " - Available: " + str(movie_available))

    if movie_available:
        list_item = xbmcgui.ListItem(f"{movie_metadata['title']} [COLOR blue]({movie_metadata['year']})[/COLOR]")
    else:
        list_item = xbmcgui.ListItem(f"[COLOR silver]{movie_metadata['title']}[/COLOR] [COLOR steelblue]({movie_metadata['year']})[/COLOR] [COLOR red] [NO DISPONIBLE][/COLOR]")
        
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
        
        xbmcplugin.addDirectoryItem(handle=__handle__, url=None, listitem=list_item)

    else:
        xbmcplugin.addDirectoryItem(handle=__handle__, url=url, listitem=list_item)

    print("Finished processing movie: " + movie_metadata['title'])

print("ALL MOVIES PROCESSED")    

xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

xbmcplugin.endOfDirectory(__handle__)