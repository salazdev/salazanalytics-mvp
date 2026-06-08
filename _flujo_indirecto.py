"""
_flujo_indirecto.py  —  SalazAnalytics
Micro-activo: Estado de Flujos de Caja (Método Indirecto)
Parser universal — acepta cualquier formato de software contable
Siigo · World Office · Alegra · SAP · QuickBooks · Excel manual
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ── Paleta ───────────────────────────────────────────────────────────────────
PALETTE  = ["#00C2FF", "#7B2FBE", "#00FFB3", "#FF6B6B", "#FFD93D", "#4ECDC4"]
BG_DARK  = "#0D1B2A"
BG_CARD  = "#132030"
BG_DEEP  = "#0a1520"
BORDER   = "#1a3a5c"
TEXT_SEC = "#7B9BB5"
ACCENT   = "#00C2FF"
DANGER   = "#FF6B6B"
SUCCESS  = "#00FFB3"
WARN     = "#FFD93D"
PURPLE   = "#7B2FBE"

# Categorías conocidas de secciones
SECCIONES = {
    "operacion":     ["OPERACI", "OPERATIVA", "OPERATING"],
    "inversion":     ["INVERSI", "INVERSIÓN", "INVESTING", "CAPITAL"],
    "financiamiento":["FINANC", "FINANCING"],
    "conciliacion":  ["CONCILI", "SALDO", "EFECTIVO", "CASH"],
}

TOTALES_KEYWORDS = [
    "FLUJO DE CAJA OPERATIVO", "FLUJO DE CAJA DE INVERSIÓN",
    "FLUJO DE CAJA DE FINANCIAMIENTO", "FLUJO DE CAJA DE FINANCIAMIENTO",
    "AUMENTO", "DISMINUCIÓN", "SALDO FINAL", "SALDO INICIAL",
    "FCO", "FCI", "FCF", "TOTAL", "NETO",
]


# ── Utilidades ────────────────────────────────────────────────────────────────
def fmt_num(v, escala=""):
    try:
        if abs(v) >= 1_000_000:
            return f"${v/1_000_000:,.1f}M{escala}"
        elif abs(v) >= 1_000:
            return f"${v/1_000:,.0f}K{escala}"
        return f"${v:,.0f}{escala}"
    except Exception:
        return str(v)


def card_html(titulo, valor, color=ACCENT, sub=""):
    sub_html = f"<p style='color:{TEXT_SEC};font-size:.73rem;margin:.15rem 0 0;'>{sub}</p>" if sub else ""
    return f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;
                padding:.9rem 1rem;text-align:center;">
        <p style="color:{TEXT_SEC};font-size:.75rem;margin:0 0 .2rem;">{titulo}</p>
        <p style="color:{color};font-weight:700;font-size:1.35rem;margin:0;">{valor}</p>
        {sub_html}
    </div>"""


def plot_base(title=""):
    cfg = dict(paper_bgcolor=BG_DARK, plot_bgcolor=BG_DARK,
               font_color="#E8F4FD", legend=dict(bgcolor=BG_CARD))
    if title:
        cfg["title"] = title
    return cfg


def es_seccion(texto):
    t = str(texto).upper().strip()
    for _, keys in SECCIONES.items():
        for k in keys:
            if k in t:
                return True
    return False


def es_total(texto):
    t = str(texto).upper().strip()
    return any(k in t for k in TOTALES_KEYWORDS)


def color_valor(v):
    try:
        return SUCCESS if float(v) >= 0 else DANGER
    except Exception:
        return TEXT_SEC


# ── Parser universal ─────────────────────────────────────────────────────────
def parse_flujo_excel(df_raw):
    """
    Detecta automáticamente:
    - Fila de encabezados (contiene años: 'Año X', '20XX', 'Período X', etc.)
    - Columna de conceptos
    - Columnas numéricas por período
    Retorna: (df_data, años, metadata)
    """
    header_row = None
    años = []

    # Buscar fila de encabezados
    for i, row in df_raw.iterrows():
        vals = [str(v) for v in row.values if pd.notna(v)]
        año_hits = sum(1 for v in vals if
                       any(p in v.upper() for p in ["AÑO", "YEAR", "PERÍODO", "PERIODO"]) or
                       (v.strip().isdigit() and 2000 <= int(v.strip()) <= 2040))
        if año_hits >= 2:
            header_row = i
            break

    if header_row is None:
        return None, [], {}

    # Extraer encabezados
    headers = df_raw.iloc[header_row].tolist()
    col_concepto = 0
    cols_años = []

    for j, h in enumerate(headers):
        h_str = str(h).upper().strip() if pd.notna(h) else ""
        if ("AÑO" in h_str or "YEAR" in h_str or "PERÍODO" in h_str or "PERIODO" in h_str or
                (h_str.isdigit() and 2000 <= int(h_str) <= 2040)):
            cols_años.append((j, str(h).strip()))
        elif "CONCEPTO" in h_str or "DESCRIPCI" in h_str or "LÍNEA" in h_str or "LINEA" in h_str:
            col_concepto = j

    if not cols_años:
        return None, [], {}

    años = [a[1] for a in cols_años]
    idx_años = [a[0] for a in cols_años]

    # Metadatos (filas antes del header)
    metadata = {}
    for i in range(header_row):
        for v in df_raw.iloc[i].values:
            if pd.notna(v) and str(v).strip():
                if "empresa" not in metadata:
                    metadata["empresa"] = str(v).strip()
                elif "titulo" not in metadata:
                    metadata["titulo"] = str(v).strip()
                break

    # Extraer datos
    rows = []
    seccion_actual = "General"
    for i in range(header_row + 1, len(df_raw)):
        row = df_raw.iloc[i]
        concepto = str(row.iloc[col_concepto]).strip() if pd.notna(row.iloc[col_concepto]) else ""
        if not concepto or concepto == "nan":
            continue

        vals = {}
        for j, año in zip(idx_años, años):
            try:
                v = row.iloc[j]
                vals[año] = float(str(v).replace(",", "").replace(" ", "")) if pd.notna(v) else 0.0
            except Exception:
                vals[año] = 0.0

        if es_seccion(concepto):
            seccion_actual = concepto
            continue

        tipo = "total" if es_total(concepto) else "item"
        rows.append({"concepto": concepto, "seccion": seccion_actual,
                     "tipo": tipo, **vals})

    if not rows:
        return None, años, metadata

    df_data = pd.DataFrame(rows)
    return df_data, años, metadata


# ── Proyección ────────────────────────────────────────────────────────────────
def proyectar(valores, n=3, factor=1.0):
    if len(valores) < 2:
        return [valores[-1] * factor if valores else 0] * n
    x = np.arange(len(valores))
    m, b = np.polyfit(x, valores, 1)
    x_fut = np.arange(len(valores), len(valores) + n)
    proj = m * x_fut + b
    reciente = np.mean(valores[-min(3, len(valores)):])
    return (proj * 0.4 + reciente * 0.6) * factor


# ── Datos demo ────────────────────────────────────────────────────────────────
def demo_data():
    data = {
        "concepto": [
            "Utilidad Neta del Ejercicio",
            "Depreciaciones y Amortizaciones",
            "Variación en Cuentas por Cobrar",
            "Variación en Inventarios",
            "Variación en Cuentas por Pagar",
            "FLUJO DE CAJA OPERATIVO (FCO)",
            "Adquisición de Propiedad y Equipo (CAPEX)",
            "Inversión en Activos Intangibles",
            "Venta de Activos",
            "FLUJO DE CAJA DE INVERSIÓN (FCI)",
            "Nuevos Préstamos Bancarios",
            "Amortización de Deuda",
            "Pago de Dividendos",
            "FLUJO DE CAJA DE FINANCIAMIENTO (FCF)",
            "AUMENTO / DISMINUCIÓN NETO DE EFECTIVO",
            "Saldo Inicial de Caja",
            "SALDO FINAL DE CAJA Y EQUIVALENTES",
        ],
        "seccion": [
            "ACTIVIDADES DE OPERACIÓN"] * 6 + [
            "ACTIVIDADES DE INVERSIÓN"] * 4 + [
            "ACTIVIDADES DE FINANCIAMIENTO"] * 4 + [
            "CONCILIACIÓN Y SALDOS"] * 3,
        "tipo": ["item"] * 5 + ["total"] + ["item"] * 3 + ["total"] +
                ["item"] * 3 + ["total"] + ["total"] * 3,
        "Año 1": [15000, 3500, -1200, -2500, 1800, 17750,
                  -8000, -1500, 500, -8800,
                  8000, -3000, -4000, 5200,
                  14150, 4500, 18600],
        "Año 2": [18500, 3700, -1500, -800, 1200, 22550,
                  -9500, -1200, 0, -10450,
                  4000, -4500, -5000, -6220,
                  5880, 18600, 24500],
        "Año 3": [22000, 3900, -1800, -1100, 1400, 25970,
                  -6000, -1000, 1200, -5500,
                  2000, -5000, -6000, -10550,
                  9920, 24500, 34390],
        "Año 4": [26500, 4100, -2000, -1300, 1600, 30750,
                  -5000, -800, 0, -5450,
                  0, -5500, -7500, -13380,
                  11920, 34390, 46350],
        "Año 5": [31000, 4300, -2200, -1500, 1900, 35650,
                  -5500, -900, 300, -5700,
                  0, -6000, -9000, -15210,
                  14740, 46350, 61100],
    }
    return pd.DataFrame(data), ["Año 1", "Año 2", "Año 3", "Año 4", "Año 5"], {
        "empresa": "SALAZ ANALYTICS",
        "titulo": "Estado de Flujos de Caja Proyectado (Método Indirecto)"
    }


# ════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
def show():
    st.markdown("## 📊 Flujo de Caja — Método Indirecto")
    st.markdown(
        f"<p style='color:{TEXT_SEC}'>Analiza tu Estado de Flujos proyectado. "
        f"Compatible con cualquier software contable.</p>",
        unsafe_allow_html=True)

    # ── Carga ────────────────────────────────────────────────────────────────
    fuente = st.radio("Fuente", ["📂 Cargar Excel", "📋 Datos demo"],
                      horizontal=True, key="fi_fuente")

    df_data, años, meta = None, [], {}

    if fuente == "📂 Cargar Excel":
        uploaded = st.file_uploader(
            "Sube tu Estado de Flujos de Caja (.xlsx)",
            type=["xlsx", "xls"], key="fi_upload",
            help="Acepta exportaciones de Siigo, World Office, Alegra, SAP, QuickBooks o Excel manual.")

        if uploaded:
            try:
                sheets = pd.read_excel(uploaded, sheet_name=None, header=None)
                sheet_name = st.selectbox("Hoja", list(sheets.keys()), key="fi_sheet")
                df_raw = sheets[sheet_name]
                df_data, años, meta = parse_flujo_excel(df_raw)

                if df_data is None:
                    st.warning(
                        "⚠️ No pude detectar el formato automáticamente. "
                        "Asegúrate de que el archivo tenga columnas con 'Año 1', 'Año 2'... "
                        "o años como 2022, 2023. Si el formato es muy diferente, "
                        "escríbeme cómo está estructurado y lo adapto.")
                    st.dataframe(df_raw.head(10), use_container_width=True)
                    return
                else:
                    st.success(
                        f"✅ **{len(df_data)} conceptos** detectados · "
                        f"**{len(años)} períodos**: {', '.join(años)}")
            except Exception as e:
                st.error(f"Error leyendo archivo: {e}")
                return
    else:
        df_data, años, meta = demo_data()
        st.info("📋 Datos demo — SALAZ ANALYTICS, proyección 5 años.")

    if df_data is None or len(años) == 0:
        return

    # ── Metadatos ────────────────────────────────────────────────────────────
    empresa = meta.get("empresa", "")
    titulo  = meta.get("titulo", "Estado de Flujos de Caja")
    if empresa or titulo:
        st.markdown(
            f"<div style='background:{BG_CARD};border:1px solid {BORDER};"
            f"border-radius:8px;padding:.6rem 1rem;margin-bottom:.5rem;'>"
            f"<p style='color:{ACCENT};font-weight:600;font-size:.85rem;margin:0;'>{empresa}</p>"
            f"<p style='color:{TEXT_SEC};font-size:.78rem;margin:0;'>{titulo}</p>"
            f"</div>", unsafe_allow_html=True)

    # ── Extraer totales clave ────────────────────────────────────────────────
    totales = df_data[df_data["tipo"] == "total"]

    def get_total(keywords):
        for kw in keywords:
            match = totales[totales["concepto"].str.upper().str.contains(kw, na=False)]
            if len(match):
                return match.iloc[0]
        return None

    fco_row = get_total(["FCO", "OPERATIVO", "OPERACIÓN", "OPERACION"])
    fci_row = get_total(["FCI", "INVERSIÓN", "INVERSION", "INVESTING"])
    fcf_row = get_total(["FCF", "FINANCIAMIENTO", "FINANCIACIÓN", "FINANCING"])
    neto_row = get_total(["AUMENTO", "DISMINUCIÓN", "NETO DE EFECTIVO", "NET CASH"])
    saldo_final_row = get_total(["SALDO FINAL", "ENDING", "FIN DE AÑO"])
    saldo_ini_row   = get_total(["SALDO INICIAL", "BEGINNING", "PRINCIPIO"])

    def serie(row):
        if row is None:
            return [0.0] * len(años)
        return [float(row.get(a, 0) or 0) for a in años]

    fco_vals  = serie(fco_row)
    fci_vals  = serie(fci_row)
    fcf_vals  = serie(fcf_row)
    neto_vals = serie(neto_row) if neto_row is not None else [f+i+c for f,i,c in zip(fco_vals,fci_vals,fcf_vals)]
    saldo_final_vals = serie(saldo_final_row)
    saldo_ini_vals   = serie(saldo_ini_row)

    # ════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Resumen Ejecutivo",
        "💧 Cascada por Año",
        "📈 Tendencias",
        "🔮 Proyección",
        "⚠️ Alertas",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — RESUMEN EJECUTIVO
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📋 Vista ejecutiva")

        # Selector de año
        año_sel = st.select_slider("Ver año", options=años, key="fi_año_sel")
        idx_sel = años.index(año_sel)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card_html("Flujo Operativo",
                              fmt_num(fco_vals[idx_sel]),
                              SUCCESS if fco_vals[idx_sel] >= 0 else DANGER,
                              "FCO"),
                    unsafe_allow_html=True)
        c2.markdown(card_html("Flujo Inversión",
                              fmt_num(fci_vals[idx_sel]),
                              WARN if fci_vals[idx_sel] < 0 else SUCCESS,
                              "FCI — inversión normal si es negativo"),
                    unsafe_allow_html=True)
        c3.markdown(card_html("Flujo Financiamiento",
                              fmt_num(fcf_vals[idx_sel]),
                              SUCCESS if fcf_vals[idx_sel] >= 0 else ACCENT,
                              "FCF"),
                    unsafe_allow_html=True)
        c4.markdown(card_html("Saldo Final de Caja",
                              fmt_num(saldo_final_vals[idx_sel]) if saldo_final_vals[idx_sel] != 0 else fmt_num(neto_vals[idx_sel]),
                              SUCCESS if (saldo_final_vals[idx_sel] or neto_vals[idx_sel]) >= 0 else DANGER,
                              año_sel),
                    unsafe_allow_html=True)

        st.divider()

        # Tabla completa del año seleccionado
        st.markdown(f"#### Detalle completo — {año_sel}")
        df_año = df_data[["concepto", "seccion", "tipo", año_sel]].copy()
        df_año.columns = ["Concepto", "Sección", "Tipo", "Valor"]
        df_año["Valor"] = df_año["Valor"].apply(lambda v: fmt_num(v) if pd.notna(v) else "—")

        # Colorear totales
        def estilo_fila(row):
            if row["Tipo"] == "total":
                return [f"color:{ACCENT};font-weight:600"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_año[["Concepto", "Sección", "Valor"]],
            use_container_width=True, hide_index=True)

        # Evolución del saldo final
        st.markdown("#### Evolución del saldo de caja")
        fig = go.Figure()

        if any(v != 0 for v in saldo_final_vals):
            fig.add_trace(go.Scatter(
                x=años, y=saldo_final_vals, mode="lines+markers+text",
                name="Saldo Final", line=dict(color=ACCENT, width=3),
                marker=dict(size=10, color=ACCENT),
                text=[fmt_num(v) for v in saldo_final_vals],
                textposition="top center"))
        if any(v != 0 for v in saldo_ini_vals):
            fig.add_trace(go.Scatter(
                x=años, y=saldo_ini_vals, mode="lines+markers",
                name="Saldo Inicial", line=dict(color=TEXT_SEC, width=1.5, dash="dot"),
                marker=dict(size=6)))

        fig.add_hline(y=0, line_dash="solid", line_color=DANGER, opacity=0.3)
        fig.update_layout(xaxis_title="Período", yaxis_title="Miles $",
                          **plot_base("Saldo de Caja — Evolución"))
        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — CASCADA POR AÑO
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 💧 Cascada de flujo de caja por año")

        año_cas = st.selectbox("Año", años, key="fi_año_cas")
        idx_cas = años.index(año_cas)

        fco_v = fco_vals[idx_cas]
        fci_v = fci_vals[idx_cas]
        fcf_v = fcf_vals[idx_cas]
        neto_v = neto_vals[idx_cas]

        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["FCO\nOperativo", "FCI\nInversión", "FCF\nFinanciamiento", "FLUJO\nNETO"],
            y=[fco_v, fci_v, fcf_v, 0],
            text=[fmt_num(v) for v in [fco_v, fci_v, fcf_v, neto_v]],
            textposition="outside",
            connector={"line": {"color": BORDER, "width": 1}},
            increasing={"marker": {"color": SUCCESS}},
            decreasing={"marker": {"color": DANGER}},
            totals={"marker": {"color": ACCENT}},
        ))
        fig.update_layout(showlegend=False,
                          **plot_base(f"Cascada de Flujos — {año_cas}"))
        st.plotly_chart(fig, use_container_width=True)

        # Barras apiladas comparativas todos los años
        st.markdown("#### Comparativo todos los períodos")
        fig2 = go.Figure()
        fig2.add_bar(x=años, y=fco_vals, name="FCO Operativo",
                     marker_color=SUCCESS)
        fig2.add_bar(x=años, y=fci_vals, name="FCI Inversión",
                     marker_color=DANGER)
        fig2.add_bar(x=años, y=fcf_vals, name="FCF Financiamiento",
                     marker_color=PURPLE)
        fig2.add_trace(go.Scatter(
            x=años, y=neto_vals, mode="lines+markers",
            name="Flujo Neto", line=dict(color=ACCENT, width=2.5),
            marker=dict(size=8)))
        fig2.update_layout(barmode="group", xaxis_title="Período",
                           yaxis_title="Miles $",
                           **plot_base("FCO / FCI / FCF por período"))
        st.plotly_chart(fig2, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — TENDENCIAS
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📈 Análisis de tendencias")

        # Crecimiento YoY del FCO
        if len(fco_vals) >= 2:
            crec_fco = [(fco_vals[i] - fco_vals[i-1]) / abs(fco_vals[i-1]) * 100
                        if fco_vals[i-1] != 0 else 0
                        for i in range(1, len(fco_vals))]
            años_crec = años[1:]

            fig = go.Figure()
            fig.add_bar(x=años_crec, y=crec_fco,
                        marker_color=[SUCCESS if v >= 0 else DANGER for v in crec_fco],
                        name="Crecimiento FCO")
            fig.add_hline(y=0, line_dash="solid", line_color=TEXT_SEC, opacity=0.4)
            fig.update_layout(xaxis_title="Período", yaxis_title="%",
                              **plot_base("Crecimiento YoY del Flujo Operativo (FCO)"))
            st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)

        # FCO vs Saldo final
        with c1:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=años, y=fco_vals, mode="lines+markers",
                                      name="FCO", line=dict(color=SUCCESS, width=2)))
            fig2.add_trace(go.Scatter(x=años, y=saldo_final_vals if any(saldo_final_vals) else neto_vals,
                                      mode="lines+markers", name="Saldo Final",
                                      line=dict(color=ACCENT, width=2, dash="dot")))
            fig2.update_layout(xaxis_title="Período", yaxis_title="Miles $",
                               **plot_base("FCO vs Saldo Final"))
            st.plotly_chart(fig2, use_container_width=True)

        # Cobertura inversión con operación
        with c2:
            cobertura = [f / abs(i) if i != 0 else 0 for f, i in zip(fco_vals, fci_vals)]
            fig3 = go.Figure()
            fig3.add_bar(x=años, y=cobertura,
                         marker_color=[SUCCESS if v >= 1 else WARN if v >= 0.5 else DANGER
                                       for v in cobertura],
                         name="Ratio cobertura")
            fig3.add_hline(y=1, line_dash="dash", line_color=SUCCESS, opacity=0.6,
                           annotation_text="FCO cubre FCI",
                           annotation_font_color=SUCCESS)
            fig3.update_layout(xaxis_title="Período", yaxis_title="Ratio",
                               **plot_base("FCO / |FCI| — Cobertura de Inversión"))
            st.plotly_chart(fig3, use_container_width=True)

        # Top conceptos del FCO
        st.markdown("#### Composición del Flujo Operativo")
        items_op = df_data[
            (df_data["seccion"].str.upper().str.contains("OPERACI", na=False)) &
            (df_data["tipo"] == "item")
        ].copy()
        if len(items_op) and len(años):
            año_ref = años[-1]
            items_op["valor_ref"] = items_op[año_ref].apply(
                lambda v: abs(float(v)) if pd.notna(v) else 0)
            items_op = items_op.nlargest(8, "valor_ref")
            fig4 = px.bar(items_op, x=año_ref, y="concepto", orientation="h",
                          color=año_ref,
                          color_continuous_scale=["#1a3a5c", "#00C2FF"],
                          template="plotly_dark",
                          title=f"Top conceptos operativos — {año_ref}")
            fig4.update_layout(**plot_base())
            st.plotly_chart(fig4, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — PROYECCIÓN
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🔮 Proyección de períodos futuros")

        col_n, col_esc = st.columns(2)
        n_proy = col_n.slider("Períodos a proyectar", 1, 5, 3, key="fi_n_proy")

        escenarios = {
            "Optimista":  {"fco": 1.15, "fci": 0.95, "fcf": 1.0},
            "Base":       {"fco": 1.00, "fci": 1.00, "fcf": 1.0},
            "Pesimista":  {"fco": 0.85, "fci": 1.10, "fcf": 1.0},
        }

        # Detectar patrón de nombres de años
        base_num = None
        for a in años:
            if "AÑO" in a.upper():
                try:
                    base_num = int(''.join(filter(str.isdigit, a)))
                except Exception:
                    pass
            elif a.isdigit():
                base_num = int(a)

        if base_num and "AÑO" in años[0].upper():
            años_fut = [f"Año {base_num + i}" for i in range(1, n_proy + 1)]
        elif base_num and años[0].isdigit():
            años_fut = [str(base_num + i) for i in range(1, n_proy + 1)]
        else:
            años_fut = [f"Proy. {i+1}" for i in range(n_proy)]

        colores_esc = {"Optimista": SUCCESS, "Base": WARN, "Pesimista": DANGER}
        dash_esc = {"Optimista": "dot", "Base": "dash", "Pesimista": "dashdot"}

        fig = go.Figure()
        # Histórico saldo
        hist_saldo = saldo_final_vals if any(saldo_final_vals) else (
            [sum(neto_vals[:i+1]) for i in range(len(neto_vals))])
        fig.add_trace(go.Scatter(x=años, y=hist_saldo, mode="lines+markers",
                                 name="Histórico", line=dict(color=ACCENT, width=2.5),
                                 marker=dict(size=8)))

        for nombre, factores in escenarios.items():
            fco_p = proyectar(fco_vals, n_proy, factores["fco"])
            fci_p = proyectar(fci_vals, n_proy, factores["fci"])
            fcf_p = proyectar(fcf_vals, n_proy, factores["fcf"])
            neto_p = [f + i + c for f, i, c in zip(fco_p, fci_p, fcf_p)]

            saldo_base = hist_saldo[-1] if hist_saldo else 0
            saldo_p = []
            s = saldo_base
            for n in neto_p:
                s += n
                saldo_p.append(s)

            fig.add_trace(go.Scatter(
                x=años_fut, y=saldo_p, mode="lines+markers",
                name=nombre, line=dict(color=colores_esc[nombre], width=2,
                                       dash=dash_esc[nombre]),
                marker=dict(size=7)))

        if años_fut:
            fig.add_vrect(x0=años_fut[0], x1=años_fut[-1],
                          fillcolor="rgba(123,47,190,0.07)", layer="below",
                          line_width=0, annotation_text="Zona proyectada",
                          annotation_font_color=PURPLE,
                          annotation_position="top left")

        fig.add_hline(y=0, line_dash="solid", line_color=DANGER, opacity=0.35,
                      annotation_text="Quiebre",
                      annotation_font_color=DANGER)

        fig.update_layout(xaxis_title="Período", yaxis_title="Saldo (Miles $)",
                          **plot_base(f"Proyección de saldo — {n_proy} períodos adicionales"))
        st.plotly_chart(fig, use_container_width=True)

        # Tabla resumen proyección
        st.markdown("#### Resumen de proyección")
        rows_proy = []
        for nombre, factores in escenarios.items():
            fco_p = proyectar(fco_vals, n_proy, factores["fco"])
            fci_p = proyectar(fci_vals, n_proy, factores["fci"])
            fcf_p = proyectar(fcf_vals, n_proy, factores["fcf"])
            neto_p = [f + i + c for f, i, c in zip(fco_p, fci_p, fcf_p)]
            rows_proy.append({
                "Escenario": nombre,
                **{f"FCO {a}": fmt_num(v) for a, v in zip(años_fut, fco_p)},
                **{f"Flujo Neto {a}": fmt_num(v) for a, v in zip(años_fut, neto_p)},
            })
        st.dataframe(pd.DataFrame(rows_proy), use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — ALERTAS
    # ════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### ⚠️ Alertas y diagnóstico financiero")

        alertas = []
        color_map = {"danger": DANGER, "warning": WARN,
                     "info": ACCENT, "success": SUCCESS}

        # 1. FCO negativo en algún año
        años_fco_neg = [a for a, v in zip(años, fco_vals) if v < 0]
        if años_fco_neg:
            alertas.append(("danger", "🚨",
                f"FCO negativo en: {', '.join(años_fco_neg)}",
                "El negocio no genera caja suficiente de su operación. Revisa márgenes y capital de trabajo."))
        else:
            alertas.append(("success", "✅",
                "FCO positivo en todos los períodos",
                f"El negocio genera caja operativa sana. Mejor año: {años[fco_vals.index(max(fco_vals))]} ({fmt_num(max(fco_vals))})."))

        # 2. Cobertura de inversión
        for a, fco_v, fci_v in zip(años, fco_vals, fci_vals):
            if fci_v < 0 and fco_v > 0:
                ratio = fco_v / abs(fci_v)
                if ratio < 0.8:
                    alertas.append(("warning", "⚠️",
                        f"{a}: FCO cubre solo el {ratio:.0%} del CAPEX",
                        f"Inversión de {fmt_num(abs(fci_v))} vs FCO de {fmt_num(fco_v)}. Considera financiamiento adicional."))
                    break

        # 3. Tendencia FCO
        if len(fco_vals) >= 3:
            tend = np.polyfit(range(len(fco_vals)), fco_vals, 1)[0]
            if tend > 0:
                alertas.append(("success", "📈",
                    f"FCO con tendencia creciente (+{fmt_num(tend)}/período)",
                    "Tu flujo operativo mejora consistentemente. Buen indicador de sostenibilidad."))
            else:
                alertas.append(("warning", "📉",
                    f"FCO con tendencia decreciente ({fmt_num(tend)}/período)",
                    "El flujo operativo se está deteriorando. Revisa estructura de costos e ingresos."))

        # 4. Dependencia de financiamiento
        for a, fco_v, fcf_v in zip(años, fco_vals, fcf_vals):
            if fcf_v > 0 and fco_v < fcf_v * 0.5:
                alertas.append(("warning", "🏦",
                    f"{a}: Alta dependencia de financiamiento externo",
                    f"FCF ({fmt_num(fcf_v)}) supera en más del 50% al FCO ({fmt_num(fco_v)}). "
                    f"Riesgo si se corta el crédito."))
                break

        # 5. Saldo final creciente
        if len(saldo_final_vals) >= 2 and all(v > 0 for v in saldo_final_vals):
            crec = (saldo_final_vals[-1] - saldo_final_vals[0]) / abs(saldo_final_vals[0]) * 100
            alertas.append(("info", "💰",
                f"Saldo de caja crece {crec:.0f}% entre {años[0]} y {años[-1]}",
                f"De {fmt_num(saldo_final_vals[0])} a {fmt_num(saldo_final_vals[-1])}."))

        for tipo, icono, titulo, detalle in alertas:
            color = color_map[tipo]
            st.markdown(f"""
            <div style="background:{BG_CARD};border-left:4px solid {color};
                        border-radius:8px;padding:1rem 1.2rem;margin-bottom:.8rem;">
                <p style="color:{color};font-weight:600;margin:0 0 .3rem;">{icono} {titulo}</p>
                <p style="color:{TEXT_SEC};font-size:.87rem;margin:0;">{detalle}</p>
            </div>""", unsafe_allow_html=True)

        # KPIs financieros clave
        st.divider()
        st.markdown("#### 🩺 Indicadores clave de salud financiera")

        último_año = años[-1]
        idx_ult = len(años) - 1
        fco_u = fco_vals[idx_ult]
        fci_u = fci_vals[idx_ult]
        fcf_u = fcf_vals[idx_ult]
        fcl = fco_u + fci_u  # Free Cash Flow = FCO + FCI

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card_html(
            f"Free Cash Flow ({último_año})",
            fmt_num(fcl),
            SUCCESS if fcl >= 0 else DANGER,
            "FCO + FCI"), unsafe_allow_html=True)
        c2.markdown(card_html(
            "Cobertura FCO/FCI",
            f"{fco_u/abs(fci_u):.1f}x" if fci_u != 0 else "N/A",
            SUCCESS if fci_u != 0 and fco_u/abs(fci_u) >= 1 else WARN,
            "≥ 1x es saludable"), unsafe_allow_html=True)
        c3.markdown(card_html(
            "Crecimiento FCO",
            f"{(fco_vals[-1]-fco_vals[0])/abs(fco_vals[0])*100:.0f}%" if fco_vals[0] != 0 else "N/A",
            SUCCESS,
            f"{años[0]} → {años[-1]}"), unsafe_allow_html=True)
        c4.markdown(card_html(
            f"Saldo Final ({último_año})",
            fmt_num(saldo_final_vals[-1]) if saldo_final_vals[-1] != 0 else fmt_num(sum(neto_vals)),
            SUCCESS if (saldo_final_vals[-1] or sum(neto_vals)) >= 0 else DANGER,
            "posición de caja"), unsafe_allow_html=True)
