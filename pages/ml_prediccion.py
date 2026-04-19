import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

PALETTE = ["#00C2FF","#7B2FBE","#00FFB3","#FF6B6B","#FFD93D","#4ECDC4"]

def load_data(f):
    try:
        sheets = pd.read_excel(f, sheet_name=None)
        return sheets
    except Exception as e:
        st.error(f"Error leyendo archivo: {e}")
        return None

def preparar_datos(df):
    df = df.copy()
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['dia_semana'] = df['Fecha'].dt.dayofweek
        df['mes'] = df['Fecha'].dt.month
        df['dia_mes'] = df['Fecha'].dt.day
        df['semana'] = df['Fecha'].dt.isocalendar().week.astype(int)
    if 'Hora de Cobro' in df.columns:
        df['hora'] = pd.to_datetime(df['Hora de Cobro'], format='%H:%M:%S', errors='coerce').dt.hour
    return df

def show():
    st.markdown("## 🤖 Análisis Predictivo con Machine Learning")
    st.markdown("<p style='color:#7B9BB5'>Anticipa resultados, detecta patrones ocultos y toma mejores decisiones con IA.</p>", unsafe_allow_html=True)

    f = st.session_state.get("uploaded_file") if st.session_state.get("file_ext") == "xlsx" else None
    uploaded = st.file_uploader("Sube tu archivo Excel con datos históricos", type=["xlsx","xls"])
    if uploaded:
        f = uploaded
        st.session_state["uploaded_file"] = uploaded
        st.session_state["file_ext"] = "xlsx"

    if not f:
        st.info("👆 Sube un archivo Excel con datos históricos para activar el motor de predicción.")
        _mostrar_capacidades()
        return

    sheets = load_data(f)
    if not sheets:
        return

    sheet_name = st.selectbox("Selecciona la hoja de datos", list(sheets.keys()))
    df_raw = sheets[sheet_name]
    st.success(f"✅ **{len(df_raw):,} registros** cargados · {len(df_raw.columns)} columnas")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Diagnóstico",
        "📈 Predicción de Ventas",
        "👥 Segmentación",
        "🏆 Ranking Productos",
        "⚠️ Alertas Inteligentes",
    ])

    w
