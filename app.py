import streamlit as st

st.title("Clasificador de temperatura")
temperatura = st.number_input(
  "Introduce la temperatura en C:",
value=20
)

 if temperatura < 15:
 st.info    ("El clima esta frio")
 elif 15 <= temperatura <= 25:
 st.success    ("El clima esta templado")
 else:
 st.warning     ("El clima esta caluroso")
