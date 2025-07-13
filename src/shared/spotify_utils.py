import requests
import random
import base64
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET")
PODCASTS = [
    "L'After Foot",
    "These Football Times",
    "Xadrez Verbal",
    "Tifo Football Podcast",
    "First Take",
    "TED Talks Daily",
    "Freakonomics Radio",
    "The Joe Rogan Experience",
    "How I Built This",
    "Café da Manhã",
    "O Assunto"
]

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


def get_latest_episode_for_podcast(token: str, podcast_name: str):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "q": podcast_name,
        "type": "show",
        "limit": 1
    }
    resp = requests.get(search_url, headers=headers, params=params)
    resp.raise_for_status()
    shows = resp.json().get("shows", {}).get("items", [])

    if not shows:
        return {"podcast": podcast_name, "error": "Podcast not found"}

    show = shows[0]
    show_id = show["id"]

    episodes_url = f"https://api.spotify.com/v1/shows/{show_id}/episodes"
    params = {
        "limit": 1,
        "market": "US"
    }
    resp = requests.get(episodes_url, headers=headers, params=params)
    resp.raise_for_status()
    episodes = resp.json().get("items", [])

    if not episodes:
        return {"podcast": podcast_name, "error": "No episodes found"}

    latest = episodes[0]
    return {
        "podcast": podcast_name,
        "episode_name": latest["name"],
        "release_date": latest["release_date"],
        "episode_url": latest["external_urls"]["spotify"]
    }

def get_latest_episodes_for_all_podcasts(n=5):
    token = get_spotify_token()
    results = []
    for name in PODCASTS:
        try:
            ep = get_latest_episode_for_podcast(token, name)
            results.append(ep)
        except Exception as e:
            results.append({"podcast": name, "error": str(e)})
    filtered = [r for r in results if "error" not in r and "release_date" in r]    
    filtered.sort(key=lambda x: datetime.strptime(x["release_date"], "%Y-%m-%d"), reverse=True)
    top_n = filtered[:n]
    return top_n