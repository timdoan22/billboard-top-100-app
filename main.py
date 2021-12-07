from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

URL = "https://www.billboard.com/charts/hot-100"

user_date = input("Which year do you want to travel to? Enter the date (YYYY-MM-DD): ")
year_entered = user_date.split("-")[0]

response = requests.get(f"{URL}/{user_date}")
billboard_100_page = response.text

soup = BeautifulSoup(billboard_100_page, "html.parser")

top_songs = soup.find_all(name="h3", id="title-of-a-story")
top_songs = [song.getText().strip("\n") for song in top_songs[3:103]]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        show_dialog=True,
        cache_path="token.txt"
    )
)

current_user = sp.current_user()["id"]
songs_uri = []

for song in top_songs:
    search_song = sp.search(q=f"track:{song} year:{year_entered}", limit=1, type="track", market="US")
    try:
        song_uri = search_song["tracks"]["items"][0]["uri"]
    except IndexError:
        pass
    else:
        songs_uri.append(song_uri)

new_playlist = sp.user_playlist_create(user=current_user, name=f"{user_date} Billboard 100", public=False)
sp.user_playlist_add_tracks(user=current_user, playlist_id=new_playlist["id"], tracks=songs_uri)
