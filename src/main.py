import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import json
from app.utils.db_utils import insert_mood, get_connection
from dotenv import load_dotenv
load_dotenv()

OUTPUT_PATH = "data/output"

def load_json(file_name):
    try:
        with open(os.path.join(OUTPUT_PATH, file_name), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar {file_name}: {e}")
        return None

st.set_page_config(page_title="Holiday Helper", page_icon="🏞️")

st.title("Holiday Helper 🏞️")
st.write("Seu assistente pessoal de férias na Suíça!")

st.markdown("---")


from shared.spotify_utils import get_spotify_token, get_spotify_genres, search_playlists_by_genres

token = get_spotify_token()
genres = get_spotify_genres()
playlists = search_playlists_by_genres(token, genres)


st.title("🎧 Sugestões musicais para hoje")

token = get_spotify_token()
genres = get_spotify_genres()
playlists = search_playlists_by_genres(token, genres)

for pl in playlists:
    st.markdown(f"**{pl['name']}**  \n[Gênero: {pl['genre']}]({pl['url']})")




from data.letterboxd_read import get_daily_recommendations, mark_as_watched, get_all_unwatched

st.title("🎬 Recomendações de Hoje")

recs = get_daily_recommendations()

if not recs:
    st.success("Você já assistiu todos os filmes da sua watchlist! 👏")
else:
    # Mostrar filmes
    for _, name, year, uri in recs:
        st.markdown(f"- **{name}** ({year}) – [🔗 Link]({uri})")

    # Dropdown
    options = ["Nenhum"] + get_all_unwatched()
    selected = st.selectbox("Você assistiu algum dos seus filmes ontem?", options)

    if selected != "Nenhum":
        if st.button("✅ Marcar como assistido"):
            mark_as_watched(selected)
            st.success(f"{selected} marcado como assistido!")
            st.experimental_rerun()


from shared.wired_today import random_wired_articles_today

st.title("📰 Notícias Wired de Hoje")

artigos = random_wired_articles_today()

if artigos:
    for artigo in artigos:
        st.markdown(f"### [{artigo['title']}]({artigo['link']})")
        st.caption(f"🕒 Publicado às {artigo['published']} UTC")
else:
    st.info("Nenhum artigo novo da Wired hoje.")

if "show_swim_info" not in st.session_state:
    st.session_state["show_swim_info"] = False

from shared.fetch_transport import parse_transport_response

weather = load_json("weather.json")
checklist = load_json("checklist.json")
lake_temps = load_json("lake_temperatures.json")
transport = load_json("transport.json")

if st.button("Vamos nadar aonde hoje?"):
    st.session_state["show_swim_info"] = True
    
if st.session_state["show_swim_info"]:

    if weather:
        st.subheader("🌤️ Clima do dia")

        st.write(f"**Data:** {weather.get('date', 'N/A')} ({weather.get('timezone', '')})")
        st.write(f"**Máxima:** {weather.get('max_temp', 'N/A')} °C")
        st.write(f"**Mínima:** {weather.get('min_temp', 'N/A')} °C")
        st.write(f"**Descrição do dia:** {weather.get('day_desc', 'N/A')}")
        # st.write(f"**Descrição da noite:** {weather.get('night_desc', 'N/A')}")
        


    if checklist:
        st.subheader("🎒 Checklist")
        st.info(checklist.get("mensagem", ""))
        for item in checklist.get("itens", []):
            st.write(f"• {item}")

    if lake_temps:
        st.subheader("🌡️ Temperatura dos lagos")
        for spot in lake_temps:
            name = spot.get("name", "Desconhecido")
            lake = spot.get("lake", "—")
            temp = spot.get("temp")
            status = spot.get("status", "Sem status")
            if temp is not None:
                st.success(f"{name} ({lake}): {temp}°C – {status}")
            else:
                st.error(f"{name} ({lake}): Erro – {status}")

    if transport:
        st.subheader("🚍 Transporte até pontos de natação")

        # Lista de destinos para o selectbox
        destinos = [t.get("destination", "Destino desconhecido") for t in transport]

        praia_escolhida = st.selectbox("Selecione a praia para ver o trajeto detalhado:", destinos, key="praia_escolhida")

        # Busca os dados do destino escolhido
        dados_praia = next((t for t in transport if t.get("destination") == praia_escolhida), None)

        if dados_praia:
            if "error" in dados_praia:
                st.error(f"{praia_escolhida}: {dados_praia['error']}")
            else:
                dur = dados_praia.get("duration_minutes", "?")
                st.write(f"Tempo estimado até {praia_escolhida}: {dur} minutos")

                # Chama a função que você já tem para parsear os detalhes do trajeto
                mensagem_trajeto = dados_praia.get("route_data", "Não foi possível carregar os detalhes.")
                st.text_area("Detalhes do trajeto", mensagem_trajeto, height=150)

