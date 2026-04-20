import streamlit as st
import anthropic, base64

def call_claude_pdf(pdf_b64: str, prompt: str, api_key: str) -> str:
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
    st.markdown("## 📄 Análisis de Documentos PDF con IA")

    if not st.session_state.get("api_key"):
        with st.expander("🔑 Configurar API Key", expanded=True):
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
        st.info("👆 Sube un PDF para analizarlo con IA.")
        col1, col2, col3 = st.columns(3)
        for c, icon, t in [
            (col1, "🏛️", "Cámara de Comercio"),
            (col2, "📋", "Contratos y Acuerdos"),
            (col3, "💰", "Estados Financ
