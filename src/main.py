import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from app.utils.db_utils import insert_mood, get_connection
from dotenv import load_dotenv
load_dotenv()



from shared.fetch_transport import get_transport_data, parse_transport_response, simplify_directions_response, generate_transport_summary

st.set_page_config(page_title="Holiday Helper", page_icon="🏞️")

st.title("Holiday Helper 🏞️")
st.write("Seu assistente pessoal de férias na Suíça!")

st.markdown("---")


if st.checkbox("Ver histórico de humor"):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT * FROM mood_log ORDER BY timestamp DESC")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    
    df = pd.DataFrame(rows, columns=columns)

    cur.close()
    con.close()
    
    st.dataframe(df)





# Garantir que a pasta 'data' existe
os.makedirs("data", exist_ok=True)


from app.utils.recommendation import get_media_by_mood
# Exemplo de escolha de humor (pode ser entrada do usuário)
mood = st.selectbox("Como você está se sentindo?", ["feliz", "triste", "cansado", "animado"])

st.success(f"Humor selecionado: **{mood}** 🎯")

if st.button("Salvar humor"):
    insert_mood(mood)
    st.success(f"Humor '{mood}' salvo com sucesso!")

media = get_media_by_mood(mood)
st.write(f"Sugestão para você: **{media['title']}** ({media['type']})")

if media["type"].lower() == "filme":
    st.info(f"🎬 Filme: {media['title']}")
elif media["type"].lower() == "passeio":
    st.info(f"🌄 Passeio: {media['title']}")
else:
    st.info(f"🎲 Sugestão: {media['title']}")

from shared.spotify_utils import get_spotify_token, search_playlist_by_mood

# Depois que usuário escolhe o humor:
if mood:
    try:
        token = get_spotify_token()
        playlist = search_playlist_by_mood(token, mood)
        if playlist:
            st.markdown(f"### Playlist para o humor **{mood}**")
            if playlist["image_url"]:
                st.image(playlist["image_url"], width=300)
            st.markdown(f"[Ouça no Spotify]({playlist['url']})")
        else:
            st.info("Nenhuma playlist encontrada para esse humor.")
    except Exception as e:
        st.error(f"Erro ao buscar playlist no Spotify: {e}")

origin = os.getenv("USER_CITY")
from shared.lake_utils import get_all_spots

spots = get_all_spots()
spot_names = [spot[0] for spot in spots]
selected_spot_name = st.selectbox("Escolha o ponto de natação:", spot_names)

selected_spot = next(spot for spot in spots if spot[0] == selected_spot_name)
_, selected_lake, lat, lng = selected_spot
destination_coords = f"{lat},{lng}"

st.write(f"🧭 Destino selecionado: {selected_spot_name} ({selected_lake})")

if st.button("Consultar transporte"):
    with st.spinner("Consultando tempo estimado..."):
        try:
            data = get_transport_data(origin, destination_coords)
            message = parse_transport_response(data)
            st.success(message)
        except Exception as e:
            st.error(f"Erro: {e}")


from shared.checklist import generate_checklist
st.subheader("🎒 Checklist sugerido para hoje")

# 🔁 Simulando dados até a integração real com API
weather_data_mock = {
    "temp": 26,
    "weather": "Clear"
}

mensagem, itens = generate_checklist(weather_data_mock)

st.info(mensagem)
st.markdown("**Itens recomendados:**")
for item in itens:
    st.write(f"• {item}")



from shared.lake_utils import build_mock_transport_message

from shared.weather_utils import get_mock_weather

st.title("Holiday Helper - Clima")

weather = get_mock_weather()

st.write(f"Temperatura: {weather['temperature_celsius']}°C")
st.write(f"Condição: {weather['condition']}")
st.write(f"Última atualização: {weather['timestamp']}")


if st.button("Executar DAGs e mostrar resumo do transporte"):
    try:
        data = get_transport_data(origin, destination)
        summary = generate_transport_summary(data)
        st.success(summary)
    except Exception as e:
        st.error(f"Erro ao buscar dados da API: {e}")


import streamlit as st
from shared.airflow_api import get_jwt_token, trigger_dag

DAG_IDS = ["holiday_helper_dag", "mood_etl_dag_test"]

st.subheader("🚀 Executar DAGs do Airflow")

token = None
try:
    token = get_jwt_token()
except Exception as e:
    st.error(f"Erro ao obter token: {e}")

if token:
    for dag_id in DAG_IDS:
        if st.button(f"Executar DAG: {dag_id}", key=f"run_{dag_id}"):
            try:
                status_code, text = trigger_dag(dag_id, token)
                st.success(f"DAG '{dag_id}' executada com sucesso! ({status_code})")
            except Exception as e:
                st.error(f"Erro ao executar DAG '{dag_id}': {e}")


import streamlit as st
from shared.lake_utils import get_all_spots, get_lake_temperature_today

st.title("🌊 Verificador de Temperatura dos Lagos")

spots = get_all_spots()

for name, lake, lat, lng in spots:
    with st.spinner(f"🔍 Verificando {name}..."):
        temp, status = get_lake_temperature_today(lake, lat, lng)
        if temp:
            st.success(f"🏖️ {name} ({lake}) → {temp}°C ({status})")
        else:
            st.error(f"⚠️ {name} ({lake}) → Erro: {status}")
    


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
