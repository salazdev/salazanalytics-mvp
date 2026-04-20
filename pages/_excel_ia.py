import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, anthropic

PALETTE = ["#00C2FF", "#7B2FBE", "#00FFB3", "#FF6B6B", "#FFD93D", "#4ECDC4"]

def call_claude(prompt, system=""):
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
            c1.metric("Filas", len(df))
            c2.metric("Columnas", len(df.columns))
            c3.metric("Nulos", int(df.isnull().sum().sum()))
            c4.metric("Numéricos", len(cols_num))

    with tab2:
        cols_num = df.select_dtypes("number").columns.tolist()
        cols_cat = df.select_dtypes("object").columns.tolist()
        if not cols_num:
            st.warning("No se encontraron columnas numéricas.")
        else:
            chart_type = st.selectbox("Tipo de gráfica", ["Barras", "Línea", "Dispersión", "Histograma", "Pastel", "Mapa de calor"])
            col_y = st.selectbox("Eje Y / Valor", cols_num)
            opciones_x = cols_cat + cols_num
            col_x = st.selectbox("Eje X / Categoría", opciones_x)
            opciones_color = ["—"] + cols_cat
            color_sel = st.selectbox("Color por (opcional)", opciones_color)
            color_col = None if color_sel == "—" else color_sel
            common = dict(color_discrete_sequence=PALETTE, template="plotly_dark")
            if chart_type == "Barras":
                fig = px.bar(df, x=col_x, y=col_y, color=color_col, **common)
            elif chart_type == "Línea":
                fig = px.line(df, x=col_x, y=col_y, color=color_col, **common)
            elif chart_type == "Dispersión":
                fig = px.scatter(df, x=col_x, y=col_y, color=color_col, **common)
            elif chart_type == "Histograma":
                fig = px.histogram(df, x=col_y, color=color_col, **common)
            elif chart_type == "Pastel":
                fig = px.pie(df, names=col_x, values=col_y, **common)
            else:
                corr = df[cols_num].corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", template="plotly_dark")
            fig.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD", margin=dict(t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if not st.session_state.get("api_key"):
            st.warning("⚠️ Configura tu API Key de Anthropic primero.")
            return
        st.markdown("### 🤖 Análisis automático con Claude")
        if st.button("🔍 Generar análisis completo", type="primary"):
            stats_json = df.describe(include="all").to_json()
            sample = df.head(20).to_csv(index=False)
            prompt = f"""Analiza este conjunto de datos de una empresa colombiana y entrega:
1. Resumen ejecutivo (3-4 oraciones)
2. Hallazgos clave (top 5 insights numerados)
3. Oportunidades de mejora detectadas
4. Recomendaciones accionables

Muestra de datos (CSV):
{sample}

Estadísticas descriptivas (JSON):
{stats_json}
"""
            with st.spinner("Claude está analizando tus datos…"):
                try:
                    respuesta = call_claude(prompt)
                    st.session_state["ai_analysis"] = respuesta
                    st.markdown(respuesta)
                except Exception as e:
                    st.error(f"Error con la API: {e}")
        elif st.session_state.get("ai_analysis"):
            st.markdown(st.session_state["ai_analysis"])

        st.divider()
        st.markdown("### 💬 Pregunta específica")
        pregunta = st.text_input("¿Qué quieres saber sobre tus datos?", placeholder="Ej: ¿Cuáles son los productos con mayor margen?")
        if st.button("Preguntar") and pregunta:
            sample = df.head(50).to_csv(index=False)
            prompt = f"Datos:\n{sample}\n\nPregunta: {pregunta}"
            with st.spinner("Analizando…"):
                try:
                    st.markdown(call_claude(prompt))
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab4:
        cols_num = df.select_dtypes("number").columns.tolist()
        if cols_num:
            st.dataframe(df[cols_num].describe().T.style.format("{:.2f}"), use_container_width=True)
        st.markdown("**Valores nulos por columna:**")
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            st.dataframe(nulls.rename("Nulos"), use_container_width=True)
        else:
            st.success("✅ No hay valores nulos en el dataset.")
