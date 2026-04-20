import streamlit as st

def show():
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
        <h1 style="color:#00C2FF;font-size:2.4rem;font-weight:700;margin:0;">
            Tus datos, tu ventaja competitiva
        </h1>
        <p style="color:#7B9BB5;font-size:1.05rem;margin-top:.5rem;">
            Sube un archivo Excel o PDF y obtén insights con inteligencia artificial en segundos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, label, desc in [
        (c1, "📗", "Análisis de Excel", "Upload .xlsx → insights automáticos con IA"),
        (c2, "📄", "Análisis de PDF",   "Contratos, estados financieros, cámara de comercio"),
        (c3, "💬", "Chat con datos",    "Pregunta en español, obtén gráficas y respuestas"),
        (c4, "🔍", "Anomalías",         "Detecta valores atípicos y alertas automáticas"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#132030;border:1px solid #1a3a5c;border-radius:12px;
                        padding:1.2rem;text-align:center;height:160px;">
                <div style="font-size:2rem;">{icon}</div>
                <p style="color:#00C2FF;font-weight:600;margin:.4rem 0 .3rem;">{label}</p>
                <p style="color:#7B9BB5;font-size:.82rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Empieza ahora — sube tu archivo")
    uploaded = st.file_uploader(
        "Arrastra un Excel o PDF aquí",
        type=["xlsx", "xls", "pdf"],
        label_visibility="collapsed",
    )

    if uploaded:
        ext = uploaded.name.split(".")[-1].lower()
        st.success(f"Archivo **{uploaded.name}** cargado. Selecciona un módulo en el menú lateral.")
        st.session_state["uploaded_file"] = uploaded
        st.session_state["file_ext"] = ext

    st.divider()
    st.markdown("#### Como funciona?")
    s1, s2, s3, s4 = st.columns(4)
    for col, n, t, d in [
        (s1, "1", "Sube tu archivo",     "Excel o PDF desde tu computador"),
        (s2, "2", "IA lo analiza",        "Claude API procesa y extrae insights"),
        (s3, "3", "Visualiza resultados", "Graficas interactivas con Plotly"),
        (s4, "4", "Exporta tu reporte",   "PDF profesional listo para presentar"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#0a1520;border:1px solid #1a3a5c;border-radius:10px;
                        padding:1rem;text-align:center;">
                <div style="background:#00C2FF;color:#0D1B2A;font-weight:700;font-size:1.1rem;
                            width:32px;height:32px;border-radius:50%;margin:0 auto .6rem;
                            display:flex;align-items:center;justify-content:center;">{n}</div>
                <p style="color:#E8F4FD;font-weight:600;font-size:.9rem;margin:0 0 .2rem;">{t}</p>
                <p style="color:#7B9BB5;font-size:.78rem;margin:0;">{d}</p>
            </div>
            """, unsafe_allow_html=True)
