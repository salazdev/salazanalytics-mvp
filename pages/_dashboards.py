import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

PALETTE = ["#00C2FF","#7B2FBE","#00FFB3","#FF6B6B","#FFD93D","#4ECDC4"]

def show():
    st.markdown("## 📈 Dashboard Interactivo")

    df = st.session_state.get("df")
    if df is None:
        uploaded = st.file_uploader("Sube un Excel para generar el dashboard", type=["xlsx","xls"])
        if uploaded:
            df = pd.read_excel(uploaded)
            st.session_state["df"] = df
        else:
            st.info("👆 Carga un archivo Excel para construir tu dashboard.")
            return

    cols_num = df.select_dtypes("number").columns.tolist()
    cols_cat = df.select_dtypes("object").columns.tolist()

    if not cols_num:
        st.warning("El archivo no tiene columnas numéricas para graficar.")
        return

    st.markdown("### KPIs principales")
    kpi_cols = st.columns(min(len(cols_num), 4))
    for i, col in enumerate(cols_num[:4]):
        with kpi_cols[i]:
            total = df[col].sum()
            promedio = df[col].mean()
            st.metric(label=col, value=f"{total:,.0f}", delta=f"Prom: {promedio:,.1f}")

    st.divider()

    st.markdown("### Distribución y tendencias")
    c1, c2 = st.columns(2)

    with c1:
        y1 = st.selectbox("Métrica principal", cols_num, key="d_y1")
        if cols_cat:
            x1 = st.selectbox("Categoría", cols_cat, key="d_x1")
            fig1 = px.bar(df.groupby(x1)[y1].sum().reset_index(), x=x1, y=y1,
                          color_discrete_sequence=PALETTE, template="plotly_dark",
                          title=f"{y1} por {x1}")
        else:
            fig1 = px.histogram(df, x=y1, color_discrete_sequence=PALETTE, template="plotly_dark")
        fig1.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        if len(cols_num) >= 2:
            y2 = st.selectbox("Segunda métrica", cols_num, key="d_y2", index=min(1, len(cols_num)-1))
            fig2 = px.scatter(df, x=cols_num[0], y=y2, color=cols_cat[0] if cols_cat else
