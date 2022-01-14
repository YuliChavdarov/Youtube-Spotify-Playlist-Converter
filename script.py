import requests
import json
import regex
from dotenv import load_dotenv
load_dotenv()

import os
import googleapiclient.discovery

spotifyUserId = os.getenv("spotifyUserId")
spotifyAuthToken = os.getenv("spotifyAuthToken")
spotifyPlaylistID = os.getenv("spotifyPlaylist").split("/").pop()
youtubePlaylist = os.getenv("youtubePlaylist").split("list=").pop()
youtube_API_key = os.getenv("youtube_API_key")

api_service_name = "youtube"
api_version = "v3"

class PlaylistConverter:

    def getSongNames(self, playlist_ID, startIndex, endIndex):
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = youtube_API_key)

        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist_ID
        )

        try:
            response = request.execute()
        except:
            print("An error occured. The Youtube API key might be invalid or inactive.")
            return []


        nextPageToken = response.get('nextPageToken')

        items = response["items"]

        while (nextPageToken and len(items) < endIndex):
            currentPage = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_ID,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()
            items += currentPage["items"]
            
            nextPageToken = currentPage.get('nextPageToken')

        songNames = []

        for num, item in enumerate(items, start = 1):
            if num < startIndex:
                continue
            elif len(songNames) <= endIndex - startIndex:
                title = item["snippet"]["title"]
                match = regex.findall(r"[\p{L}0-9 \";,&.'’+—–-]+ *[|—–-] *[\p{L}0-9 \";,&.'’—–-]+", title)
                if match:
                    if regex.search(r" feat| ft| FEAT | FT", match[0]):
                        beforeFeat = regex.split(r" feat| ft| FEAT| FT", match[0])[0]
                        songNames.append(regex.sub(r" [x&—–-] ", " ", beforeFeat))
                        continue
                    songNames.append(regex.sub(r" [x&—–-] ", " ", match[0]))
                else:
                    songNames.append(regex.sub(r" [x&—–-] ", " ", title))
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
                "Authorization" : "Bearer {0}".format(spotifyAuthToken)
            })

        if not response.ok or not response.json()["tracks"]["items"]:
            return None

        else:
            return response.json()["tracks"]["items"][0]["uri"]


    def addSongsToSpotifyPlaylist(self, spotifyPlaylistID, youtubePlaylistID, startIndex, endIndex, reversed = False):
        endpoint = "https://api.spotify.com/v1/playlists/{0}/tracks".format(spotifyPlaylistID)

        songNames = self.getSongNames(youtubePlaylistID, startIndex, endIndex)
        URIs = []

        songsAdded = len(songNames)

        for song in songNames:
            URI = self.getSpotifyURI(song)
            if URI == None:
                print("\"{0}\" was not added".format(song))
                songsAdded -= 1
                continue
            else:
                URIs.append(URI)

        if reversed:
            URIs.reverse()

        response = requests.post(
            endpoint,
            data = json.dumps(URIs),
            headers = {
                "Content-Type":"application/json",
                "Authorization" : "Bearer {0}".format(spotifyAuthToken)
            })

        if response.ok:
            print("Done! {0} songs added.".format(songsAdded))
            print("{0} songs not added. They are either not on Spotify, or you have to add them manually.".format(len(songNames) - songsAdded))

        elif response.status_code == 401:
            print("An error occured. The Spotify token might be invalid or expired.")


script = PlaylistConverter()
script.addSongsToSpotifyPlaylist(spotifyPlaylistID, youtubePlaylist, 1, 10, True)