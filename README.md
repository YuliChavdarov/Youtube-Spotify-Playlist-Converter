# How to use

0. Download the source files or clone this repository.
1. Download and install [Python](https://www.python.org/downloads/).
2. Open a terminal in the folder that contains script.py.
3. Create a virtual environment for the project:

```bash
virtualenv playlist_converter
```

4. Activate the virtual environment:

Windows:

```bash
source playlist_converter/Scripts/activate
```
Linux, Mac:

```bash
source playlist_converter/bin/activate
```

5. Install the requirements.

```bash
pip install -r requirements.txt
```

6. Rename .env_sample to .env.
7. Log into your Spotify account and go to Profile -> Account. Copy your Username and paste it into .env (spotifyUserId).
8. Copy the URL of the playlist in which you want the songs to be added and paste it into .env (spotifyPlaylist).
9. Visit https://developer.spotify.com/console/put-playlist-tracks/, click Get Token, select playlist-modify-public and playlist-modify-private, and click Request Token.
10. Copy the generated token into .env (spotifyAuthToken).
11. Go to Youtube, copy the URL of the source playlist and paste it into .env (youtubePlaylist).
12. Go to https://console.developers.google.com/ and create a project.
13. Go to Library and enable YouTube Data API v3.
14. Select Create Credentials, select Youtube Data API v3, Public Data.
15. Copy the generated API key into .env (youtube_API_key).
16. Run the script.

```bash
python ./script.py
```

That's it! You should see how many songs have been added, as well as the count and names of the songs that have not been found.


## Note
If you would like to contribute to the project by adding a GUI, improving the regular expression for song name extraction, or any other way, feel free to submit a pull request.
