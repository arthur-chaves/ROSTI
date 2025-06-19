import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def search_playlist_by_mood(token, mood):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": mood,
        "type": "playlist",
        "limit": 3
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    items = resp.json().get("playlists", {}).get("items", [])
    if items:
        playlist = items[0]
        return {
            "name": playlist["name"],
            "url": playlist["external_urls"]["spotify"],
            "image_url": playlist["images"][0]["url"] if playlist["images"] else None
        }
    return None
