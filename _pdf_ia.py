import streamlit as st
import anthropic
import base64

def call_claude_pdf(pdf_b64, prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64},
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return msg.content[0].text

def show():
    st.markdown("## Analisis de Documentos PDF con IA")

    if not st.session_state.get("api_key"):
        with st.expander("Configurar API Key", expanded=True):
            key = st.text_input("API Key de Anthropic", type="password")
            if st.button("Guardar"):
                st.session_state["api_key"] = key
                st.success("Guardada")
        return

    f = None
    if st.session_state.get("file_ext") == "pdf":
        f = st.session_state.get("uploaded_file")

    uploaded = st.file_uploader("Sube tu documento PDF", type=["pdf"])
    if uploaded:
        f = uploaded
        st.session_state["uploaded_file"] = uploaded
        st.session_state["file_ext"] = "pdf"

    if not f:
        st.info("Sube un PDF para analizarlo con IA.")
        col1, col2, col3 = st.columns(3)
        for c, icon, t in [
            (col1, "🏛", "Camara de Comercio"),
            (col2, "📋", "Contratos y Acuerdos"),
            (col3, "📊", "Estados Financieros"),
        ]:
            with c:
                st.markdown(f"""
                <div style="background:#132030;border:1px solid #1a3a5c;border-radius:10px;
                            padding:1.2rem;text-align:center;">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <p style="color:#E8F4FD;font-weight:600;margin:.4rem 0;">{t}</p>
                </div>
                """, unsafe_allow_html=True)
        return

    pdf_bytes = f.read()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode()
    st.success(f"Archivo {f.name} cargado ({len(pdf_bytes)//1024} KB)")

    tipo = st.selectbox("Tipo de analisis", [
        "Resumen ejecutivo completo",
        "Extraccion de datos financieros",
        "Revision de clausulas contratos",
        "Datos de Camara de Comercio",
        "Analisis personalizado",
    ])

    prompts = {
        "Resumen ejecutivo completo": "Genera un resumen ejecutivo completo de este documento. Incluye objetivo principal, puntos clave, datos importantes, fechas relevantes y conclusiones. Responde en español.",
        "Extraccion de datos financieros": "Extrae todos los datos financieros: ingresos, gastos, utilidades, activos, pasivos, patrimonio, ratios financieros. Presentalo en formato estructurado. Responde en español.",
        "Revision de clausulas contratos": "Analiza este contrato y extrae partes involucradas, objeto del contrato, obligaciones, plazos, penalidades, clausulas de riesgo y recomendaciones. Responde en español.",
        "Datos de Camara de Comercio": "Extrae los datos del registro mercantil: razon social, NIT, representante legal, actividad economica, capital, matricula, renovaciones. Responde en español.",
        "Analisis personalizado": None,
    }

    prompt_custom = ""
    if tipo == "Analisis personalizado":
        prompt_custom = st.text_area("Escribe tu pregunta:", placeholder="Que quieres saber del documento?")

    prompt_final = prompts.get(tipo) or prompt_custom

    if st.button("Analizar con IA", type="primary") and prompt_final:
        with st.spinner("Claude esta leyendo tu documento..."):
            try:
                resultado = call_claude_pdf(pdf_b64, prompt_final, st.session_state["api_key"])
                st.session_state["pdf_resultado"] = resultado
            except Exception as e:
                st.error(f"Error: {e}")
                return

    if st.session_state.get("pdf_resultado"):
        st.divider()
        st.markdown("### Resultado del analisis")
        st.markdown(st.session_state["pdf_resultado"])
        st.divider()
        followup = st.text_input("Pregunta de seguimiento sobre el documento:")
        if st.button("Preguntar") and followup:
            with st.spinner("Analizando..."):
                try:
                    resp = call_claude_pdf(pdf_b64, followup, st.session_state["api_key"])
                    st.markdown(resp)
                except Exception as e:
                    st.error(f"Error: {e}")
