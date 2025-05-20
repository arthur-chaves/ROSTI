import streamlit as st

st.set_page_config(page_title="Holiday Helper", page_icon="🏞️")

st.title("Holiday Helper 🏞️")
st.write("Seu assistente pessoal de férias na Suíça!")

st.markdown("---")

st.subheader("Escolha seu humor de hoje:")
mood = st.selectbox("Como você está se sentindo?", ["Relaxado", "Aventureiro", "Caseiro"])

st.success(f"Humor selecionado: **{mood}** 🎯")
