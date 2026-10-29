import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="ChemPH | Calculadora de pH", page_icon="🧪", layout="wide")

st.title("🧪 ChemPH")
st.subheader("Calculadora de pH para Ingeniería Química")
st.write("Herramienta educativa para estimar el pH de disoluciones acuosas y explorar su relación con procesos químicos.")

with st.sidebar:
    st.header("Menú")
    seccion = st.radio("Selecciona una sección:", [
        "Calculadora", "Comparar concentraciones", "Caso industrial", "Marco teórico"
    ])
    st.caption("Modelo educativo: soluciones acuosas diluidas a 25 °C, salvo que se indique otra cosa.")

def clasificar(ph):
    if ph < 7 - 1e-7:
        return "Ácida"
    if ph > 7 + 1e-7:
        return "Básica"
    return "Neutra (aprox.)"

def pH_de_H(h):
    if h <= 0:
        raise ValueError("La concentración debe ser mayor que cero.")
    return -math.log10(h)

def pH_de_OH(oh):
    if oh <= 0:
        raise ValueError("La concentración debe ser mayor que cero.")
    poh = -math.log10(oh)
    return 14.0 - poh

def ph_acido_debil(c, ka):
    # HA <-> H+ + A-; x^2/(C-x)=Ka. Raíz positiva de la ecuación cuadrática.
    if c <= 0 or ka <= 0:
        raise ValueError("La concentración y Ka deben ser mayores que cero.")
    x = (-ka + math.sqrt(ka**2 + 4*ka*c)) / 2
    return -math.log10(x), x

if seccion == "Calculadora":
    st.markdown("### Calcula una disolución")
    modo = st.selectbox("¿Qué dato conoces?", [
        "Concentración de H⁺", "Concentración de OH⁻",
        "Ácido fuerte (modelo ideal)", "Base fuerte (modelo ideal)",
        "Ácido acético (ácido débil)"
    ])
    col1, col2 = st.columns(2)
    with col1:
        if modo in ["Concentración de H⁺", "Concentración de OH⁻"]:
            etiqueta = "[H⁺] (mol/L)" if modo == "Concentración de H⁺" else "[OH⁻] (mol/L)"
            concentracion = st.number_input(etiqueta, min_value=1e-14, max_value=10.0,
                                            value=1e-3, format="%.6g")
        elif modo in ["Ácido fuerte (modelo ideal)", "Base fuerte (modelo ideal)"]:
            sustancia = "HCl" if modo.startswith("Ácido") else "NaOH"
            concentracion = st.number_input(f"Concentración formal de {sustancia} (mol/L)",
                                            min_value=1e-14, max_value=10.0,
                                            value=1e-3, format="%.6g")
        else:
            concentracion = st.number_input("Concentración inicial de CH₃COOH (mol/L)",
                                            min_value=1e-10, max_value=10.0,
                                            value=0.1, format="%.6g")
            ka = st.number_input("Ka del ácido acético", min_value=1e-12,
                                 max_value=1e-2, value=1.8e-5, format="%.2e")
    with col2:
        st.info("Los resultados son estimaciones. La actividad iónica, la temperatura y la composición real pueden modificar el pH medido.")
        st.write("**Condiciones del modelo:**")
        st.write("- Disolución acuosa diluida")
        st.write("- Temperatura de referencia: 25 °C")
        st.write("- Se omiten efectos de actividad, salvo en mediciones reales")

    if st.button("Calcular pH", type="primary"):
        try:
            if modo == "Concentración de H⁺":
                ph = pH_de_H(concentracion)
                detalle = f"pH = −log₁₀({concentracion:g})"
            elif modo == "Concentración de OH⁻":
                ph = pH_de_OH(concentracion)
                detalle = f"pOH = −log₁₀({concentracion:g}); pH ≈ 14 − pOH"
            elif modo == "Ácido fuerte (modelo ideal)":
                ph = pH_de_H(concentracion)
                detalle = "Se supone disociación completa: [H⁺] ≈ concentración formal."
            elif modo == "Base fuerte (modelo ideal)":
                ph = pH_de_OH(concentracion)
                detalle = "Se supone disociación completa: [OH⁻] ≈ concentración formal."
            else:
                ph, h_eq = ph_acido_debil(concentracion, ka)
                detalle = f"Equilibrio de ácido débil: [H⁺]eq ≈ {h_eq:.4g} mol/L; Ka = {ka:.2e}."
            st.divider()
            a, b, c = st.columns(3)
            a.metric("pH estimado", f"{ph:.3f}")
            b.metric("pOH estimado", f"{14-ph:.3f}")
            b_class = clasificar(ph)
            c.metric("Clasificación", b_class)
            st.caption(detalle)
            if ph < 7:
                st.warning("La disolución se clasifica como ácida en el modelo a 25 °C.")
            elif ph > 7:
                st.info("La disolución se clasifica como básica en el modelo a 25 °C.")
            else:
                st.success("La disolución se clasifica como aproximadamente neutra.")
            fig, ax = plt.subplots(figsize=(8, 1.5))
            ax.imshow(np.arange(0, 14.01, 0.1).reshape(1, -1), aspect="auto",
                      extent=[0, 14, 0, 1], cmap="RdYlGn_r")
            ax.axvline(ph, color="black", linewidth=2)
            ax.set_xlim(0, 14)
            ax.set_yticks([])
            ax.set_xticks(range(0, 15, 2))
            ax.set_xlabel("Escala de pH")
            st.pyplot(fig)
            plt.close(fig)
        except (ValueError, OverflowError) as e:
            st.error(str(e))

elif seccion == "Comparar concentraciones":
    st.markdown("### ¿Cómo cambia el pH al cambiar la concentración?")
    tipo = st.selectbox("Modelo de disolución", ["Ácido fuerte ideal (HCl)", "Base fuerte ideal (NaOH)"])
    minimo = st.number_input("Exponente mínimo de concentración (10^x mol/L)", min_value=-12, max_value=-1, value=-6)
    maximo = st.number_input("Exponente máximo de concentración (10^x mol/L)", min_value=-11, max_value=0, value=-2)
    if minimo >= maximo:
        st.error("El exponente mínimo debe ser menor que el máximo.")
    else:
        exponentes = np.linspace(minimo, maximo, 60)
        concentraciones = 10.0 ** exponentes
        phs = -np.log10(concentraciones) if tipo.startswith("Ácido") else 14 + np.log10(concentraciones)
        tabla = pd.DataFrame({"Concentración (mol/L)": concentraciones, "pH estimado": phs})
        st.line_chart(tabla, x="Concentración (mol/L)", y="pH estimado")
        st.dataframe(tabla.iloc[::5].round(6), use_container_width=True)
        st.download_button("Descargar datos CSV", tabla.to_csv(index=False).encode("utf-8"),
                           file_name="comparacion_pH.csv", mime="text/csv")
        st.caption("Modelo ideal de ácido/base fuerte; no representa todas las soluciones concentradas ni los efectos de actividad.")

elif seccion == "Caso industrial":
    st.markdown("### Caso de estudio: seguimiento del pH en tratamiento de agua")
    st.write("En el tratamiento de agua, el pH es una variable de control importante porque afecta procesos químicos y biológicos. En una planta real se mide con un instrumento calibrado y se interpreta junto con otros parámetros.")
    ph_medido = st.slider("Introduce un pH hipotético de una muestra", min_value=0.0, max_value=14.0, value=6.2, step=0.1)
    objetivo = st.slider("Valor objetivo ilustrativo", min_value=4.0, max_value=10.0, value=7.0, step=0.1)
    diferencia = ph_medido - objetivo
    c1, c2, c3 = st.columns(3)
    c1.metric("pH de muestra", f"{ph_medido:.1f}")
    c2.metric("Objetivo elegido", f"{objetivo:.1f}")
    c3.metric("Diferencia", f"{diferencia:+.1f}")
    if abs(diferencia) < 0.05:
        st.success("La muestra coincide aproximadamente con el objetivo ilustrativo.")
    elif diferencia < 0:
        st.warning("La muestra está por debajo del objetivo ilustrativo. En un proceso real se requiere evaluación técnica antes de ajustar.")
    else:
        st.warning("La muestra está por encima del objetivo ilustrativo. En un proceso real se requiere evaluación técnica antes de ajustar.")
    st.info("Este módulo es una simulación educativa: no calcula dosis de reactivos ni sustituye procedimientos, mediciones, normas o supervisión profesional.")

else:
    st.markdown("### Marco teórico")
    st.write("El pH expresa la acidez de una disolución. En el modelo introductorio para disoluciones acuosas diluidas se usa pH ≈ −log₁₀[H⁺]. La definición rigurosa se basa en la actividad del ion hidrógeno.")
    st.latex(r"\mathrm{pH}=-\log_{10}[H^+]")
    st.latex(r"\mathrm{pOH}=-\log_{10}[OH^-]")
    st.latex(r"\mathrm{pH}+\mathrm{pOH}\approx 14\quad (25\ ^\circ\mathrm{C})")
    st.write("En este proyecto, los cálculos para HCl y NaOH suponen disociación completa; para el ácido acético se emplea un modelo de equilibrio con Ka.")
    st.markdown("**Limitaciones:** no se corrigen coeficientes de actividad, no se modelan mezclas ni sistemas polipróticos y la relación pH + pOH = 14 corresponde aproximadamente a 25 °C.")
    st.markdown("**Fuentes:** IUPAC Gold Book (definición de pH); OpenStax, *Chemistry 2e* (equilibrio ácido-base); documentación oficial de Streamlit (despliegue).")

st.divider()
st.caption("ChemPH | Proyecto académico de programación e Ingeniería Química. Verifica siempre los resultados con fuentes académicas y mediciones adecuadas.")
