import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Holiday Helper", page_icon="🏞️")

st.title("Holiday Helper 🏞️")
st.write("Seu assistente pessoal de férias na Suíça!")

st.markdown("---")

st.subheader("Escolha seu humor de hoje:")
mood = st.selectbox("Como você está se sentindo?", ["Relaxado", "Aventureiro", "Caseiro"])

st.success(f"Humor selecionado: **{mood}** 🎯")



# Garantir que a pasta 'data' existe
os.makedirs("data", exist_ok=True)

# Registrar o humor selecionado
log_path = "data/humor_log.csv"
log_entry = pd.DataFrame([{
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "humor": mood
}])
log_entry.to_csv(log_path, mode='a', header=not os.path.exists(log_path), index=False)