import streamlit as st
import requests
import os

def show():
    st.header("📄 Análisis de Documentos con IA")
    st.markdown("""
        Sube documentos legales o financieros (Cámara de Comercio, Balances) 
        para obtener un análisis normativo y predicciones financieras.
    """)

    # Configuración del Webhook (URL interna de Easypanel para mayor velocidad)
    # Ejemplo: http://n8n:5678/webhook/analisis-contable
    N8N_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/analisis-contable")

    uploaded_file = st.file_uploader("Cargar PDF", type=["pdf"], help="Máximo 10MB")

    if uploaded_file is not None:
        if st.button("🚀 Iniciar Análisis Inteligente"):
            with st.spinner("Procesando documento con n8n y Mirofish..."):
                try:
                    # Preparar el archivo para el envío
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {
                        "usuario": st.session_state.get("usuario", "anonimo"),
                        "filename": uploaded_file.name
                    }

                    # Envío al orquestador n8n
                    response = requests.post(N8N_URL, files=files, data=data, timeout=60)
                    
                    if response.status_code == 200:
                        resultado = response.json()
                        mostrar_resultados(resultado)
                    else:
                        st.error(f"❌ Error en el servidor (n8n): {response.status_code}")
                
                except Exception as e:
                    st.error(f"⚠️ Error de conexión: {str(e)}")

def mostrar_resultados(datos):
    """Muestra el análisis retornado por n8n e inteligencia de Mirofish"""
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Hallazgos Legales")
        # Datos extraídos por n8n (AI Agent)
        st.write(f"**Empresa:** {datos.get('empresa', 'No detectada')}")
        st.write(f"**Activos Totales:** ${datos.get('activos', 0):,.2f}")
        
        # Lógica de Revisoría Fiscal aplicada en n8n
        if datos.get('requiere_revisor'):
            st.warning("⚠️ **Alerta:** Según sus activos, esta empresa está obligada a tener Revisor Fiscal.")
        else:
            st.success("✅ Cumple con los requisitos mínimos actuales.")

    with col2:
        st.subheader("🔮 Predicción Mirofish")
        # Datos provenientes de tu motor de predicción
        st.metric("Proyección Flujo de Caja", f"${datos.get('prediccion_flujo', 0):,.2f}")
        st.info(f"**Análisis:** {datos.get('comentario_ia', 'Sin comentarios')}")

    if "grafica_datos" in datos:
        st.line_chart(datos["grafica_datos"])
