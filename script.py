import requests
import json
import regex
from dotenv import load_dotenv
load_dotenv()

import os
import googleapiclient.discovery

myUserID = os.getenv("myUserID")
myToken = os.getenv("myToken")
spotifyPlaylist = os.getenv("spotifyPlaylist")
youtubePlaylist = os.getenv("youtubePlaylist")
youtube_API_key = os.getenv("youtube_API_key")

class PlaylistConverter:
    def __init__(self):
        self.user_id = myUserID
        self.token = myToken
        self.youtube = self.getYoutubeClient()


    def getYoutubeClient(self):
        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = youtube_API_key)

        return youtube


    def getSongNames(self, playlist_ID, startFrom, songCount):
        request = self.youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId= playlist_ID
        )
        response = request.execute()

        nextPageToken = response.get('nextPageToken')

        while ("nextPageToken" in response):
            nextPage = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_ID,
            maxResults="50",
            pageToken=nextPageToken
            ).execute()
            response["items"] = response["items"] + nextPage["items"]

            if 'nextPageToken' not in nextPage:
                response.pop('nextPageToken', None)
            else:
                nextPageToken = nextPage['nextPageToken']

        songNames = []
        
        for num, item in enumerate(response["items"], start = 1):
            if num < startFrom:
                continue
            elif len(songNames) < songCount:
                title = item["snippet"]["title"]
                match = regex.findall(r"[\p{L}0-9 \";,&.'’+—–-]+ *[|—–-] *[\p{L}0-9 \";,&.'’—–-]+", title)
                if match:
                    if regex.search(r" feat| ft| FEAT | FT", match[0]):
                        songNames.append(regex.split(r" feat| ft| FEAT| FT", match[0])[0])
                        continue
                    songNames.append(match[0])
                else:
                    songNames.append(title)
            else:
                break

        return songNames


    def getSpotifyURI(self, songName):
        endpoint = "https://api.spotify.com/v1/search"

        request_body = {"q": songName, "type":"track", "limit":"1", "offset":"0"}

        response = requests.get(
            endpoint,
            params = request_body,
            headers = {
                "Accept": "application/json",
                "Content-Type":"application/json",
                "Authorization" : "Bearer {0}".format(self.token)
            })

        if not response.json()["tracks"]["items"]:
            return None

        else:
            return response.json()["tracks"]["items"][0]["uri"]


    def addSongsToSpotify(self, spotifyPlaylistID, youtubePlaylistID, startFrom, songCount, reversed = False):
        endpoint = "https://api.spotify.com/v1/playlists/{0}/tracks".format(spotifyPlaylistID)

        songNames = self.getSongNames(youtubePlaylistID, startFrom, songCount)
        URIs = []
        for song in songNames:
            URI = self.getSpotifyURI(song)
            if URI == None:
                print("\"{0}\" was not added".format(song))
                continue
            else:
                URIs.append(URI)

        if reversed:
            URIs.reverse()

        request_body = json.dumps(URIs)

        response = requests.post(
            endpoint,
            data = request_body,
            headers = {"Content-Type":"application/json",
            "Authorization" : "Bearer {0}".format(self.token)
            })


script = PlaylistConverter()
script.addSongsToSpotify(spotifyPlaylist ,youtubePlaylist, 1, 10, True)