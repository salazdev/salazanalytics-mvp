import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

PALETTE = ["#00C2FF","#FF6B6B","#7B2FBE","#00FFB3","#FFD93D"]

def detectar_anomalias(serie: pd.Series, n_sigma: float = 2.5):
    media = serie.mean()
    std = serie.std()
    lower = media - n_sigma * std
    upper = media + n_sigma * std
    mask = (serie < lower) | (serie > upper)
    return mask, lower, upper

def show():
    st.markdown("## 🔍 Detección de Anomalías")
    st.markdown("<p style='color:#7B9BB5'>Identifica valores atípicos y alertas automáticas en tus datos.</p>", unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        uploaded = st.file_uploader("Sube un Excel", type=["xlsx","xls"])
        if uploaded:
            df = pd.read_excel(uploaded)
            st.session_state["df"] = df
        else:
            st.info("👆 Carga un archivo Excel para analizar anomalías.")
            return

    cols_num = df.select_dtypes("number").columns.tolist()
    if not cols_num:
        st.warning("No hay columnas numéricas en el dataset.")
        return

    col_sel = st.selectbox("Columna a analizar", cols_num)
    n_sigma = st.slider("Sensibilidad (sigma)", 1.0, 4.0, 2.5, 0.1)

    serie = df[col_sel].dropna()
    mask, lower, upper = detectar_anomalias(serie, n_sigma)
    anomalias_count = mask.sum()
    pct = 100 * anomalias_count / len(serie)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total registros",  len(serie))
    c2.metric("Anomalías",        int(anomalias_count), delta=f"{pct:.1f}%", delta_color="inverse")
    c3.metric("Límite inferior",  f"{lower:,.2f}")
    c4.metric("Límite superior",  f"{upper:,.2f}")

    st.divider()

    idx = np.arange(len(serie))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=idx, y=serie.values, mode="lines", name="Datos",
                             line=dict(color="#00C2FF", width=1.5)))
    fig.add_trace(go.Scatter(x=idx[mask], y=serie.values[mask], mode="markers",
                             name="Anomalía", marker=dict(color="#FF6B6B", size=9, symbol="x")))
    fig.add_hline(y=upper, line_dash="dash", line_color="#FFD93D", annotation_text="Límite superior")
    fig.add_hline(y=lower, line_dash="dash", line_color="#FFD93D", annotation_text="Límite inferior")
    fig.update_layout(
        title=f"Anomalías en {col_sel}",
        paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD",
        legend=dict(bgcolor="#132030"), margin=dict(t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    if anomalias_count > 0:
        st.markdown(f"### 🚨 {anomalias_count} registros anómalos detectados")
        df_anom = df[mask.reindex(df.index, fill_value=False)].copy()
        df_anom["_anomalia_en"] = col_sel
        df_anom["_valor"] = serie[mask].values
        df_anom["_desviacion"] = ((serie[mask] - serie.mean()) / serie.std()).round(2).values
        st.dataframe(df_anom, use_container_width=True)

        st.divider()
        st.markdown("### 📊 Resumen en todas las columnas")
        resumen = []
        for c in cols_num:
            s = df[c].dropna()
            m, lo, hi = detectar_anomalias(s, n_sigma)
            resumen.append({
                "Columna": c,
                "Total": len(s),
                "Anomalías": int(m.sum()),
                "Porcentaje": f"{100*m.sum()/len(s):.1f}%",
                "Mín": f"{s.min():,.2f}",
                "Máx": f"{s.max():,.2f}"
            })
        st.dataframe(pd.DataFrame(resumen), use_container_width=True)
    else:
        st.success("✅ No se detectaron anomalías con el nivel de sensibilidad actual.")
