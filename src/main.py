import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from app.utils.db_utils import insert_mood, get_connection
from dotenv import load_dotenv
load_dotenv()


# rodar com .\.venv\Scripts\Activate e depois streamlit run src/main.py


# from dotenv import load_dotenv

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from shared.fetch_transport import get_transport_data, parse_transport_response

# load_dotenv()

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


origin = "Lausanne, Switzerland"
destination = "Lac Léman, Switzerland"

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
            if playlist["description"]:
                st.write(playlist["description"])
        else:
            st.info("Nenhuma playlist encontrada para esse humor.")
    except Exception as e:
        st.error(f"Erro ao buscar playlist no Spotify: {e}")


if st.button("Consultar transporte"):
    with st.spinner("Consultando tempo estimado..."):
        try:
            data = get_transport_data(origin, destination)
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

from shared.recommend_places import recommend_places

st.subheader("📍 Recomendações de lugares para visitar")

# Mock da condição do clima
weather_condition_mock = "clear"  # ou "rain", "clouds"

places = recommend_places(weather_condition_mock)

for place in places:
    st.markdown(f"**{place['name']}** - {place['category']}")
    st.markdown(f"[Ver rota no Google Maps]({place['route_url']})")
    st.write("---")

from shared.lake_utils import build_mock_transport_message

st.title("🏖️ Melhor lugar para nadar hoje")

if st.button("Ver recomendação de hoje"):
    msg = build_mock_transport_message()
    st.success(msg)


from shared.weather_utils import get_mock_weather

st.title("Holiday Helper - Clima")

weather = get_mock_weather()

st.write(f"Temperatura: {weather['temperature_celsius']}°C")
st.write(f"Condição: {weather['condition']}")
st.write(f"Última atualização: {weather['timestamp']}")


if st.button("Consultar transporte teste"):
    data = get_transport_data(origin, destination)
    st.json(data)


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


