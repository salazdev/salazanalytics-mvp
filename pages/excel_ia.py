import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, anthropic

PALETTE = ["#00C2FF", "#7B2FBE", "#00FFB3", "#FF6B6B", "#FFD93D", "#4ECDC4"]

def call_claude(prompt: str, system: str = "") -> str:
    client = anthropic.Anthropic(api_key=st.session_state.get("api_key", ""))
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system or "Eres un analista de datos experto. Responde en español de forma concisa y profesional.",
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

def show():
    st.markdown("## 📗 Análisis de Excel con IA")

    with st.expander("🔑 Configurar API Key de Anthropic", expanded=not st.session_state.get("api_key")):
        key = st.text_input("API Key", type="password", value=st.session_state.get("api_key", ""))
        if st.button("Guardar"):
            st.session_state["api_key"] = key
            st.success("API Key guardada")

    f = st.session_state.get("uploaded_file") if st.session_state.get("file_ext") == "xlsx" else None
    uploaded = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx", "xls"])
    if uploaded:
        f = uploaded
        st.session_state["uploaded_file"] = uploaded
        st.session_state["file_ext"] = "xlsx"

    if not f:
        st.info("👆 Sube un archivo Excel para comenzar el análisis.")
        return

    try:
        all_sheets = pd.read_excel(f, sheet_name=None)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return

    sheet_name = st.selectbox("Selecciona la hoja", list(all_sheets.keys()))
    df = all_sheets[sheet_name]
    st.session_state["df"] = df

    st.markdown(f"**{len(df)} filas · {len(df.columns)} columnas**")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Vista previa", "📊 Gráficas", "🤖 Análisis IA", "📐 Estadísticas"])

    with tab1:
        st.dataframe(df.head(100), use_container_width=True, height=350)
        cols_num = df.select_dtypes("number").columns.tolist()
        if cols_num:
            c1, c2, c3, c4 = st.columns(4)
            for col, label, val in [
                (c1, "Filas",     len(df)),
