import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
import io
import json

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

CATEGORIAS_INGRESO = [
    "Ventas de productos",
    "Prestación de servicios",
    "Honorarios",
    "Arrendamientos",
    "Intereses y rendimientos",
    "Otros ingresos",
]

CATEGORIAS_GASTO = [
    "Nómina y salarios",
    "Arriendo",
    "Servicios públicos",
    "Internet y telecomunicaciones",
    "Publicidad y marketing",
    "Contabilidad y revisoría",
    "Software y suscripciones",
    "Transporte y logística",
    "Compra de mercancía",
    "Equipos y herramientas",
    "Gastos bancarios",
    "Impuestos y tasas",
    "Capacitación",
    "Otros gastos",
]

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Tarifa SIMPLE 2024 — servicios profesionales (grupo 3)
TARIFAS_SIMPLE = {
    "0-6.000":    2.0,
    "6.000-15.000": 2.8,
    "15.000-30.000": 5.5,
    "30.000-80.000": 7.0,
    ">80.000":    8.5,
}

# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────

def _init():
    if "movimientos" not in st.session_state:
        st.session_state["movimientos"] = []  # lista de dicts

def _movimientos() -> list:
    return st.session_state.get("movimientos", [])

def _df() -> pd.DataFrame:
    mvs = _movimientos()
    if not mvs:
        return pd.DataFrame(columns=["fecha","tipo","categoria","descripcion","valor","iva","valor_iva","total"])
    df = pd.DataFrame(mvs)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha", ascending=False).reset_index(drop=True)
    return df

# ─────────────────────────────────────────────
# EXPORTAR EXCEL
# ─────────────────────────────────────────────

def _exportar_excel() -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    COLOR_DARK  = "0D1B2A"
    COLOR_CYAN  = "00C2FF"
    COLOR_GREEN = "00A86B"
    COLOR_RED   = "E53935"
    COLOR_GRAY  = "7B9BB5"
    COLOR_LIGHT = "E8F4FD"

    wb = Workbook()

    # ── Hoja 1: Movimientos ──
    ws1 = wb.active
    ws1.title = "Movimientos"

    headers = ["Fecha", "Tipo", "Categoría", "Descripción", "Valor Base", "IVA %", "Valor IVA", "Total"]
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=h)
        cell.font = Font(bold=True, color=COLOR_CYAN, name="Arial", size=10)
        cell.fill = PatternFill("solid", start_color=COLOR_DARK)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    df = _df()
    for row_idx, row in df.iterrows():
        r = row_idx + 2
        ws1.cell(r, 1, str(row["fecha"])[:10])
        ws1.cell(r, 2, row["tipo"])
        ws1.cell(r, 3, row["categoria"])
        ws1.cell(r, 4, row["descripcion"])
        ws1.cell(r, 5, row["valor"])
        ws1.cell(r, 6, row["iva"])
        ws1.cell(r, 7, row["valor_iva"])
        ws1.cell(r, 8, row["total"])

        # color fila por tipo
        fill_color = "E8F5E9" if row["tipo"] == "Ingreso" else "FFEBEE"
        for col in range(1, 9):
            cell = ws1.cell(r, col)
            cell.fill = PatternFill("solid", start_color=fill_color)
            cell.font = Font(name="Arial", size=9)
            if col in [5, 7, 8]:
                cell.number_format = '$#,##0'

    # anchos
    for col, w in zip(range(1, 9), [12, 10, 22, 35, 14, 8, 12, 14]):
        ws1.column_dimensions[get_column_letter(col)].width = w

    # ── Hoja 2: Resumen mensual ──
    ws2 = wb.create_sheet("Resumen Mensual")
    df2 = _df().copy()
    if not df2.empty:
        df2["mes"] = df2["fecha"].dt.month
        df2["año"] = df2["fecha"].dt.year

        headers2 = ["Mes", "Ingresos", "Gastos", "Utilidad", "IVA Cobrado", "IVA Pagado", "IVA Neto"]
        for col, h in enumerate(headers2, 1):
            cell = ws2.cell(1, col, h)
            cell.font = Font(bold=True, color=COLOR_CYAN, name="Arial", size=10)
            cell.fill = PatternFill("solid", start_color=COLOR_DARK)
            cell.alignment = Alignment(horizontal="center")

        grupos = df2.groupby(["año", "mes"])
        r = 2
        for (año, mes), g in sorted(grupos):
            ingresos  = g[g["tipo"]=="Ingreso"]["total"].sum()
            gastos    = g[g["tipo"]=="Gasto"]["total"].sum()
            iva_cobrado = g[g["tipo"]=="Ingreso"]["valor_iva"].sum()
            iva_pagado  = g[g["tipo"]=="Gasto"]["valor_iva"].sum()

            ws2.cell(r, 1, f"{MESES[mes-1]} {año}")
            ws2.cell(r, 2, ingresos)
            ws2.cell(r, 3, gastos)
            ws2.cell(r, 4, f"=B{r}-C{r}")
            ws2.cell(r, 5, iva_cobrado)
            ws2.cell(r, 6, iva_pagado)
            ws2.cell(r, 7, f"=E{r}-F{r}")

            for col in range(2, 8):
                ws2.cell(r, col).number_format = '$#,##0'
            r += 1

        # Totales
        last = r - 1
        ws2.cell(r, 1, "TOTAL").font = Font(bold=True, name="Arial")
        for col in range(2, 8):
            ws2.cell(r, col, f"=SUM({get_column_letter(col)}2:{get_column_letter(col)}{last})")
            ws2.cell(r, col).number_format = '$#,##0'
            ws2.cell(r, col).font = Font(bold=True, name="Arial")

        for col in range(1, 8):
            ws2.column_dimensions[get_column_letter(col)].width = 18

    # ── Hoja 3: IVA SIMPLE ──
    ws3 = wb.create_sheet("IVA y SIMPLE")
    ws3["A1"] = "Liquidación IVA y SIMPLE"
    ws3["A1"].font = Font(bold=True, color=COLOR_CYAN, name="Arial", size=12)

    if not df2.empty:
        total_ingresos  = df2[df2["tipo"]=="Ingreso"]["total"].sum()
        total_gastos    = df2[df2["tipo"]=="Gasto"]["total"].sum()
        iva_cobrado     = df2[df2["tipo"]=="Ingreso"]["valor_iva"].sum()
        iva_pagado      = df2[df2["tipo"]=="Gasto"]["valor_iva"].sum()
        iva_neto        = iva_cobrado - iva_pagado
        ingresos_base   = df2[df2["tipo"]=="Ingreso"]["valor"].sum()

        # Estimar SIMPLE (tarifa 2.0% base para simplificar — el usuario ajusta)
        simple_estimado = ingresos_base * 0.02

        datos = [
            ("", ""),
            ("INGRESOS TOTALES", total_ingresos),
            ("GASTOS TOTALES", total_gastos),
            ("UTILIDAD BRUTA", total_ingresos - total_gastos),
            ("", ""),
            ("IVA COBRADO (ventas)", iva_cobrado),
            ("IVA PAGADO (compras)", iva_pagado),
            ("IVA A PAGAR / FAVOR", iva_neto),
            ("", ""),
            ("BASE INGRESOS SIMPLE", ingresos_base),
            ("TARIFA SIMPLE aprox. 2%", simple_estimado),
            ("* Verifique tarifa con su contador", ""),
        ]
        for i, (label, valor) in enumerate(datos, 3):
            ws3[f"A{i}"] = label
            if valor != "":
                ws3[f"B{i}"] = valor
                ws3[f"B{i}"].number_format = '$#,##0'
            if label and not label.startswith("*"):
                ws3[f"A{i}"].font = Font(name="Arial", size=10)
                ws3[f"B{i}"].font = Font(name="Arial", size=10, bold=True)

        ws3.column_dimensions["A"].width = 30
        ws3.column_dimensions["B"].width = 18

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# ─────────────────────────────────────────────
# AGENTE IA — registra movimiento desde texto
# ─────────────────────────────────────────────

def _agente_registrar(texto: str) -> dict:
    import anthropic, re

    system = """Eres el asistente contable de SalazAnalytics para empresas colombianas en Régimen Simple.
Extrae del texto un movimiento contable y devuelve SOLO JSON válido sin markdown:

{
  "tipo": "Ingreso" o "Gasto",
  "categoria": string (una de las categorías colombianas típicas),
  "descripcion": string corto,
  "valor": número entero en pesos colombianos (sin IVA),
  "iva": 0 o 5 o 19,
  "mensaje": "confirmación amigable en español"
}

Si el valor mencionado incluye IVA, descuéntalo para obtener la base.
Si no se menciona IVA, usa 0."""

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": texto}]
    )
    raw = re.sub(r"```json|```", "", resp.content[0].text).strip()
    return json.loads(raw)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def show():
    _init()

    st.markdown("## 📒 Contabilidad")
    st.markdown(
        "<p style='color:#7B9BB5'>Ingresos, gastos, IVA y estimado SIMPLE — "
        "todo en un solo lugar.</p>",
        unsafe_allow_html=True
    )

    tab_agente, tab_manual, tab_dashboard, tab_iva = st.tabs([
        "🤖 Registrar con IA", "✏️ Registro Manual", "📊 Dashboard", "🧾 IVA y SIMPLE"
    ])

    # ══════════════════════════════════════════
    # TAB AGENTE IA
    # ══════════════════════════════════════════
    with tab_agente:
        st.markdown("### Registra un movimiento en lenguaje natural")
        st.markdown(
            "<p style='color:#7B9BB5'>Cuéntale al agente qué pasó y él lo clasifica.</p>",
            unsafe_allow_html=True
        )

        with st.expander("💡 Ejemplos"):
            st.markdown("""
- *"Pagué arriendo de oficina $1.200.000"*
- *"Cobré honorarios a cliente ABC por $3.500.000 más IVA"*
- *"Compré papelería $85.000 sin IVA"*
- *"Recibí pago de servicio de contabilidad $800.000 con IVA del 19%"*
- *"Nómina de mayo $2.800.000"*
            """)

        texto = st.text_area(
            "Describe el movimiento:",
            placeholder="Ej: Pagué el internet de mayo $120.000...",
            height=100,
            key="agente_contab_texto"
        )

        if st.button("🤖 Registrar con IA", type="primary", key="btn_agente_contab"):
            if not texto.strip():
                st.warning("Escribe el movimiento primero.")
            else:
                with st.spinner("Clasificando movimiento..."):
                    try:
                        r = _agente_registrar(texto)
                        valor_iva = round(r["valor"] * r["iva"] / 100)
                        total = r["valor"] + valor_iva
                        mov = {
                            "fecha":       str(date.today()),
                            "tipo":        r["tipo"],
                            "categoria":   r["categoria"],
                            "descripcion": r["descripcion"],
                            "valor":       r["valor"],
                            "iva":         r["iva"],
                            "valor_iva":   valor_iva,
                            "total":       total,
                        }
                        st.session_state["movimientos"].append(mov)
                        tipo_color = "🟢" if r["tipo"] == "Ingreso" else "🔴"
                        st.success(
                            f"{tipo_color} {r['mensaje']}  \n"
                            f"**{r['tipo']}** · {r['categoria']} · "
                            f"Base: ${r['valor']:,.0f} · IVA: ${valor_iva:,.0f} · "
                            f"Total: ${total:,.0f}"
                        )
                    except Exception as e:
                        st.error(f"Error del agente: {e}")

    # ══════════════════════════════════════════
    # TAB REGISTRO MANUAL
    # ══════════════════════════════════════════
    with tab_manual:
        st.markdown("### Nuevo movimiento")

        c1, c2 = st.columns(2)
        with c1:
            tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True, key="m_tipo")
        with c2:
            fecha_mov = st.date_input("Fecha", value=date.today(), key="m_fecha_mov")

        categorias = CATEGORIAS_INGRESO if tipo == "Ingreso" else CATEGORIAS_GASTO
        categoria = st.selectbox("Categoría", categorias, key="m_categoria")
        descripcion = st.text_input("Descripción", key="m_descripcion",
                                    placeholder="Ej: Honorarios cliente XYZ")

        c1, c2, c3 = st.columns(3)
        with c1:
            valor = st.number_input("Valor base (sin IVA)", min_value=0, step=1000,
                                    key="m_valor", value=0)
        with c2:
            iva_pct = st.selectbox("IVA %", [0, 5, 19], key="m_iva")
        with c3:
            valor_iva = valor * iva_pct / 100
            total_mov = valor + valor_iva
            st.metric("Total con IVA", f"${total_mov:,.0f}")

        if st.button("➕ Guardar movimiento", type="primary", key="btn_guardar_mov"):
            if not descripcion:
                st.warning("Agrega una descripción.")
            elif valor <= 0:
                st.warning("El valor debe ser mayor a 0.")
            else:
                st.session_state["movimientos"].append({
                    "fecha":       str(fecha_mov),
                    "tipo":        tipo,
                    "categoria":   categoria,
                    "descripcion": descripcion,
                    "valor":       valor,
                    "iva":         iva_pct,
                    "valor_iva":   round(valor_iva),
                    "total":       round(total_mov),
                })
                st.success(f"✅ Movimiento guardado — ${total_mov:,.0f}")

        # ── Tabla de movimientos ──
        df = _df()
        if not df.empty:
            st.divider()
            st.markdown("### Movimientos registrados")

            # Filtros
            c1, c2, c3 = st.columns(3)
            with c1:
                filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos","Ingreso","Gasto"],
                                           key="filtro_tipo")
            with c2:
                meses_disponibles = sorted(df["fecha"].dt.month.unique())
                filtro_mes = st.selectbox(
                    "Mes",
                    ["Todos"] + [MESES[m-1] for m in meses_disponibles],
                    key="filtro_mes"
                )
            with c3:
                filtro_cat = st.selectbox(
                    "Categoría",
                    ["Todas"] + sorted(df["categoria"].unique().tolist()),
                    key="filtro_cat"
                )

            df_f = df.copy()
            if filtro_tipo != "Todos":
                df_f = df_f[df_f["tipo"] == filtro_tipo]
            if filtro_mes != "Todos":
                mes_num = MESES.index(filtro_mes) + 1
                df_f = df_f[df_f["fecha"].dt.month == mes_num]
            if filtro_cat != "Todas":
                df_f = df_f[df_f["categoria"] == filtro_cat]

            # Mostrar con colores
            df_show = df_f[["fecha","tipo","categoria","descripcion","valor","iva","valor_iva","total"]].copy()
            df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")

            def _color_fila(row):
                color = "#1a3a1a" if row["tipo"] == "Ingreso" else "#3a1a1a"
                return [f"background-color: {color}"] * len(row)

            styled = df_show.style.apply(_color_fila, axis=1)
            df_show.columns = ["Fecha","Tipo","Categoría","Descripción","Base","IVA%","Valor IVA","Total"]

            st.dataframe(
                styled,
                use_container_width=True,
                height=350
            )

            # Botón eliminar último
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button("🗑️ Eliminar último", key="btn_del_ultimo"):
                    if st.session_state["movimientos"]:
                        st.session_state["movimientos"].pop()
                        st.rerun()
            with c2:
                if st.button("📥 Exportar a Excel", key="btn_exportar", type="primary"):
                    xlsx = _exportar_excel()
                    b64 = base64.b64encode(xlsx).decode()
                    mes_actual = MESES[date.today().month - 1]
                    href = (
                        f'<a href="data:application/vnd.openxmlformats-officedocument.'
                        f'spreadsheetml.sheet;base64,{b64}" '
                        f'download="contabilidad_{mes_actual}_{date.today().year}.xlsx" '
                        f'style="display:inline-block;background:#00C2FF;color:#0D1B2A;'
                        f'font-weight:700;padding:.6rem 1.2rem;border-radius:8px;'
                        f'text-decoration:none;">⬇️ Descargar Excel</a>'
                    )
                    st.markdown(href, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # TAB DASHBOARD
    # ══════════════════════════════════════════
    with tab_dashboard:
        df = _df()
        if df.empty:
            st.info("Registra movimientos para ver el dashboard.")
        else:
            import plotly.express as px
            import plotly.graph_objects as go

            total_ingresos = df[df["tipo"]=="Ingreso"]["total"].sum()
            total_gastos   = df[df["tipo"]=="Gasto"]["total"].sum()
            utilidad       = total_ingresos - total_gastos
            margen         = (utilidad / total_ingresos * 100) if total_ingresos > 0 else 0

            # Métricas principales
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Ingresos", f"${total_ingresos:,.0f}")
            c2.metric("💸 Gastos",   f"${total_gastos:,.0f}")
            color_util = "normal" if utilidad >= 0 else "inverse"
            c3.metric("📈 Utilidad", f"${utilidad:,.0f}", delta=f"{margen:.1f}% margen")
            c4.metric("📝 Movimientos", len(df))

            st.divider()

            # Gráfico mensual
            df2 = df.copy()
            df2["mes_num"] = df2["fecha"].dt.month
            df2["mes"]     = df2["fecha"].dt.month.apply(lambda m: MESES[m-1])
            df2["año"]     = df2["fecha"].dt.year

            resumen = df2.groupby(["año","mes_num","mes","tipo"])["total"].sum().reset_index()
            resumen = resumen.sort_values("mes_num")

            if not resumen.empty:
                fig = px.bar(
                    resumen, x="mes", y="total", color="tipo", barmode="group",
                    color_discrete_map={"Ingreso":"#00C2FF","Gasto":"#7B2FBE"},
                    title="Ingresos vs Gastos por mes",
                    labels={"total":"Valor ($)","mes":"Mes","tipo":"Tipo"},
                    template="plotly_dark"
                )
                fig.update_layout(
                    plot_bgcolor="#0D1B2A",
                    paper_bgcolor="#0D1B2A",
                    font_color="#E8F4FD",
                    title_font_color="#00C2FF"
                )
                st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)

            # Donut gastos por categoría
            with c1:
                gastos_cat = df[df["tipo"]=="Gasto"].groupby("categoria")["total"].sum().reset_index()
                if not gastos_cat.empty:
                    fig2 = px.pie(
                        gastos_cat, values="total", names="categoria",
                        title="Distribución de gastos",
                        hole=0.5,
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig2.update_layout(
                        plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                        font_color="#E8F4FD", title_font_color="#00C2FF"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            # Top ingresos por categoría
            with c2:
                ing_cat = df[df["tipo"]=="Ingreso"].groupby("categoria")["total"].sum().reset_index()
                ing_cat = ing_cat.sort_values("total", ascending=True)
                if not ing_cat.empty:
                    fig3 = px.bar(
                        ing_cat, x="total", y="categoria", orientation="h",
                        title="Ingresos por categoría",
                        template="plotly_dark",
                        color_discrete_sequence=["#00C2FF"]
                    )
                    fig3.update_layout(
                        plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                        font_color="#E8F4FD", title_font_color="#00C2FF"
                    )
                    st.plotly_chart(fig3, use_container_width=True)

    # ══════════════════════════════════════════
    # TAB IVA Y SIMPLE
    # ══════════════════════════════════════════
    with tab_iva:
        df = _df()
        if df.empty:
            st.info("Registra movimientos para ver la liquidación.")
        else:
            st.markdown("### 🧾 Liquidación IVA")

            # Filtro período
            años = sorted(df["fecha"].dt.year.unique(), reverse=True)
            c1, c2 = st.columns(2)
            with c1:
                año_sel = st.selectbox("Año", años, key="iva_año")
            with c2:
                periodo = st.selectbox(
                    "Período IVA",
                    ["Bimestre 1 (Ene-Feb)", "Bimestre 2 (Mar-Abr)",
                     "Bimestre 3 (May-Jun)", "Bimestre 4 (Jul-Ago)",
                     "Bimestre 5 (Sep-Oct)", "Bimestre 6 (Nov-Dic)",
                     "Cuatrimestre 1 (Ene-Abr)", "Cuatrimestre 2 (May-Ago)",
                     "Cuatrimestre 3 (Sep-Dic)", "Año completo"],
                    key="iva_periodo"
                )

            # Mapear período a meses
            mapa_periodos = {
                "Bimestre 1 (Ene-Feb)": [1,2],
                "Bimestre 2 (Mar-Abr)": [3,4],
                "Bimestre 3 (May-Jun)": [5,6],
                "Bimestre 4 (Jul-Ago)": [7,8],
                "Bimestre 5 (Sep-Oct)": [9,10],
                "Bimestre 6 (Nov-Dic)": [11,12],
                "Cuatrimestre 1 (Ene-Abr)": [1,2,3,4],
                "Cuatrimestre 2 (May-Ago)": [5,6,7,8],
                "Cuatrimestre 3 (Sep-Dic)": [9,10,11,12],
                "Año completo": list(range(1,13)),
            }
            meses_sel = mapa_periodos[periodo]

            df_p = df[
                (df["fecha"].dt.year == año_sel) &
                (df["fecha"].dt.month.isin(meses_sel))
            ]

            if df_p.empty:
                st.warning("No hay movimientos en ese período.")
            else:
                iva_cobrado = df_p[df_p["tipo"]=="Ingreso"]["valor_iva"].sum()
                iva_pagado  = df_p[df_p["tipo"]=="Gasto"]["valor_iva"].sum()
                iva_neto    = iva_cobrado - iva_pagado

                c1, c2, c3 = st.columns(3)
                c1.metric("IVA Cobrado (ventas)", f"${iva_cobrado:,.0f}")
                c2.metric("IVA Descontable (compras)", f"${iva_pagado:,.0f}")
                color = "inverse" if iva_neto > 0 else "normal"
                c3.metric(
                    "IVA a Pagar" if iva_neto > 0 else "Saldo a Favor",
                    f"${abs(iva_neto):,.0f}",
                )

                st.divider()
                st.markdown("### 📊 Estimado SIMPLE")
                st.markdown(
                    "<p style='color:#7B9BB5;font-size:.85rem'>"
                    "Estimación orientativa — confirma con tu contador.</p>",
                    unsafe_allow_html=True
                )

                ingresos_base = df_p[df_p["tipo"]=="Ingreso"]["valor"].sum()
                ingresos_uvt  = ingresos_base / 47_065  # UVT 2024

                # Determinar tarifa
                if ingresos_uvt <= 6000:
                    tarifa = 2.0
                    rango = "0 - 6.000 UVT"
                elif ingresos_uvt <= 15000:
                    tarifa = 2.8
                    rango = "6.000 - 15.000 UVT"
                elif ingresos_uvt <= 30000:
                    tarifa = 5.5
                    rango = "15.000 - 30.000 UVT"
                elif ingresos_uvt <= 80000:
                    tarifa = 7.0
                    rango = "30.000 - 80.000 UVT"
                else:
                    tarifa = 8.5
                    rango = "> 80.000 UVT"

                simple_estimado = ingresos_base * tarifa / 100

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Ingresos base período", f"${ingresos_base:,.0f}")
                c2.metric("Ingresos en UVT", f"{ingresos_uvt:,.1f}")
                c3.metric(f"Tarifa SIMPLE ({rango})", f"{tarifa}%")
                c4.metric("SIMPLE Estimado", f"${simple_estimado:,.0f}")

                st.info(
                    f"💡 Con ingresos de ${ingresos_base:,.0f} en este período, "
                    f"tu tarifa SIMPLE aplicable es del **{tarifa}%** "
                    f"(rango {rango}). SIMPLE estimado: **${simple_estimado:,.0f}**. "
                    f"Recuerda que SIMPLE ya incluye IVA, Renta, ICA y otras contribuciones."
                )

                # Exportar
                st.divider()
                if st.button("📥 Exportar informe completo Excel", type="primary", key="btn_exp_iva"):
                    xlsx = _exportar_excel()
                    b64 = base64.b64encode(xlsx).decode()
                    href = (
                        f'<a href="data:application/vnd.openxmlformats-officedocument.'
                        f'spreadsheetml.sheet;base64,{b64}" '
                        f'download="contabilidad_completa_{año_sel}.xlsx" '
                        f'style="display:inline-block;background:#00C2FF;color:#0D1B2A;'
                        f'font-weight:700;padding:.6rem 1.2rem;border-radius:8px;'
                        f'text-decoration:none;">⬇️ Descargar Excel Completo</a>'
                    )
                    st.markdown(href, unsafe_allow_html=True)
