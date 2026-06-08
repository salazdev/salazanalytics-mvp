"""
_flujo_caja.py  —  SalazAnalytics
Micro-activo: Flujo de Caja Inteligente
Proyección 30/60/90 días · 3 escenarios · Simulador de decisiones · Alertas de quiebre
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Paleta (consistente con el resto de la app) ──────────────────────────────
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


# ── Utilidades ───────────────────────────────────────────────────────────────
def fmt_cop(v):
    try:
        return f"${v:,.0f}"
    except Exception:
        return str(v)


def card_html(titulo, valor, color=ACCENT, subtitulo=""):
    sub = (f"<p style='color:{TEXT_SEC};font-size:.74rem;margin:.2rem 0 0;'>"
           f"{subtitulo}</p>") if subtitulo else ""
    return f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;
                padding:1rem 1.2rem;text-align:center;height:120px;
                display:flex;flex-direction:column;justify-content:center;">
        <p style="color:{TEXT_SEC};font-size:.76rem;margin:0 0 .25rem;">{titulo}</p>
        <p style="color:{color};font-weight:700;font-size:1.45rem;margin:0;">{valor}</p>
        {sub}
    </div>"""


def alerta_html(icono, titulo, detalle, color):
    return f"""
    <div style="background:{BG_CARD};border-left:4px solid {color};border-radius:8px;
                padding:1rem 1.2rem;margin-bottom:.8rem;">
        <p style="color:{color};font-weight:600;margin:0 0 .3rem;">{icono} {titulo}</p>
        <p style="color:{TEXT_SEC};font-size:.87rem;margin:0;">{detalle}</p>
    </div>"""


def plot_base():
    return dict(paper_bgcolor=BG_DARK, plot_bgcolor=BG_DARK,
                font_color="#E8F4FD", legend=dict(bgcolor=BG_CARD))


# ── Detección automática de columnas ────────────────────────────────────────
def detectar_cols(df):
    cols_lower = {c.lower(): c for c in df.columns}

    def match(keys):
        for k in keys:
            for cl, co in cols_lower.items():
                if k in cl:
                    return co
        return None

    return {
        "fecha":    match(["fecha", "date", "día", "dia", "periodo", "mes", "month"]),
        "monto":    match(["monto", "valor", "total", "importe", "amount", "value",
                           "suma", "ingreso", "egreso", "flujo", "saldo"]),
        "tipo":     match(["tipo", "type", "categoria", "category", "clase",
                           "movimiento", "naturaleza"]),
        "concepto": match(["concepto", "descripcion", "descripción", "detalle",
                           "nombre", "item", "cuenta", "glosa"]),
    }


def clasificar_tipo(df, col_tipo, col_monto):
    df = df.copy()
    if col_tipo:
        t = df[col_tipo].astype(str).str.lower()
        df["_tipo"] = "Desconocido"
        df.loc[t.str.contains("ingreso|entrada|venta|cobro|income|revenue|credit|haber",
                               na=False), "_tipo"] = "Ingreso"
        df.loc[t.str.contains("egreso|salida|gasto|pago|costo|expense|debit|compra|debe",
                               na=False), "_tipo"] = "Egreso"
        if col_monto:
            nd = df["_tipo"] == "Desconocido"
            df.loc[nd & (df[col_monto] >= 0), "_tipo"] = "Ingreso"
            df.loc[nd & (df[col_monto] <  0), "_tipo"] = "Egreso"
    elif col_monto:
        df["_tipo"] = np.where(df[col_monto] >= 0, "Ingreso", "Egreso")
    else:
        df["_tipo"] = "Ingreso"
    return df


# ── Proyección con tendencia + promedio móvil ────────────────────────────────
def proyectar_serie(valores, n=3, factor=1.0):
    if len(valores) == 0:
        return [0.0] * n
    if len(valores) == 1:
        return [valores[0] * factor] * n
    x = np.arange(len(valores))
    m, b = np.polyfit(x, valores, 1)
    x_fut = np.arange(len(valores), len(valores) + n)
    tend = m * x_fut + b
    reciente = np.mean(valores[-min(3, len(valores)):])
    proj = tend * 0.4 + reciente * 0.6
    return np.maximum(proj * factor, 0).tolist()


# ── Datos demo ───────────────────────────────────────────────────────────────
def generar_demo():
    rng = np.random.default_rng(42)
    hoy = datetime.today()
    rows = []
    ingresos_base = [18_000_000, 22_000_000, 19_500_000, 25_000_000, 21_000_000, 28_000_000]
    egresos_cfg = [
        ("Nómina",        0.42),
        ("Arriendo",      0.11),
        ("Proveedores",   0.24),
        ("Servicios públicos", 0.07),
        ("Marketing",     0.08),
        ("Varios",        0.08),
    ]
    for i in range(6):
        origen = hoy - timedelta(days=30 * (5 - i))
        base_ing = ingresos_base[i]
        base_egr = base_ing * rng.uniform(0.65, 0.78)
        # 4 cobros de ventas distribuidos en el mes
        for semana in range(4):
            fecha = origen + timedelta(weeks=semana, days=int(rng.integers(0, 5)))
            rows.append({
                "Fecha":    fecha,
                "Concepto": f"Ventas semana {semana+1}",
                "Tipo":     "Ingreso",
                "Monto":    base_ing / 4 * rng.uniform(0.85, 1.15),
            })
        # Egresos fijos y variables
        for concepto, pct in egresos_cfg:
            fecha = origen + timedelta(days=int(rng.integers(1, 27)))
            rows.append({
                "Fecha":    fecha,
                "Concepto": concepto,
                "Tipo":     "Egreso",
                "Monto":    base_egr * pct * rng.uniform(0.92, 1.08),
            })
    df = pd.DataFrame(rows)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df.sort_values("Fecha").reset_index(drop=True)


# ════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
def show():
    st.markdown("## 💰 Flujo de Caja Inteligente")
    st.markdown(
        f"<p style='color:{TEXT_SEC}'>Proyecta tu efectivo, detecta quiebres y simula "
        f"decisiones antes de tomarlas.</p>", unsafe_allow_html=True)

    # ── Saldo inicial ────────────────────────────────────────────────────────
    with st.expander("⚙️ Configuración inicial", expanded=False):
        saldo_inicial = st.number_input(
            "Saldo actual en caja / banco ($)", value=0, step=500_000,
            format="%d", key="fc_saldo_ini",
            help="Dinero disponible hoy, antes de los movimientos del archivo.")
    saldo_ini = float(st.session_state.get("fc_saldo_ini", 0))

    # ── Fuente de datos ──────────────────────────────────────────────────────
    fuente = st.radio(
        "Fuente de datos",
        ["📂 Cargar Excel", "✏️ Entrada manual", "📋 Datos demo"],
        horizontal=True, key="fc_fuente")

    df_fc = None  # DataFrame normalizado: [Fecha, Concepto, Tipo, Monto]

    # ── Opción 1: Excel ──────────────────────────────────────────────────────
    if fuente == "📂 Cargar Excel":
        uploaded = st.file_uploader(
            "Sube tu archivo de flujo de caja",
            type=["xlsx", "xls"], key="fc_upload")

        if uploaded:
            try:
                sheets = pd.read_excel(uploaded, sheet_name=None)
                sheet_name = st.selectbox("Hoja", list(sheets.keys()), key="fc_sheet")
                df_raw = sheets[sheet_name]

                st.markdown(f"<p style='color:{TEXT_SEC};font-size:.83rem;'>"
                            f"Vista previa ({len(df_raw):,} filas)</p>",
                            unsafe_allow_html=True)
                st.dataframe(df_raw.head(5), use_container_width=True)

                mapeados = detectar_cols(df_raw)
                with st.expander("⚙️ Verificar mapeo de columnas"):
                    c1, c2, c3, c4 = st.columns(4)
                    opts = [None] + list(df_raw.columns)

                    def idx(val):
                        return opts.index(val) if val in opts else 0

                    col_fecha    = c1.selectbox("Fecha",    opts, index=idx(mapeados["fecha"]),    key="fc_cf")
                    col_monto    = c2.selectbox("Monto",    opts, index=idx(mapeados["monto"]),    key="fc_cm")
                    col_tipo     = c3.selectbox("Tipo",     opts, index=idx(mapeados["tipo"]),     key="fc_ct")
                    col_concepto = c4.selectbox("Concepto", opts, index=idx(mapeados["concepto"]), key="fc_cc")

                if col_fecha and col_monto:
                    dw = df_raw.copy()
                    dw["Fecha"] = pd.to_datetime(dw[col_fecha], errors="coerce")
                    dw["Monto"] = (pd.to_numeric(
                        dw[col_monto].astype(str)
                          .str.replace(r"[\$,\s]", "", regex=True),
                        errors="coerce").fillna(0).abs())
                    dw["Concepto"] = dw[col_concepto].astype(str) if col_concepto else "Sin concepto"
                    dw = clasificar_tipo(dw, col_tipo, col_monto)
                    dw.rename(columns={"_tipo": "Tipo"}, inplace=True)
                    df_fc = (dw[["Fecha", "Concepto", "Tipo", "Monto"]]
                             .dropna(subset=["Fecha", "Monto"])
                             .sort_values("Fecha")
                             .reset_index(drop=True))
                    st.success(f"✅ **{len(df_fc):,} movimientos** cargados")
                else:
                    st.warning("Selecciona al menos las columnas **Fecha** y **Monto**.")
            except Exception as e:
                st.error(f"Error leyendo archivo: {e}")

    # ── Opción 2: Manual ─────────────────────────────────────────────────────
    elif fuente == "✏️ Entrada manual":
        if "fc_movs" not in st.session_state:
            st.session_state["fc_movs"] = []

        with st.form("fc_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            concepto = c1.text_input("Concepto", placeholder="Ej: Ventas semana 1")
            tipo     = c2.selectbox("Tipo", ["Ingreso", "Egreso"])
            monto    = c3.number_input("Monto ($)", min_value=0.0, step=100_000.0, format="%.0f")
            fecha    = c4.date_input("Fecha", value=datetime.today())
            ok = st.form_submit_button("➕ Agregar movimiento", type="primary", use_container_width=True)
            if ok and monto > 0 and concepto.strip():
                st.session_state["fc_movs"].append({
                    "Fecha": pd.Timestamp(fecha),
                    "Concepto": concepto.strip(),
                    "Tipo": tipo,
                    "Monto": float(monto),
                })
                st.rerun()

        movs = st.session_state.get("fc_movs", [])
        if movs:
            df_m = pd.DataFrame(movs)
            st.dataframe(
                df_m.style.format({"Monto": "${:,.0f}"}),
                use_container_width=True)
            col_x, col_dl = st.columns([1, 3])
            if col_x.button("🗑️ Limpiar", key="fc_clear"):
                st.session_state["fc_movs"] = []
                st.rerun()
            df_fc = df_m.sort_values("Fecha").reset_index(drop=True)
        else:
            st.info("Agrega movimientos arriba para comenzar.")

    # ── Opción 3: Demo ───────────────────────────────────────────────────────
    else:
        df_fc = generar_demo()
        st.info("📋 **Datos demo** — empresa de servicios, 6 meses de historial.")
        with st.expander("Ver datos demo"):
            st.dataframe(df_fc.style.format({"Monto": "${:,.0f}"}), use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # ANÁLISIS  (solo si hay datos)
    # ════════════════════════════════════════════════════════════════════════
    if df_fc is None or len(df_fc) == 0:
        return

    df_fc = df_fc.copy()
    df_fc["Mes"] = df_fc["Fecha"].dt.to_period("M").astype(str)
    df_fc["Flujo"] = df_fc.apply(
        lambda r: r["Monto"] if r["Tipo"] == "Ingreso" else -r["Monto"], axis=1)
    df_fc["Saldo_Acum"] = saldo_ini + df_fc["Flujo"].cumsum()

    ingresos_t = df_fc[df_fc["Tipo"] == "Ingreso"]["Monto"].sum()
    egresos_t  = df_fc[df_fc["Tipo"] == "Egreso"]["Monto"].sum()
    flujo_neto = ingresos_t - egresos_t
    saldo_final = df_fc["Saldo_Acum"].iloc[-1]
    n_meses     = df_fc["Mes"].nunique()
    ing_mens_prom = ingresos_t / max(n_meses, 1)
    egr_mens_prom = egresos_t  / max(n_meses, 1)
    margen = (flujo_neto / ingresos_t * 100) if ingresos_t > 0 else 0

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Diagnóstico",
        "🔮 Proyección 30/60/90",
        "🎯 Simulador de Decisiones",
        "⚠️ Alertas de Quiebre",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — DIAGNÓSTICO
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📊 Resumen del período")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card_html("Total Ingresos",  fmt_cop(ingresos_t),  SUCCESS),   unsafe_allow_html=True)
        c2.markdown(card_html("Total Egresos",   fmt_cop(egresos_t),   DANGER),    unsafe_allow_html=True)
        c3.markdown(card_html("Flujo Neto",      fmt_cop(flujo_neto),
                              ACCENT if flujo_neto >= 0 else DANGER),               unsafe_allow_html=True)
        c4.markdown(card_html("Margen Neto",     f"{margen:.1f}%",
                              SUCCESS if margen >= 20 else WARN if margen >= 10 else DANGER,
                              "saludable ≥ 20%"),                                   unsafe_allow_html=True)

        st.divider()
        c1, c2 = st.columns(2)

        # Ingresos vs Egresos por mes
        with c1:
            meses_u   = sorted(df_fc["Mes"].unique())
            ing_m_ser = df_fc[df_fc["Tipo"] == "Ingreso"].groupby("Mes")["Monto"].sum()
            egr_m_ser = df_fc[df_fc["Tipo"] == "Egreso"].groupby("Mes")["Monto"].sum()
            df_mens = pd.DataFrame({
                "Mes":      meses_u,
                "Ingresos": [ing_m_ser.get(m, 0) for m in meses_u],
                "Egresos":  [egr_m_ser.get(m, 0) for m in meses_u],
            })
            fig = go.Figure()
            fig.add_bar(x=df_mens["Mes"], y=df_mens["Ingresos"],
                        name="Ingresos", marker_color=SUCCESS)
            fig.add_bar(x=df_mens["Mes"], y=df_mens["Egresos"],
                        name="Egresos",  marker_color=DANGER)
            fig.update_layout(barmode="group", title="Ingresos vs Egresos por Mes",
                              xaxis_title="Mes", yaxis_title="$", **plot_base())
            st.plotly_chart(fig, use_container_width=True)

        # Saldo acumulado
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_fc["Fecha"], y=df_fc["Saldo_Acum"],
                mode="lines", name="Saldo acumulado",
                line=dict(color=ACCENT, width=2),
                fill="tozeroy", fillcolor="rgba(0,194,255,0.10)"))
            fig2.add_hline(y=0, line_dash="dash", line_color=DANGER, opacity=0.6,
                           annotation_text="Cero", annotation_font_color=DANGER)
            fig2.update_layout(title="Saldo Acumulado", xaxis_title="Fecha",
                               yaxis_title="$", **plot_base())
            st.plotly_chart(fig2, use_container_width=True)

        # Composición de egresos
        top_egr = (df_fc[df_fc["Tipo"] == "Egreso"]
                   .groupby("Concepto")["Monto"].sum()
                   .sort_values(ascending=False).head(8))
        if len(top_egr):
            c1, c2 = st.columns(2)
            with c1:
                fig3 = px.pie(values=top_egr.values, names=top_egr.index,
                              color_discrete_sequence=PALETTE, template="plotly_dark",
                              title="¿En qué gastas más?")
                fig3.update_layout(**plot_base())
                st.plotly_chart(fig3, use_container_width=True)
            with c2:
                # Flujo neto mensual
                neto_m = df_fc.groupby("Mes")["Flujo"].sum().reset_index()
                neto_m.columns = ["Mes", "Neto"]
                neto_m["Color"] = neto_m["Neto"].apply(
                    lambda v: SUCCESS if v >= 0 else DANGER)
                fig4 = go.Figure(go.Bar(
                    x=neto_m["Mes"], y=neto_m["Neto"],
                    marker_color=neto_m["Color"].tolist(),
                    name="Flujo neto"))
                fig4.add_hline(y=0, line_dash="solid", line_color=TEXT_SEC, opacity=0.4)
                fig4.update_layout(title="Flujo Neto Mensual", xaxis_title="Mes",
                                   yaxis_title="$", **plot_base())
                st.plotly_chart(fig4, use_container_width=True)

        # Tabla de detalle
        with st.expander("📋 Ver todos los movimientos"):
            st.dataframe(
                df_fc[["Fecha", "Concepto", "Tipo", "Monto", "Saldo_Acum"]]
                .style.format({"Monto": "${:,.0f}", "Saldo_Acum": "${:,.0f}"})
                .applymap(lambda v: f"color:{SUCCESS}" if v == "Ingreso"
                          else (f"color:{DANGER}" if v == "Egreso" else ""),
                          subset=["Tipo"]),
                use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — PROYECCIÓN
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🔮 Proyección de flujo de caja")
        st.markdown(f"<p style='color:{TEXT_SEC}'>Basada en la tendencia histórica de tus datos.</p>",
                    unsafe_allow_html=True)

        col_h, col_o, col_p = st.columns(3)
        horizonte = col_h.select_slider(
            "Horizonte (días)", options=[30, 60, 90], value=60, key="fc_hor")
        factor_opt = col_o.slider("Optimista: ingresos +%", 5, 40, 15, key="fc_opt") / 100
        factor_pes = col_p.slider("Pesimista: ingresos -%",  5, 40, 15, key="fc_pes") / 100

        n_meses_pred = horizonte // 30

        # Series históricas mensuales
        ing_hist = [df_fc[df_fc["Tipo"] == "Ingreso"].groupby("Mes")["Monto"]
                    .sum().get(m, 0) for m in sorted(df_fc["Mes"].unique())]
        egr_hist = [df_fc[df_fc["Tipo"] == "Egreso"].groupby("Mes")["Monto"]
                    .sum().get(m, 0) for m in sorted(df_fc["Mes"].unique())]

        # Fechas futuras
        ultima = df_fc["Fecha"].max()
        meses_fut = [(ultima + timedelta(days=30 * (i + 1))).strftime("%Y-%m")
                     for i in range(n_meses_pred)]

        # Calcular escenarios
        configs = {
            "Optimista":  (1 + factor_opt, 0.95),
            "Base":       (1.00,            1.00),
            "Pesimista":  (1 - factor_pes,  1.10),
        }
        colores_esc = {"Optimista": SUCCESS, "Base": WARN, "Pesimista": DANGER}
        dash_esc    = {"Optimista": "dot",   "Base": "dash", "Pesimista": "dashdot"}

        escenarios = {}
        for nombre, (fi, fe) in configs.items():
            ing_p = proyectar_serie(ing_hist, n_meses_pred, fi)
            egr_p = proyectar_serie(egr_hist, n_meses_pred, fe)
            neto_p = [i - e for i, e in zip(ing_p, egr_p)]
            saldo_p = []
            s = saldo_final
            for n in neto_p:
                s += n
                saldo_p.append(s)
            escenarios[nombre] = {"ing": ing_p, "egr": egr_p, "neto": neto_p, "saldo": saldo_p}

        # Gráfico
        fig = go.Figure()

        # Histórico (saldo acumulado mensual)
        hist_mens = df_fc.groupby("Mes")["Flujo"].sum().cumsum() + saldo_ini
        fig.add_trace(go.Scatter(
            x=list(hist_mens.index), y=hist_mens.values,
            mode="lines", name="Histórico",
            line=dict(color=ACCENT, width=2.5)))

        for nombre, datos in escenarios.items():
            fig.add_trace(go.Scatter(
                x=meses_fut, y=datos["saldo"],
                mode="lines+markers", name=nombre,
                line=dict(color=colores_esc[nombre], width=2, dash=dash_esc[nombre]),
                marker=dict(size=7)))

        if meses_fut:
            fig.add_vrect(
                x0=meses_fut[0], x1=meses_fut[-1],
                fillcolor="rgba(123,47,190,0.07)", layer="below", line_width=0,
                annotation_text="Zona proyectada",
                annotation_font_color=PURPLE,
                annotation_position="top left")

        fig.add_hline(y=0, line_dash="solid", line_color=DANGER, opacity=0.45,
                      annotation_text="Quiebre de caja",
                      annotation_font_color=DANGER,
                      annotation_position="bottom right")

        fig.update_layout(
            title=f"Saldo proyectado — próximos {horizonte} días",
            xaxis_title="Mes", yaxis_title="Saldo ($)",
            **plot_base())
        st.plotly_chart(fig, use_container_width=True)

        # Tabla resumen
        st.markdown("#### Resumen por escenario")
        filas = []
        for nombre, datos in escenarios.items():
            quiebre = next(
                (meses_fut[i] for i, s in enumerate(datos["saldo"]) if s < 0),
                "✅ No detectado")
            filas.append({
                "Escenario":        nombre,
                "Ingresos proy.":   fmt_cop(sum(datos["ing"])),
                "Egresos proy.":    fmt_cop(sum(datos["egr"])),
                "Flujo neto proy.": fmt_cop(sum(datos["neto"])),
                "Saldo final":      fmt_cop(datos["saldo"][-1]) if datos["saldo"] else "$0",
                "Quiebre de caja":  quiebre,
            })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

        # Barras de ingresos/egresos proyectados por mes
        if meses_fut:
            st.markdown("#### Ingresos vs Egresos proyectados (escenario Base)")
            df_proy = pd.DataFrame({
                "Mes":      meses_fut,
                "Ingresos": escenarios["Base"]["ing"],
                "Egresos":  escenarios["Base"]["egr"],
            })
            fig2 = go.Figure()
            fig2.add_bar(x=df_proy["Mes"], y=df_proy["Ingresos"],
                         name="Ingresos", marker_color=SUCCESS)
            fig2.add_bar(x=df_proy["Mes"], y=df_proy["Egresos"],
                         name="Egresos",  marker_color=DANGER)
            fig2.update_layout(barmode="group", title="Proyección Base mensual",
                               xaxis_title="Mes", yaxis_title="$", **plot_base())
            st.plotly_chart(fig2, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — SIMULADOR DE DECISIONES
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🎯 Simulador: ¿Qué pasa si…?")
        st.markdown(
            f"<p style='color:{TEXT_SEC}'>Ajusta los parámetros y mira el impacto "
            f"en tu flujo <em>antes</em> de decidir.</p>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<p style='color:{SUCCESS};font-weight:600;'>📈 Ingresos</p>",
                        unsafe_allow_html=True)
            delta_ventas  = st.slider("Cambio en ventas (%)", -60, 100, 0, key="sim_dv")
            nueva_linea   = st.number_input(
                "Nueva línea de ingresos ($/mes)", 0, value=0,
                step=500_000, format="%d", key="sim_nl")

        with c2:
            st.markdown(f"<p style='color:{DANGER};font-weight:600;'>📉 Egresos</p>",
                        unsafe_allow_html=True)
            nuevos_emp    = st.slider("Empleados nuevos (+/-)", -10, 20, 0, key="sim_ne")
            costo_emp     = st.number_input(
                "Costo por empleado ($/mes)", 0, value=2_000_000,
                step=100_000, format="%d", key="sim_ce")
            nuevo_fijo    = st.number_input(
                "Nuevo costo fijo mensual ($)", 0, value=0,
                step=200_000, format="%d", key="sim_nf")
            reduccion_egr = st.slider("Reducción de otros gastos (%)", 0, 50, 0, key="sim_re")

        # Cálculo de impacto
        ing_sim = (ing_mens_prom * (1 + delta_ventas / 100)) + nueva_linea
        egr_sim = (egr_mens_prom * (1 - reduccion_egr / 100)
                   + nuevos_emp * costo_emp + nuevo_fijo)
        neto_act = ing_mens_prom - egr_mens_prom
        neto_sim = ing_sim - egr_sim
        delta_n  = neto_sim - neto_act

        st.divider()
        st.markdown("#### Impacto mensual estimado")
        c1, c2, c3, c4 = st.columns(4)

        def pct_cambio(nuevo, viejo):
            if viejo == 0:
                return ""
            pct = (nuevo - viejo) / abs(viejo) * 100
            return f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}%"

        c1.markdown(card_html("Ingresos actuales",  fmt_cop(ing_mens_prom), TEXT_SEC,  "promedio mensual"), unsafe_allow_html=True)
        c2.markdown(card_html("Ingresos simulados", fmt_cop(ing_sim),
                              SUCCESS if ing_sim >= ing_mens_prom else DANGER,
                              pct_cambio(ing_sim, ing_mens_prom)), unsafe_allow_html=True)
        c3.markdown(card_html("Egresos simulados",  fmt_cop(egr_sim),
                              DANGER if egr_sim > egr_mens_prom else SUCCESS,
                              pct_cambio(egr_sim, egr_mens_prom)), unsafe_allow_html=True)
        c4.markdown(card_html("Flujo neto simulado", fmt_cop(neto_sim),
                              ACCENT if neto_sim >= 0 else DANGER,
                              f"{'▲' if delta_n >= 0 else '▼'} {fmt_cop(abs(delta_n))} vs actual"),
                    unsafe_allow_html=True)

        # Waterfall
        labels = [
            "Base ingresos",
            f"Ventas ({delta_ventas:+}%)",
            "Nueva línea",
            f"Empleados ({nuevos_emp:+})",
            "Nuevo fijo",
            f"Reducción gastos ({reduccion_egr}%)",
            "FLUJO NETO",
        ]
        valores = [
            ing_mens_prom,
            ing_mens_prom * (delta_ventas / 100),
            float(nueva_linea),
            -(nuevos_emp * costo_emp),
            -float(nuevo_fijo),
            egr_mens_prom * (reduccion_egr / 100),
            0,
        ]
        medidas = ["absolute", "relative", "relative",
                   "relative", "relative", "relative", "total"]

        fig = go.Figure(go.Waterfall(
            orientation="v", measure=medidas, x=labels, y=valores,
            connector={"line": {"color": BORDER}},
            increasing={"marker": {"color": SUCCESS}},
            decreasing={"marker": {"color": DANGER}},
            totals={"marker": {"color": ACCENT}},
        ))
        fig.update_layout(title="Cascada de impacto de la decisión",
                          showlegend=False, **plot_base())
        st.plotly_chart(fig, use_container_width=True)

        # Proyección con decisión aplicada (12 meses)
        meses_sim = 12
        meses_fut_sim = [(df_fc["Fecha"].max() + timedelta(days=30 * (i + 1))).strftime("%Y-%m")
                         for i in range(meses_sim)]
        saldo_sim_arr, saldo_base_arr = [], []
        s_sim = s_base = saldo_final
        for _ in range(meses_sim):
            s_base += neto_act
            s_sim  += neto_sim
            saldo_base_arr.append(s_base)
            saldo_sim_arr.append(s_sim)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=meses_fut_sim, y=saldo_base_arr,
            mode="lines", name="Sin cambios",
            line=dict(color=TEXT_SEC, width=2, dash="dot")))
        fig2.add_trace(go.Scatter(
            x=meses_fut_sim, y=saldo_sim_arr,
            mode="lines+markers", name="Con la decisión",
            line=dict(color=ACCENT if neto_sim >= 0 else DANGER, width=2.5),
            marker=dict(size=6)))
        fig2.add_hline(y=0, line_dash="solid", line_color=DANGER, opacity=0.45,
                       annotation_text="Quiebre", annotation_font_color=DANGER)
        fig2.update_layout(title="Saldo proyectado a 12 meses (base vs decisión)",
                           xaxis_title="Mes", yaxis_title="$", **plot_base())
        st.plotly_chart(fig2, use_container_width=True)

        # Veredicto
        if neto_sim > neto_act * 1.1:
            cv, iv, msg = SUCCESS, "✅", f"La decisión **mejora** tu flujo neto mensual en {fmt_cop(abs(delta_n))}. Adelante."
        elif neto_sim >= 0:
            cv, iv, msg = WARN, "⚠️", f"Flujo neto positivo de {fmt_cop(neto_sim)}/mes, pero el margen es ajustado. Monitorea de cerca."
        else:
            cv, iv, msg = DANGER, "🚨", f"Esta decisión genera un flujo neto **negativo** de {fmt_cop(neto_sim)}/mes. Revisa antes de proceder."

        st.markdown(f"""
        <div style="background:{BG_CARD};border-left:4px solid {cv};border-radius:10px;
                    padding:1.2rem;margin-top:.5rem;">
            <p style="color:{cv};font-weight:700;font-size:1.05rem;margin:0;">{iv} Veredicto del simulador</p>
            <p style="color:#E8F4FD;font-size:.93rem;margin:.4rem 0 0;">{msg}</p>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — ALERTAS DE QUIEBRE
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚠️ Alertas críticas de caja")

        alertas = []
        color_map = {"danger": DANGER, "warning": WARN, "info": ACCENT, "success": SUCCESS}

        # 1. Saldo final negativo
        if saldo_final < 0:
            alertas.append(("danger", "🚨",
                f"Saldo acumulado negativo: {fmt_cop(saldo_final)}",
                "Tu caja acumulada está en números rojos. Acción inmediata requerida."))

        # 2. Meses con flujo neto negativo
        neto_m = df_fc.groupby("Mes")["Flujo"].sum()
        meses_neg = neto_m[neto_m < 0]
        if len(meses_neg):
            alertas.append(("danger", "📉",
                f"{len(meses_neg)} mes(es) con flujo neto negativo",
                f"Meses en déficit: {', '.join(meses_neg.index.tolist())}. "
                f"Déficit total: {fmt_cop(meses_neg.sum())}"))

        # 3. Ratio egresos/ingresos
        ratio = egresos_t / ingresos_t if ingresos_t > 0 else 0
        if ratio > 0.85:
            alertas.append(("danger" if ratio > 0.95 else "warning", "📊",
                f"Ratio egresos/ingresos: {ratio:.0%}",
                f"De cada $100 que entran, gastas ${ratio*100:.0f}. "
                f"{'Nivel crítico.' if ratio > 0.95 else 'Umbral saludable < 80%.'}"))

        # 4. Concentración de ingresos
        ing_conc = (df_fc[df_fc["Tipo"] == "Ingreso"]
                    .groupby("Concepto")["Monto"].sum())
        if len(ing_conc) and ing_conc.max() / ing_conc.sum() > 0.60:
            pct = ing_conc.max() / ing_conc.sum()
            alertas.append(("warning", "⚠️",
                f"Alta concentración: {pct:.0%} de ingresos en una sola fuente",
                f"'{ing_conc.idxmax()}' domina tus ingresos. Diversifica para reducir riesgo."))

        # 5. Tendencia de flujo neto
        if n_meses >= 3:
            tend = np.polyfit(range(len(neto_m)), neto_m.values, 1)[0]
            if tend < -ing_mens_prom * 0.03:
                alertas.append(("warning", "📉",
                    "Tendencia de flujo neto a la baja",
                    f"Tu flujo neto disminuye aprox. {fmt_cop(abs(tend))}/mes. "
                    f"Revisa estructura de costos."))

        # 6. Reserva mínima
        reserva_min = ing_mens_prom * 1.5
        if saldo_final < reserva_min and saldo_final >= 0:
            alertas.append(("info", "💡",
                f"Reserva de caja por debajo del mínimo recomendado",
                f"Tienes {fmt_cop(saldo_final)} disponible. Se recomienda mantener al menos "
                f"{fmt_cop(reserva_min)} (1.5 meses de ingresos)."))

        if not alertas:
            alertas.append(("success", "✅",
                "¡Salud financiera OK!",
                "No se detectaron alertas críticas en el período analizado."))

        for tipo, icono, titulo, detalle in alertas:
            st.markdown(
                alerta_html(icono, titulo, detalle, color_map[tipo]),
                unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📈 Saldo acumulado con zonas de riesgo")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_fc["Fecha"], y=df_fc["Saldo_Acum"],
            mode="lines+markers", name="Saldo",
            line=dict(color=ACCENT, width=2),
            marker=dict(size=4,
                        color=[DANGER if s < 0 else SUCCESS for s in df_fc["Saldo_Acum"]])))

        s_min = df_fc["Saldo_Acum"].min()
        s_max = df_fc["Saldo_Acum"].max()

        # Zona roja
        fig.add_hrect(
            y0=min(s_min * 1.15, -1), y1=0,
            fillcolor="rgba(255,107,107,0.10)", layer="below", line_width=0,
            annotation_text="Zona de riesgo", annotation_font_color=DANGER,
            annotation_position="bottom right")

        # Zona verde (reserva saludable)
        reserva = ing_mens_prom * 1.5
        if s_max > reserva:
            fig.add_hrect(
                y0=reserva, y1=s_max * 1.05,
                fillcolor="rgba(0,255,179,0.06)", layer="below", line_width=0,
                annotation_text="Zona saludable", annotation_font_color=SUCCESS,
                annotation_position="top right")

        fig.add_hline(y=0, line_dash="solid", line_color=DANGER, opacity=0.35)
        fig.add_hline(y=reserva, line_dash="dash", line_color=SUCCESS, opacity=0.4,
                      annotation_text=f"Reserva mínima ({fmt_cop(reserva)})",
                      annotation_font_color=SUCCESS,
                      annotation_position="top left")

        fig.update_layout(
            title="Saldo acumulado con zonas de alerta",
            xaxis_title="Fecha", yaxis_title="Saldo ($)",
            **plot_base())
        st.plotly_chart(fig, use_container_width=True)

        # KPIs de salud
        st.markdown("#### 🩺 Indicadores de salud financiera")
        dias_reserva = (saldo_final / (egr_mens_prom / 30)) if egr_mens_prom > 0 else 0
        burn_rate = egr_mens_prom
        runway = saldo_final / burn_rate if burn_rate > 0 else float("inf")

        c1, c2, c3 = st.columns(3)
        c1.markdown(card_html(
            "Días de reserva",
            f"{max(dias_reserva, 0):.0f} días",
            SUCCESS if dias_reserva >= 45 else WARN if dias_reserva >= 15 else DANGER,
            "recomendado ≥ 45 días"), unsafe_allow_html=True)
        c2.markdown(card_html(
            "Burn Rate mensual",
            fmt_cop(burn_rate),
            WARN, "egreso mensual promedio"), unsafe_allow_html=True)
        c3.markdown(card_html(
            "Runway",
            f"{runway:.1f} meses" if runway != float("inf") else "∞",
            SUCCESS if runway >= 3 else WARN if runway >= 1 else DANGER,
            "meses que aguanta la caja"), unsafe_allow_html=True)
