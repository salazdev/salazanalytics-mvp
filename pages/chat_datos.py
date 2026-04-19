import streamlit as st
import pandas as pd
import plotly.express as px
import anthropic, json

PALETTE = ["#00C2FF","#7B2FBE","#00FFB3","#FF6B6B","#FFD93D"]

def call_claude(messages: list, system: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system,
        messages=messages,
    )
    return msg.content[0].text

def show():
    st.markdown("## 💬 Chat con tus datos")
    st.markdown("<p style='color:#7B9BB5'>Pregunta en lenguaje natural y obtén respuestas con gráficas automáticas.</p>", unsafe_allow_html=True)

    if not st.session_state.get("api_key"):
        st.warning("⚠️ Configura tu API Key en el módulo de Excel primero.")
        return

    df = st.session_state.get("df")

    if df is None:
        uploaded = st.file_uploader("Sube un Excel para chatear con él", type=["xlsx", "xls"])
        if uploaded:
            df = pd.read_excel(uploaded)
            st.session_state["df"] = df
        else:
            st.info("👆 Primero analiza un Excel en el módulo correspondiente, o sube uno aquí.")
            return

    cols_num = df.select_dtypes("number").columns.tolist()
    cols_cat = df.select_dtypes("object").columns.tolist()
    sample_csv = df.head(30).to_csv(index=False)

    system_prompt = f"""Eres un analista de datos experto que ayuda a interpretar datos de empresas colombianas.
El usuario ha cargado un dataset con {len(df)} filas y {len(df.columns)} columnas.
Columnas numéricas: {cols_num}
Columnas categóricas: {cols_cat}

Muestra de datos (CSV):
{sample_csv}

Cuando el usuario pregunte algo que requiera una gráfica, responde con un JSON en este formato exacto (sin markdown, solo el JSON puro):
{{"tipo_grafica": "barras|linea|pastel|histograma|dispersión", "x": "columna_x", "y": "columna_y", "titulo": "Título", "texto": "Explicación del gráfico"}}

Si la pregunta no requiere gráfica, responde con texto normal en español, claro y profesional.
"""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        role_class = "chat-user" if msg["role"] == "user" else "chat-ai"
        ic
