import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from app.utils.db_utils import insert_mood, get_connection


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



