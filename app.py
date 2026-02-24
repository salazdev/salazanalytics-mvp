import streamlit as st
import pandas as pd
import PyPDF2
import io
import re
from datetime import datetime
import os

# ------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (DEBE SER LO PRIMERO)
# ------------------------------------------------------------
st.set_page_config(
    page_title="SalazAnalytics - Procesamiento de Facturas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# FUNCIONES DE PROCESAMIENTO
# ------------------------------------------------------------
def extract_invoice_data_smart(text):
    """
    Versión mejorada para facturas colombianas
    """
    data = {
        "fecha": "No encontrada",
        "numero_factura": "No encontrado",
        "proveedor": "No encontrado",
        "nit": "No encontrado",
        "total": "No encontrado",
        "iva": "No encontrado",
        "subtotal": "No encontrado",
        "cufe": "No encontrado"
    }
    
    # Buscar fecha (formatos comunes)
    fecha_patterns = [
        r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{2}[/-]\d{2}[/-]\d{4})',
    ]
    for pattern in fecha_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["fecha"] = match.group(1)
            break
    
    # Buscar número de factura (mejorado)
    factura_patterns = [
        r'Factura[:\s]*[Nn]?[oÓ]?\.?\s*([A-Z0-9-]+)',
        r'FACTURA\s+([A-Z0-9-]+)',
        r'No\.?\s*Factura[:\s]*([A-Z0-9-]+)',
    ]
    for pattern in factura_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["numero_factura"] = match.group(1)
            break
    
    # Buscar proveedor (nombre de la empresa emisora)
    lines = text.split('\n')
    for i, line in enumerate(lines[:20]):
        line = line.strip()
        if (len(line) > 5 and 
            any(word in line.upper() for word in ['S.A.S', 'LTDA', 'SAS', 'LIMITADA']) or
            (line.isupper() and len(line.split()) > 1 and not re.search(r'\d{5,}', line))):
            data["proveedor"] = line
            break
    
    # Buscar NIT (mejorado para formato colombiano)
    nit_patterns = [
        r'NIT[:\s]*([0-9.-]+)',
        r'([0-9]{9,10})',
        r'([0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9])'
    ]
    for pattern in nit_patterns:
        match = re.search(pattern, text)
        if match:
            data["nit"] = match.group(1)
            break
    
    # Buscar TOTAL (ahora busca específicamente después de la palabra TOTAL)
    total_match = re.search(r'TOTAL[:\s]*[$]?\s*([0-9.,]+)', text, re.IGNORECASE)
    if total_match:
        data["total"] = total_match.group(1)
    else:
        # Si no encuentra TOTAL, busca al final del documento
        numbers = re.findall(r'[$]?\s*([0-9.,]+)', text)
        if numbers:
            data["total"] = numbers[-1]  # Toma el último número grande (suele ser el total)
    
    # Buscar IVA (mejorado)
    iva_patterns = [
        r'IVA[:\s]*[$]?\s*([0-9.,]+)',
        r'IVA\s*19%[:\s]*[$]?\s*([0-9.,]+)',
        r'Impuesto[:\s]*[$]?\s*([0-9.,]+)',
    ]
    for pattern in iva_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["iva"] = match.group(1)
            break
    
    # Buscar subtotal (útil para verificación)
    subtotal_match = re.search(r'Subtotal[:\s]*[$]?\s*([0-9.,]+)', text, re.IGNORECASE)
    if subtotal_match:
        data["subtotal"] = subtotal_match.group(1)
    
    # Buscar CUFE (para facturas electrónicas colombianas)
    cufe_match = re.search(r'([a-f0-9]{32,})', text, re.IGNORECASE)
    if cufe_match:
        data["cufe"] = cufe_match.group(1)
    
    return data
    
    # Buscar fecha (formatos comunes: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
    fecha_patterns = [
        r'(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(\d{4}[/-]\d{2}[/-]\d{2})',
        r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in fecha_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["fecha"] = match.group(1)
            break
    
    # Buscar número de factura
    factura_patterns = [
        r'(Factura|N[oÓ]\.?|Número)[:\s]*([A-Z0-9-]+)',
        r'FACTURA\s+([A-Z0-9-]+)',
        r'(\d{1,15})'
    ]
    for pattern in factura_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Tomar el último grupo que es el número
            data["numero_factura"] = match.group(len(match.groups()))
            break
    
    # Buscar proveedor (líneas que parezcan nombre de empresa)
    lines = text.split('\n')
    for line in lines[:15]:  # Buscar en primeras 15 líneas
        line = line.strip()
        if (len(line) > 5 and 
            any(word in line.upper() for word in ['S.A.S', 'LTDA', 'SAS', 'LIMITADA']) or
            (line.isupper() and len(line.split()) > 1 and not re.search(r'\d{5,}', line))):
            data["proveedor"] = line
            break
    
    # Buscar NIT
    nit_patterns = [
        r'NIT[:\s]*([0-9.-]+)',
        r'(\d{9,10})',
        r'(\d{3}\.\d{3}\.\d{3}-\d)'
    ]
    for pattern in nit_patterns:
        match = re.search(pattern, text)
        if match:
            data["nit"] = match.group(1)
            break
    
    # Buscar total
    total_patterns = [
        r'TOTAL[:\s]*[$]?([0-9.,]+)',
        r'Valor total[:\s]*[$]?([0-9.,]+)',
        r'([0-9.,]+)\s*$'
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["total"] = match.group(1)
            break
    
    # Buscar IVA
    iva_patterns = [
        r'IVA[:\s]*[$]?([0-9.,]+)',
        r'Impuesto[:\s]*[$]?([0-9.,]+)'
    ]
    for pattern in iva_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["iva"] = match.group(1)
            break
    
    # Buscar CUFE (para facturas electrónicas colombianas)
    cufe_match = re.search(r'([a-f0-9]{32,})', text, re.IGNORECASE)
    if cufe_match:
        data["cufe"] = cufe_match.group(1)
    
    return data

def format_currency(value):
    """Formatea valores como moneda"""
    try:
        if value and value != "No encontrado":
            # Limpiar el valor y convertir a número
            clean_value = re.sub(r'[^\d.,]', '', str(value))
            clean_value = clean_value.replace('.', '').replace(',', '.')
            num_value = float(clean_value)
            return f"${num_value:,.0f}".replace(',', '.')
    except:
        pass
    return value

# ------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ------------------------------------------------------------

# Título con logo (si tienes)
st.markdown("""
    <h1 style='text-align: center; color: #2E86AB;'>
        📊 SalazAnalytics
    </h1>
    <h3 style='text-align: center; color: #666; margin-top: -15px;'>
        Procesamiento inteligente de facturas para contadores
    </h3>
    <hr style='margin-bottom: 30px;'>
""", unsafe_allow_html=True)

# Sidebar con información del cliente
with st.sidebar:
    st.markdown("### 👤 Cliente")
    st.info("**Plan:** Profesional (Demo)")
    st.caption(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    st.markdown("### 📋 Instrucciones")
    st.markdown("""
    1. Sube tu factura en formato PDF
    2. La IA extraerá los datos automáticamente
    3. Revisa y descarga el resultado
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Estadísticas")
    st.metric("Facturas hoy", "0")
    st.metric("Límite mensual", "500")
    
    # Versión
    st.markdown("---")
    st.caption("v1.0.0 - MVP")

# Área principal
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Subir factura")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo PDF aquí",
        type=['pdf'],
        help="Selecciona el archivo PDF de la factura que deseas procesar"
    )
    
    if uploaded_file is not None:
        # Mostrar información del archivo
        file_size = len(uploaded_file.getvalue()) / 1024
        st.success(f"✅ **Archivo:** {uploaded_file.name}")
        st.caption(f"**Tamaño:** {file_size:.1f} KB")
        
        # Botón de procesar
        if st.button("🚀 Procesar factura", type="primary", use_container_width=True):
            with st.spinner("⏳ Procesando factura... esto puede tomar unos segundos"):
                # Guardar el archivo en sesión para mantenerlo
                st.session_state['uploaded_file'] = uploaded_file
                st.session_state['file_name'] = uploaded_file.name
                
                # Extraer texto del PDF
                text, num_pages = extract_text_from_pdf(uploaded_file)
                
                if num_pages > 0 and "Error" not in text:
                    # Extraer datos
                    extracted_data = extract_invoice_data_smart(text)
                    st.session_state['extracted_data'] = extracted_data
                    st.session_state['full_text'] = text
                    st.session_state['num_pages'] = num_pages
                    st.session_state['processed'] = True
                    st.rerun()
                else:
                    st.error(f"❌ {text}")
    else:
        # Mostrar placeholder cuando no hay archivo
        st.info("👆 Comienza subiendo una factura")
        
        # Ejemplo visual
        with st.expander("📋 Ver ejemplo de resultado"):
            st.json({
                "fecha": "22/02/2025",
                "proveedor": "Ejemplo S.A.S.",
                "nit": "901.234.567-8",
                "total": "$1,250,000",
                "iva": "$237,500",
                "cufe": "f1a2b3c4d5e6..."
            })

with col2:
    st.markdown("### 📊 Resultados")
    
    if 'processed' in st.session_state and st.session_state['processed']:
        data = st.session_state['extracted_data']
        
        # Crear pestañas para diferentes vistas
        tab1, tab2, tab3 = st.tabs(["📋 Datos extraídos", "📝 Texto completo", "📥 Exportar"])
        
        with tab1:
            # Mostrar datos en tarjetas
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("📅 Fecha", data["fecha"])
                st.metric("🏢 Proveedor", data["proveedor"])
                st.metric("💰 Total", format_currency(data["total"]))
            
            with col_b:
                st.metric("🔢 N° Factura", data["numero_factura"])
                st.metric("🆔 NIT", data["nit"])
                st.metric("🧾 IVA", format_currency(data["iva"]))
            
            if data["cufe"] != "No encontrado" and len(data["cufe"]) > 10:
                with st.expander("🔍 Ver CUFE"):
                    st.code(data["cufe"], language="text")
            
            st.caption(f"📄 Páginas procesadas: {st.session_state['num_pages']}")
        
        with tab2:
            st.text_area(
                "Contenido extraído del PDF",
                st.session_state['full_text'][:3000] + ("..." if len(st.session_state['full_text']) > 3000 else ""),
                height=300
            )
        
        with tab3:
            # Preparar datos para exportar
            export_data = data.copy()
            export_data["archivo_original"] = st.session_state['file_name']
            export_data["fecha_procesamiento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Crear DataFrame
            df = pd.DataFrame([export_data])
            
            # Opciones de exportación
            col_csv, col_json = st.columns(2)
            
            with col_csv:
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"factura_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_json:
                json_str = df.to_json(orient='records', indent=2, force_ascii=False)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str.encode('utf-8'),
                    file_name=f"factura_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.info("💡 Estos formatos son compatibles con Excel, Contasol y otros software contables.")
    else:
        st.info("👈 Sube una factura para ver los resultados")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>© 2025 SalazAnalytics - Procesamiento inteligente de facturas para contadores profesionales</p>
        <p>Versión MVP • Contacto: soporte@salazanalytics.com</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Inicializar session state si no existe
if 'processed' not in st.session_state:
    st.session_state['processed'] = False