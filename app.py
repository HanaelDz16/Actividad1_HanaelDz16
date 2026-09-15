import streamlit as st

st.title("Clasificador de temperatura")
temperatura = st.number_input(
  "Introduce la temperatura en "C:",
value=20
)
