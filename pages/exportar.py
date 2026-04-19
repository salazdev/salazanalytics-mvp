import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import anthropic
from datetime import datetime
import base64

def call_claude(prompt: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

def df_to_html_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    style = """
    <style>
    table{border-collapse:collapse;width:100%;font-size:12px;font-family:Arial,sans-serif;}
    th{background:#0D1B2A;color:#00C2FF;padding:8px 10px;text-align:left;border:1px solid #1a3a5c;}
    td{padding:7px 10px;border:1px solid #ddd;color:#1a1a2e;}
    tr:nth-child(even){background:#f5f8fc;}
    </style>
    """
    return style + df.head(max_rows).to_html(index=False)

def show():
    st.markdown("## 📑 Exportar Reporte")
    st.markdown("<p style='color:#7B9BB5'>Genera un reporte profesional listo para presentar.</p>", unsafe_allow_html=True)

    df = st.session_state.get("df")

    st.markdown("### ⚙️ Configuración del reporte")
    c1, c2 = st.columns(2)
    with c1:
        empresa = st.text_input("Nombre de la empresa", value="Mi Empresa S.A.S.")
        autor = st.text_input("Preparado por", value="SalazAnalytics")
    with c2:
        titulo = st.text_input("Título del reporte", value="Análisis de Datos Gerencial")
        fecha = st.date_input("Fecha", value=datetime.today())

    incluir_ia = st.checkbox("✅ Incluir análisis narrativo con IA", value=True)
    incluir_tabla = st.checkbox("✅ Incluir tabla de datos (primeras 20 filas)", value=True)
    incluir_stats = st.checkbox("✅ Incluir estadísticas descriptivas", value=True)

    if st.button("📥 Generar reporte HTML", type="primary"):
        if df is None:
            st.warning("No hay datos cargados. Ve al módulo de Excel primero.")
            return

        cols_num = df.select_dtypes("number").columns.tolist()

        ai_text = ""
        if incluir_ia and st.session_state.get("api_key"):
            with st.spinner("Generando análisis con IA…"):
                sample = df.head(30).to_csv(index=False)
                prompt = f"""Genera un informe gerencial profesional en español para una empresa colombiana basado en estos datos:
{sample}

Incluye: Resumen ejecutivo, hallazgos clave (5 puntos), riesgos identificados y recomendaciones estratégicas.
Usa un tono profesional y formal."""
                try:
                    ai_text = call_claude(prompt, st.session_state["api_key"])
                except:
                    ai_text = "No se pudo generar el análisis con IA."

        chart_html = ""
        if cols_num:
            fig = px.bar(df.head(20), y=cols_num[0],
                         color_discrete_sequence=["#00C2FF"],
                         template="plotly_white", title=f"Vista general: {cols_num[0]}")
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")

        stats_html = ""
        if incluir_stats and cols_num:
            stats_html = "<h2>Estadísticas descriptivas</h2>" + df[cols_num].describe().T.to_html()

        tabla_html = f"<h2>Muestra de datos</h2>{df_to_html_table(df)}" if incluir_tabla else ""
        ai_section = f"<h2>Análisis con Inteligencia Artificial</h2><div style='white-space:pre-wrap'>{ai_text}</div>" if ai_text else ""

        html_report = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:#fff;color:#1a1a2e;}}
  .header{{background:#0D1B2A;color:white;padding:2.5rem 3rem;}}
  .header h1{{color:#00C2FF;margin:0 0 .3rem;font-size:1.8rem;}}
  .header p{{margin:.2rem 0;color:#7B9BB5;font-size:.9rem;}}
  .content{{padding:2rem 3rem;}}
  h2{{color:#0D1B2A;border-bottom:3px solid #00C2FF;padding-bottom:.4rem;margin-top:2rem;}}
  .badge{{display:inline-block;background:#00C2FF;color:#0D1B2A;padding:3px 12px;border-radius:20px;font-size:.8rem;font-weight:700;}}
  table{{border-collapse:collapse;width:100%;margin:.5rem 0;}}
  th{{background:#0D1B2A;color:#00C2FF;padding:8px 10px;text-align:left;}}
  td{{padding:7px 10px;border-bottom:1px solid #eee;}}
  tr:nth-child(even){{background:#f8fafc;}}
  .footer{{background:#0D1B2A;color:#7B9BB5;text-align:center;padding:1.5rem;font-size:.8rem;margin-top:2rem;}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 {titulo}</h1>
  <p>Empresa: <strong style="color:white">{empresa}</strong></p>
  <p>Preparado por: {autor} &nbsp;|&nbsp; Fecha: {fecha.strftime('%d/%m/%Y')}</p>
  <p><span class="badge">SalazAnalytics</span> &nbsp; salazanalytics.com</p>
</div>
<div class="content">
  {ai_section}
  {chart_html}
  {tabla_html}
  {stats_html}
</div>
<div class="footer">Reporte generado por SalazAnalytics · salazanalytics.com · {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</body></html>"""

        b64 = base64.b64encode(html_report.encode()).decode()
        filename = f"reporte_salazanalytics_{datetime.today().strftime('%Y%m%d')}.html"
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display:inline-block;background:#00C2FF;color:#0D1B2A;font-weight:700;padding:.7rem 1.5rem;border-radius:8px;text-decoration:none;font-size:1rem;">⬇️ Descargar reporte HTML</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Reporte generado. Haz clic para descargarlo.")
        st.info("💡 Abre el HTML en tu navegador e imprime como PDF con Ctrl+P.")
