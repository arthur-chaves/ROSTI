import requests
import random
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


def get_spotify_genres():
    raw = os.getenv("SPOTIFY_GENRES", "")
    return [g.strip() for g in raw.split(",") if g.strip()]

def search_playlists_by_genres(token: str, genres: list[str], limit_per_genre: int = 2):
    import random
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    results = []

    for genre in genres:
        params = {
            "q": f"{genre} vacation OR {genre} férias playlist",
            "type": "playlist",
            "limit": limit_per_genre
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            playlists = resp.json().get("playlists", {}).get("items", [])
            for playlist in playlists:
                if not playlist or "name" not in playlist or "external_urls" not in playlist:
                    continue
                results.append({
                    "name": playlist["name"],
                    "url": playlist["external_urls"].get("spotify", "#"),
                    "image_url": playlist.get("images", [{}])[0].get("url"),
                    "genre": genre
                })

    return random.sample(results, min(4, len(results)))
