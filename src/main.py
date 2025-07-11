import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import json
from app.utils.db_utils import insert_mood, get_connection
from dotenv import load_dotenv
load_dotenv()

# ==== Config ====
OUTPUT_PATH = "data/output"


def load_json(file_name):
    try:
        with open(os.path.join(OUTPUT_PATH, file_name), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return None

st.set_page_config(page_title="Holiday Helper", page_icon="🏞️")

st.markdown(
    """
    <div style='text-align: center'>
        <h1>Holiday Helper 🏞️</h1>
        <p style='font-size: 20px;'>Your personal vacation assistant in Switzerland!</p>
        <hr style='margin-top: 10px; margin-bottom: 20px;'/>
    </div>
    """,
    unsafe_allow_html=True
)


# ==== Load data ====
weather = load_json("weather.json")
checklist = load_json("checklist.json")
lake_temps = load_json("lake_temperatures.json")
transport = load_json("transport.json")

from shared.spotify_utils import get_spotify_token, get_spotify_genres, search_playlists_by_genres
from data.letterboxd_read import get_daily_recommendations, mark_as_watched, get_all_unwatched, get_letterboxd_user
from shared.wired_today import random_wired_articles_today
from shared.fetch_transport import parse_transport_response


if "playlists" not in st.session_state:
    token = get_spotify_token()
    genres = get_spotify_genres()
    st.session_state["playlists"] = search_playlists_by_genres(token, genres)

if "movie_recs" not in st.session_state:
    st.session_state["movie_recs"] = get_daily_recommendations()

if "wired_articles" not in st.session_state:
    st.session_state["wired_articles"] = random_wired_articles_today()

# ==== Section: Spotify, Movies, News ====
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎧 Music Suggestions")
    for pl in st.session_state["playlists"]:
        st.markdown(f"**{pl['name']}**\n[Genre: {pl['genre']}]({pl['url']})")

with col2:
    st.subheader("🎬 Movie Picks")

    recs = get_daily_recommendations()
    if not recs:
        st.success("You've watched everything on your watchlist! 👏")
    else:
        for _, name, year, uri in recs:
            st.markdown(f"- **{name}** ({year}) – [🔗 Link]({uri})")
        options = ["None"] + get_all_unwatched()
        selected = st.selectbox("Did you watch any of these yesterday?", options)
        if selected != "None":
            if st.button("✅ Mark as watched"):
                mark_as_watched(selected)
                st.success(f"{selected} marked as watched!")
                st.experimental_rerun()
        
        letterboxd_user = get_letterboxd_user()
        if letterboxd_user:
            st.markdown(f"[📽️ See your full watchlist on Letterboxd](https://letterboxd.com/{letterboxd_user})")
        else:
            st.warning("Letterboxd user not configured.")
        


st.subheader("📰 Wired News")
articles = st.session_state["wired_articles"]
if articles:
    for article in articles:
        st.markdown(f"**[{article['title']}]({article['link']})**")
        st.caption(f"🕒 {article['published']} UTC")
else:
        st.info("No new Wired articles today.")

# ==== Divider ====
st.markdown("---")

# ==== Swim info section (always shown, no botão) ====

# Row 1: Weather | Checklist
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🌤️ Today's Weather")
    if weather:
        st.write(f"**Date:** {weather.get('date', 'N/A')} ({weather.get('timezone', '')})")
        st.write(f"**Max temp:** {weather.get('max_temp', 'N/A')} °C")
        st.write(f"**Min temp:** {weather.get('min_temp', 'N/A')} °C")
        st.write(f"**Day description:** {weather.get('day_desc', 'N/A')}")

with col_b:
    st.subheader("🎒 Packing Checklist")
    if checklist:
        for item in checklist.get("itens", []):
            st.write(f"• {item}")

# Row 2: Lake temps | Transport
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("🌡️ Lake Temperatures")

    if lake_temps:
        sorted_lakes = sorted(
            [lt for lt in lake_temps if lt.get("temp") is not None],
            key=lambda x: x.get("temp", -999),
            reverse=True
        )

        options = [3, 5, 10, len(sorted_lakes)]  # opções de quantos mostrar
        options = sorted(list(set(options)))  # garantir ordem e sem repetição

        default = 3
        count = st.selectbox("Show how many lakes?", options, index=options.index(default))

        lakes_to_show = sorted_lakes[:count]

        for spot in lakes_to_show:
            name = spot.get("name", "Unknown")
            lake = spot.get("lake", "—")
            temp = spot.get("temp")
            status = spot.get("status", "No status")
            st.success(f"{name} ({lake}): {temp}°C – {status}")




with col_d:
    st.subheader("🚍 Transport to Swimming Spot")
    if transport:
        destinations = [t.get("destination", "Unknown destination") for t in transport]
        selected_beach = st.selectbox("Select a location to view route details:", destinations, key="selected_beach")

        beach_data = next((t for t in transport if t.get("destination") == selected_beach), None)

        if beach_data:
            if "error" in beach_data:
                st.error(f"{selected_beach}: {beach_data['error']}")
            else:
                duration = beach_data.get("duration_minutes", "?")
                st.write(f"Estimated travel time to {selected_beach}: {duration} minutes")
                route_message = beach_data.get("route_data", "Unable to load route details.")
                st.text_area("Route details", route_message, height=150)

