import streamlit as st
import anthropic
import base64
import requests

N8N_WEBHOOK = "https://n8n.salazanalytics.com/webhook/analisis-contable"

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
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64
                    },
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
            if st.button("Guardar API Key"):
                st.session_state["api_key"] = key
                st.success("Guardada")

    uploaded = st.file_uploader(
        "Sube tu documento PDF",
        type=["pdf"],
        help="Maximo 10MB"
    )

    if not uploaded:
        st.info("Sube un PDF para analizarlo con IA.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style="background:#132030;border:1px solid #1a3a5c;
                        border-radius:10px;padding:1.2rem;text-align:center;">
                <div style="font-size:1.8rem;">🏛</div>
                <p style="color:#E8F4FD;font-weight:600;margin:.4rem 0;">Camara de Comercio</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:#132030;border:1px solid #1a3a5c;
                        border-radius:10px;padding:1.2rem;text-align:center;">
                <div style="font-size:1.8rem;">📋</div>
                <p style="color:#E8F4FD;font-weight:600;margin:.4rem 0;">Contratos</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style="background:#132030;border:1px solid #1a3a5c;
                        border-radius:10px;padding:1.2rem;text-align:center;">
                <div style="font-size:1.8rem;">📊</div>
                <p style="color:#E8F4FD;font-weight:600;margin:.4rem 0;">Estados Financieros</p>
            </div>""", unsafe_allow_html=True)
        return

    pdf_bytes = uploaded.read()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode()
    st.success(f"Archivo cargado: {uploaded.name} ({len(pdf_bytes)//1024} KB)")

    tipo = st.selectbox("Tipo de analisis", [
        "Resumen ejecutivo completo",
        "Extraccion de datos financieros",
        "Revision de clausulas contratos",
        "Datos de Camara de Comercio",
        "Analisis personalizado",
    ])

    prompts = {
        "Resumen ejecutivo completo": "Genera un resumen ejecutivo completo de este documento. Incluye objetivo principal, puntos clave, datos importantes, fechas relevantes y conclusiones. Responde en espanol.",
        "Extraccion de datos financieros": "Extrae todos los datos financieros: ingresos, gastos, utilidades, activos, pasivos, patrimonio. Presentalo en formato estructurado. Responde en espanol.",
        "Revision de clausulas contratos": "Analiza este contrato: partes involucradas, obligaciones, plazos, penalidades, clausulas de riesgo y recomendaciones. Responde en espanol.",
        "Datos de Camara de Comercio": "Extrae: razon social, NIT, representante legal, actividad economica, capital, matricula. Responde en espanol.",
        "Analisis personalizado": None,
    }

    prompt_custom = ""
    if tipo == "Analisis personalizado":
        prompt_custom = st.text_area("Escribe tu pregunta:", placeholder="Que quieres saber del documento?")

    prompt_final = prompts.get(tipo) or prompt_custom

    if st.button("Analizar con IA", type="primary"):
        if not prompt_final:
            st.warning("Escribe tu pregunta primero.")
            return
        if not st.session_state.get("api_key"):
            st.warning("Configura tu API Key primero.")
            return
        with st.spinner("Claude esta leyendo tu documento..."):
            try:
                resultado = call_claude_pdf(pdf_b64, prompt_final, st.session_state["api_key"])
                st.session_state["pdf_resultado"] = resultado
            except Exception as e:
                st.error(f"Error: {e}")
                return

    if st.session_state.get("pdf_resultado"):
        st.divider()
        st.markdown("### Resultado")
        st.markdown(st.session_state["pdf_resultado"])
        st.divider()
        followup = st.text_input("Pregunta de seguimiento:")
        if st.button("Preguntar") and followup:
            with st.spinner("Analizando..."):
                try:
                    resp = call_claude_pdf(pdf_b64, followup, st.session_state["api_key"])
                    st.markdown(resp)
                except Exception as e:
                    st.error(f"Error: {e}")
