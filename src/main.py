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

# st.subheader("Escolha seu humor de hoje:")
# mood = st.selectbox("Como você está se sentindo?", ["Relaxado", "Aventureiro", "Caseiro"])


# st.success(f"Humor selecionado: **{mood}** 🎯")





if st.checkbox("Ver histórico de humor"):
    con = get_connection()

    df = con.execute("SELECT * FROM mood_log ORDER BY timestamp DESC").fetchdf()
    con.close()
    st.dataframe(df)


origin = "Lausanne, Switzerland"
destination = "Lac Léman, Switzerland"

# Garantir que a pasta 'data' existe
os.makedirs("data", exist_ok=True)

# Registrar o humor selecionado
# log_path = "data/humor_log.csv"
# log_entry = pd.DataFrame([{
#     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     "humor": mood
# }])
# log_entry.to_csv(log_path, mode='a', header=not os.path.exists(log_path), index=False)

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from app.utils.recommendation import get_recommendations_by_mood

# st.markdown("---")
# st.subheader("Sugestões para o seu dia:")

# sugestoes = get_recommendations_by_mood(mood)

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




