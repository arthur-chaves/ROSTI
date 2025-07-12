import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import json
from dotenv import load_dotenv

from app.utils.db_utils import insert_mood, get_connection
from shared.spotify_utils import get_spotify_token, get_spotify_genres, search_playlists_by_genres
from data.letterboxd_read import get_daily_recommendations, mark_as_watched, get_all_unwatched, get_letterboxd_user
from shared.wired_today import random_wired_articles_today
from shared.fetch_transport import parse_transport_response

load_dotenv()

# === CONFIG ===
OUTPUT_PATH = "data/output"
st.set_page_config(page_title="Holiday Helper", page_icon="🏞️", layout="wide")

def load_json(file_name):
    try:
        with open(os.path.join(OUTPUT_PATH, file_name), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return None

# === HEADER ===
st.markdown(
    """
    <div style='text-align: center'>
        <h2 style='margin-bottom: 0;'>Holiday Helper 🏞️</h2>
        <p style='font-size: 16px; margin-top: 0;'>Your personal vacation assistant in Switzerland!</p>
        <hr style='margin-top: 5px; margin-bottom: 15px;'/>
    </div>
    """,
    unsafe_allow_html=True
)

# === Load Data ===
weather = load_json("weather.json")
checklist = load_json("checklist.json")
lake_temps = load_json("lake_temperatures.json")
transport = load_json("transport.json")

# === Session Cache ===
if "playlists" not in st.session_state:
    token = get_spotify_token()
    genres = get_spotify_genres()
    st.session_state["playlists"] = search_playlists_by_genres(token, genres)

if "movie_recommendations" not in st.session_state:
    st.session_state["movie_recommendations"] = get_daily_recommendations()

if "wired_articles" not in st.session_state:
    st.session_state["wired_articles"] = random_wired_articles_today()

# === ROW 1: Weather | Music | Movies | Lake Temps (tall) ===
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])

with col1:
    st.subheader("🌤️ Weather")
    if weather:
        date_str = weather.get('date')
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            dt = datetime.now()

        formatted_date = dt.strftime("Today is %d/%m/%Y, %A")
        st.markdown(f"**{formatted_date}**")

        tz_full = weather.get('timezone', '')
        tz_clean = ''
        if '/' in tz_full:
            tz_clean = tz_full.split('/')[-1].replace('_', ' ').title()
        else:
            tz_clean = tz_full.title()

        
        st.markdown(f"**Max:** {weather.get('max_temp', 'N/A')} °C")
        st.markdown(f"**Min:** {weather.get('min_temp', 'N/A')} °C")
        st.markdown(f"**Forecast:** {weather.get('day_desc', 'N/A')}")

with col2:
    st.subheader("🎧 Music")
    for pl in st.session_state["playlists"]:
        st.markdown(f"**{pl['name']}**\n[Genre: {pl['genre']}]({pl['url']})")

with col3:
    st.subheader("🎬 Movies")
    recs = st.session_state.movie_recommendations

    if not recs:
        st.success("All watched! 👏")
    else:
        for _, name, year, uri in recs:
            st.markdown(f"- **{name}** ({year}) – [🔗]({uri})")

        options = ["None"] + get_all_unwatched()
        if "selected_movie" not in st.session_state:
            st.session_state.selected_movie = "None"

        selected = st.selectbox(
            "Did you watch one of these yesterday?",
            options,
            index=options.index(st.session_state.selected_movie),
            key="selected_movie"
        )

        if selected != "None":
            if st.button("✅ Mark watched"):
                mark_as_watched(selected)
                st.success(f"{selected} marked!")
                st.session_state.selected_movie = "None"
                del st.session_state.movie_recommendations
                st.experimental_rerun()

        user = get_letterboxd_user()
        if user:
            st.markdown(f"[🎞️ Full list](https://letterboxd.com/{user})")

# Usar container para lake temps ocupar 2 linhas na coluna 4
with col4:
    st.subheader("🌡️ Lake Water Temperatures")
    if lake_temps:
        sorted_lakes = sorted(
            [lt for lt in lake_temps if lt.get("temp") is not None],
            key=lambda x: x.get("temp", -999),
            reverse=True
        )
        for spot in sorted_lakes:
            name = spot.get("name", "Unknown")
            lake = spot.get("lake", "—")
            temp = spot.get("temp")
            st.markdown(f"**{name} ({lake})**: {temp}°C")

# === ROW 2: Checklist | News | Transport | Lake Temps (continuação) ===
col5, col6, col7, col8 = st.columns([1, 1, 1, 1.2])

with col5:
    st.subheader("🎒 Checklist")
    if checklist:
        for item in checklist.get("itens", []):
            st.markdown(f"• {item}")

with col6:
    st.subheader("📰 Wired News")
    articles = st.session_state["wired_articles"]
    if articles:
        for article in articles:
            st.markdown(f"**[{article['title']}]({article['link']})**")
            st.caption(f"🕒 {article['published']} UTC")
    else:
        st.info("No Wired articles today.")

with col7:
    st.subheader("🚍 Transport")
    if transport:
        destinations = [t.get("destination", "Unknown") for t in transport]
        selected_beach = st.selectbox("Choose destination:", destinations, key="selected_beach")
        beach_data = next((t for t in transport if t.get("destination") == selected_beach), None)

        if beach_data:
            if "error" in beach_data:
                st.error(f"{selected_beach}: {beach_data['error']}")
            else:
                st.markdown(f"**Time:** {beach_data.get('duration_minutes', '?')} min")
                with st.expander("🗺️ Route"):
                    st.text(beach_data.get("route_data", "No details."))

# with col8:
#     # Preencher o container para a segunda linha da coluna 4 (lake temps)
#     st.subheader("🌡️ Lake Water Temperatures")
#     if lake_temps:
#         sorted_lakes = sorted(
#             [lt for lt in lake_temps if lt.get("temp") is not None],
#             key=lambda x: x.get("temp", -999),
#             reverse=True
#         )
#         for spot in sorted_lakes:
#             name = spot.get("name", "Unknown")
#             lake = spot.get("lake", "—")
#             temp = spot.get("temp")
#             st.markdown(f"**{name} ({lake})**: {temp}°C")
