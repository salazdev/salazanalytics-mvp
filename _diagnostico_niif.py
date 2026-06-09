"""
_diagnostico_niif.py — SalazAnalytics
Micro-activo: Diagnóstico NIIF Pymes
Clasificación Grupo 2 / Grupo 3 · Checklist · Semáforo · Reporte
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

# ── Paleta ────────────────────────────────────────────────────────────────────
BG_DARK  = "#0D1B2A"; BG_CARD = "#132030"; BORDER = "#1a3a5c"
TEXT_SEC = "#7B9BB5"; ACCENT  = "#00C2FF"; DANGER = "#FF6B6B"
SUCCESS  = "#00FFB3"; WARN    = "#FFD93D"; PURPLE = "#7B2FBE"

SMMLV_2026 = 1_750_905

# ── Checklist Grupo 2 (NIIF para Pymes) ──────────────────────────────────────
CHECKLIST_G2 = {
    "📋 Políticas Contables": [
        ("POL1", "Manual de políticas contables adoptado y aprobado por la dirección", "Alta"),
        ("POL2", "Políticas comunicadas al equipo contable y financiero", "Media"),
        ("POL3", "Fecha de transición a NIIF documentada", "Alta"),
        ("POL4", "Políticas revisadas en los últimos 2 años", "Media"),
    ],
    "🏭 Propiedades, Planta y Equipo — Sec. 17": [
        ("PPE1", "Vidas útiles revisadas y documentadas por clase de activo", "Alta"),
        ("PPE2", "Método de depreciación definido (línea recta, unidades producción...)", "Alta"),
        ("PPE3", "Valor residual estimado para cada clase", "Media"),
        ("PPE4", "Evaluación de deterioro realizada anualmente", "Alta"),
        ("PPE5", "Componentización de activos significativos aplicada", "Media"),
        ("PPE6", "Propiedades de inversión identificadas y separadas", "Baja"),
    ],
    "📦 Inventarios — Sec. 13": [
        ("INV1", "Método de costeo definido: FIFO o Promedio Ponderado", "Alta"),
        ("INV2", "Valor Neto Realizable evaluado al cierre", "Alta"),
        ("INV3", "Obsolescencia identificada y provisionada", "Media"),
        ("INV4", "Conteos físicos periódicos con actas de inventario", "Media"),
    ],
    "💳 Instrumentos Financieros — Sec. 11/12": [
        ("IF1", "Política de deterioro de cartera definida y documentada", "Alta"),
        ("IF2", "Modelo de pérdidas crediticias esperadas aplicado (ECL)", "Alta"),
        ("IF3", "Activos financieros clasificados correctamente", "Media"),
        ("IF4", "Pasivos financieros medidos a costo amortizado", "Media"),
        ("IF5", "Inversiones de capital clasificadas y medidas", "Baja"),
    ],
    "💰 Ingresos — Sec. 23": [
        ("ING1", "Política de reconocimiento de ingresos documentada", "Alta"),
        ("ING2", "Momento de reconocimiento definido (transferencia de riesgos/control)", "Alta"),
        ("ING3", "Ingresos diferidos identificados y contabilizados", "Media"),
        ("ING4", "Descuentos, devoluciones y rebajas registrados correctamente", "Media"),
    ],
    "🏢 Arrendamientos — Sec. 20": [
        ("ARR1", "Contratos de arrendamiento clasificados (operativo vs. financiero)", "Media"),
        ("ARR2", "Activos por derecho de uso reconocidos si aplica", "Media"),
        ("ARR3", "Pagos mínimos futuros calculados y revelados", "Baja"),
    ],
    "👥 Beneficios a Empleados — Sec. 28": [
        ("BEN1", "Cesantías, vacaciones e intereses provisionados correctamente", "Alta"),
        ("BEN2", "Obligaciones post-empleo (pensiones) identificadas", "Media"),
        ("BEN3", "Cálculo actuarial realizado si supera umbrales", "Media"),
        ("BEN4", "Bonificaciones y comisiones causadas al corte", "Alta"),
    ],
    "🧾 Impuestos — Sec. 29": [
        ("IMP1", "Impuesto diferido calculado (activo y pasivo)", "Alta"),
        ("IMP2", "Diferencias temporarias entre base fiscal y contable identificadas", "Alta"),
        ("IMP3", "Conciliación patrimonio fiscal vs. contable preparada", "Alta"),
        ("IMP4", "Recoverabilidad del activo por impuesto diferido evaluada", "Media"),
    ],
    "📊 Estados Financieros — Sec. 3-8": [
        ("EF1", "Estado de Situación Financiera (balance) bajo NIIF completo", "Alta"),
        ("EF2", "Estado de Resultados Integral preparado", "Alta"),
        ("EF3", "Estado de Cambios en Patrimonio preparado", "Alta"),
        ("EF4", "Estado de Flujos de Efectivo — método indirecto", "Alta"),
        ("EF5", "Presentados con período comparativo (año anterior)", "Alta"),
    ],
    "🔍 Revelaciones y Notas — Sec. 8": [
        ("REV1", "Notas a EE.FF. completas con todas las secciones requeridas", "Alta"),
        ("REV2", "Políticas contables significativas reveladas en notas", "Alta"),
        ("REV3", "Juicios, estimaciones e incertidumbres documentados", "Media"),
        ("REV4", "Partes relacionadas identificadas y transacciones reveladas", "Media"),
        ("REV5", "Compromisos, contingencias y hechos posteriores revelados", "Media"),
    ],
}

CHECKLIST_G3 = {
    "📋 Documentación Básica": [
        ("G3P1", "Libro fiscal actualizado y firmado", "Alta"),
        ("G3P2", "Políticas contables simplificadas documentadas", "Media"),
        ("G3P3", "Soportes de cada transacción archivados", "Alta"),
    ],
    "🏭 Activos": [
        ("G3A1", "Registro de activos fijos con valor de adquisición y depreciación acumulada", "Alta"),
        ("G3A2", "Inventario de existencias valorado al costo", "Alta"),
        ("G3A3", "Cuentas por cobrar identificadas y con soporte", "Alta"),
    ],
    "💼 Pasivos": [
        ("G3P4", "Cuentas por pagar a proveedores registradas al corte", "Alta"),
        ("G3P5", "Obligaciones financieras con saldo actualizado", "Alta"),
        ("G3P6", "Obligaciones laborales causadas (vacaciones, cesantías)", "Alta"),
    ],
    "💰 Ingresos y Gastos": [
        ("G3I1", "Ingresos registrados cuando se realiza la venta/servicio", "Alta"),
        ("G3I2", "Gastos causados en el período correspondiente", "Alta"),
        ("G3I3", "Costos de ventas calculados correctamente", "Alta"),
    ],
    "📊 Reportes Requeridos": [
        ("G3R1", "Balance de comprobación mensual preparado", "Alta"),
        ("G3R2", "Estado de resultados simplificado disponible", "Alta"),
        ("G3R3", "Declaraciones tributarias conciliadas con contabilidad", "Alta"),
    ],
}

OBLIGACIONES_TRIBUTARIAS = [
    ("RET", "Agente de Retención en la Fuente",
     "Patrimonio bruto > $4,786M o ingresos brutos > $1,532M en año anterior, o es SA/SAS/Ltda.",
     "Declaración mensual de retenciones"),
    ("IVA", "Responsable de IVA (Régimen Común)",
     "Ingresos brutos anuales > $119M (48 UVT × $2,483 aprox.) o tiene más de un local",
     "Declaración bimestral o cuatrimestral según ingresos"),
    ("ICA", "Impuesto de Industria y Comercio",
     "Realiza actividades industriales, comerciales o de servicios en el municipio",
     "Declaración bimestral o anual según municipio"),
    ("RENTA", "Declaración de Renta",
     "Persona jurídica: siempre. Persona natural: ingresos > 1,400 UVT (~$57M) o patrimonio > 4,500 UVT",
     "Declaración anual — vence según último dígito NIT"),
    ("SIMPLE", "Régimen SIMPLE de Tributación",
     "Opcional para personas naturales y jurídicas con ingresos < $3,486M (1,400 UVT × 6 aprox.)",
     "Anticipo bimestral + declaración anual"),
]

# ── Utilidades ────────────────────────────────────────────────────────────────
def card(titulo, valor, color=ACCENT, sub=""):
    s = f"<p style='color:{TEXT_SEC};font-size:.72rem;margin:.15rem 0 0'>{sub}</p>" if sub else ""
    return f"""<div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;
        padding:.8rem 1rem;text-align:center;">
        <p style="color:{TEXT_SEC};font-size:.73rem;margin:0 0 .2rem">{titulo}</p>
        <p style="color:{color};font-weight:700;font-size:1.3rem;margin:0">{valor}</p>{s}</div>"""

def badge(texto, color):
    return f"<span style='background:{color}22;color:{color};border:1px solid {color}55;border-radius:20px;padding:2px 10px;font-size:.78rem;font-weight:600'>{texto}</span>"

def semaforo_color(pct):
    if pct >= 75: return SUCCESS, "🟢 Bueno"
    if pct >= 50: return WARN,    "🟡 En proceso"
    return DANGER, "🔴 Requiere atención"

def get_checklist(grupo):
    return CHECKLIST_G2 if grupo == 2 else CHECKLIST_G3

# ── FUNCIÓN PRINCIPAL ─────────────────────────────────────────────────────────
def show():
    st.markdown("## 🏛️ Diagnóstico NIIF Pymes")
    st.markdown(f"<p style='color:{TEXT_SEC}'>Evalúa el nivel de cumplimiento de tu empresa con las Normas Internacionales de Información Financiera.</p>",
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Mi Empresa",
        "✅ Checklist NIIF",
        "🚦 Semáforo",
        "📌 Recomendaciones",
        "📄 Reporte",
    ])

    # ═══════════════════════════════════════════════════════════
    # TAB 1 — MI EMPRESA
    # ═══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🏢 Información de la empresa")
        st.markdown(f"<p style='color:{TEXT_SEC};font-size:.85rem'>Completa estos datos para clasificar tu empresa y determinar tus obligaciones.</p>",
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            nombre_emp = st.text_input("Nombre de la empresa", key="niif_nombre",
                                       placeholder="Ej: Comercializadora XYZ S.A.S.")
            tipo_persona = st.selectbox("Tipo de persona", ["Jurídica (Empresa)", "Natural (Comerciante)"], key="niif_tipo")
            sector = st.selectbox("Sector económico", [
                "Comercio", "Servicios", "Manufactura / Industrial",
                "Construcción", "Agropecuario", "Tecnología", "Salud", "Otro"
            ], key="niif_sector")
        with col2:
            empleados = st.number_input("Número de empleados", min_value=0, max_value=10000,
                                        value=15, step=1, key="niif_emp")
            activos_m = st.number_input("Activos totales (millones COP)", min_value=0.0,
                                        value=500.0, step=50.0, key="niif_activos",
                                        help="Suma de todos los activos del balance")
            ingresos_m = st.number_input("Ingresos brutos anuales (millones COP)", min_value=0.0,
                                         value=800.0, step=50.0, key="niif_ingresos",
                                         help="Ingresos brutos del último año fiscal")

        activos_smmlv  = (activos_m  * 1_000_000) / SMMLV_2026
        ingresos_smmlv = (ingresos_m * 1_000_000) / SMMLV_2026

        # Clasificación automática
        es_g3 = empleados <= 10 and activos_smmlv <= 500
        grupo = 3 if es_g3 else (1 if (activos_smmlv > 30000 or ingresos_smmlv > 30000) else 2)

        st.markdown("---")
        st.markdown("#### 📌 Clasificación automática")

        g_color = {1: DANGER, 2: ACCENT, 3: SUCCESS}[grupo]
        g_label = {
            1: "Grupo 1 — NIIF Plenas",
            2: "Grupo 2 — NIIF para Pymes",
            3: "Grupo 3 — Contabilidad Simplificada"
        }[grupo]
        g_desc = {
            1: "Aplican las NIIF completas (IASB). Requiere contador público con tarjeta profesional y revisoría fiscal.",
            2: "Aplica la NIIF para Pymes (IASB 2015 actualizada). Marco más completo con secciones específicas.",
            3: "Marco simplificado (Decreto 2420 Anexo 3). Contabilidad de base cash simplificada."
        }[grupo]

        st.markdown(f"""<div style="background:{BG_CARD};border-left:5px solid {g_color};
            border-radius:8px;padding:1rem 1.2rem;margin-bottom:1rem">
            <p style="color:{g_color};font-weight:700;font-size:1.1rem;margin:0 0 .3rem">{g_label}</p>
            <p style="color:{TEXT_SEC};font-size:.87rem;margin:0">{g_desc}</p>
            </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(card("Empleados", str(empleados), ACCENT), unsafe_allow_html=True)
        c2.markdown(card("Activos", f"{activos_smmlv:,.0f} SMMLV", g_color, f"${activos_m:,.0f}M COP"), unsafe_allow_html=True)
        c3.markdown(card("Ingresos", f"{ingresos_smmlv:,.0f} SMMLV", g_color, f"${ingresos_m:,.0f}M COP"), unsafe_allow_html=True)

        st.session_state["niif_grupo"] = grupo

        # Obligaciones tributarias
        st.markdown("---")
        st.markdown("#### 🧾 Obligaciones tributarias aplicables")
        st.markdown(f"<p style='color:{TEXT_SEC};font-size:.83rem'>Marca las que aplican a tu empresa para incluirlas en el reporte.</p>",
                    unsafe_allow_html=True)

        for codigo, nombre, criterio, periodicidad in OBLIGACIONES_TRIBUTARIAS:
            aplica = st.checkbox(
                f"**{nombre}**",
                key=f"trib_{codigo}",
                help=f"Criterio: {criterio}"
            )
            if aplica:
                st.markdown(f"<p style='color:{TEXT_SEC};font-size:.78rem;margin:-8px 0 4px 24px'>📅 {periodicidad}</p>",
                            unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 2 — CHECKLIST
    # ═══════════════════════════════════════════════════════════
    with tab2:
        grupo = st.session_state.get("niif_grupo", 2)
        checklist = get_checklist(grupo)
        g_label = f"Grupo {grupo} — {'NIIF para Pymes' if grupo == 2 else 'Contabilidad Simplificada'}"
        st.markdown(f"### ✅ Checklist {g_label}")
        st.markdown(f"<p style='color:{TEXT_SEC};font-size:.83rem'>Para cada punto indica el estado actual de tu empresa.</p>",
                    unsafe_allow_html=True)

        OPCIONES = ["✅ Cumple", "⚠️ En proceso", "❌ No cumple", "➖ No aplica"]
        COLORES  = {"✅ Cumple": SUCCESS, "⚠️ En proceso": WARN,
                    "❌ No cumple": DANGER, "➖ No aplica": TEXT_SEC}

        total_items = 0; total_cumple = 0; total_proceso = 0; total_no = 0

        for area, items in checklist.items():
            with st.expander(area, expanded=False):
                for codigo, descripcion, prioridad in items:
                    col_d, col_s = st.columns([3, 1])
                    p_color = DANGER if prioridad == "Alta" else (WARN if prioridad == "Media" else TEXT_SEC)
                    col_d.markdown(
                        f"<p style='margin:.2rem 0;font-size:.87rem'>{descripcion} "
                        f"<span style='color:{p_color};font-size:.72rem;font-weight:600'>[{prioridad}]</span></p>",
                        unsafe_allow_html=True)
                    val = col_s.selectbox("", OPCIONES, key=f"chk_{codigo}",
                                          label_visibility="collapsed")
                    if val != "➖ No aplica":
                        total_items += 1
                        if val == "✅ Cumple": total_cumple += 1
                        elif val == "⚠️ En proceso": total_proceso += 1
                        elif val == "❌ No cumple": total_no += 1

        st.session_state["niif_totales"] = (total_items, total_cumple, total_proceso, total_no)

        if total_items > 0:
            pct = total_cumple / total_items * 100
            color, label = semaforo_color(pct)
            st.markdown(f"""<div style="background:{BG_CARD};border:1px solid {BORDER};
                border-radius:8px;padding:.8rem 1.2rem;margin-top:1rem;text-align:center">
                <p style="color:{color};font-size:1.4rem;font-weight:700;margin:0">{pct:.0f}% de cumplimiento</p>
                <p style="color:{TEXT_SEC};font-size:.85rem;margin:.2rem 0 0">{label} · {total_cumple}/{total_items} ítems cumplidos</p>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 3 — SEMÁFORO
    # ═══════════════════════════════════════════════════════════
    with tab3:
        grupo = st.session_state.get("niif_grupo", 2)
        checklist = get_checklist(grupo)
        st.markdown("### 🚦 Semáforo de cumplimiento por área")

        areas_data = []
        for area, items in checklist.items():
            cumple = proceso = no = 0
            for codigo, _, _ in items:
                val = st.session_state.get(f"chk_{codigo}", "❌ No cumple")
                if val == "✅ Cumple": cumple += 1
                elif val == "⚠️ En proceso": proceso += 1
                elif val == "❌ No cumple": no += 1
            total = cumple + proceso + no
            pct = cumple / total * 100 if total > 0 else 0
            areas_data.append({"area": area, "cumple": cumple, "proceso": proceso,
                                "no": no, "total": total, "pct": pct})

        # Gráfico de barras horizontales
        areas_data.sort(key=lambda x: x["pct"])
        nombres = [a["area"].split("—")[0].strip() for a in areas_data]
        pcts    = [a["pct"] for a in areas_data]
        colores = [semaforo_color(p)[0] for p in pcts]

        fig = go.Figure(go.Bar(
            y=nombres, x=pcts, orientation="h",
            marker_color=colores,
            text=[f"{p:.0f}%" for p in pcts],
            textposition="outside",
        ))
        fig.add_vline(x=75, line_dash="dash", line_color=SUCCESS, opacity=0.5,
                      annotation_text="Meta 75%", annotation_font_color=SUCCESS)
        fig.add_vline(x=50, line_dash="dot", line_color=WARN, opacity=0.4)
        fig.update_layout(
            paper_bgcolor=BG_DARK, plot_bgcolor=BG_DARK,
            font_color="#E8F4FD", height=400,
            xaxis=dict(range=[0, 115], title="% Cumplimiento"),
            yaxis=dict(title=""),
            margin=dict(l=10, r=60, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Cards por área
        cols = st.columns(3)
        for i, a in enumerate(sorted(areas_data, key=lambda x: x["pct"], reverse=True)):
            color, label = semaforo_color(a["pct"])
            cols[i % 3].markdown(
                card(a["area"].split("—")[0].strip()[:28],
                     f"{a['pct']:.0f}%", color,
                     f"✅{a['cumple']} ⚠️{a['proceso']} ❌{a['no']}"),
                unsafe_allow_html=True)
            cols[i % 3].markdown("<div style='margin:.3rem'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 4 — RECOMENDACIONES
    # ═══════════════════════════════════════════════════════════
    with tab4:
        grupo = st.session_state.get("niif_grupo", 2)
        checklist = get_checklist(grupo)
        st.markdown("### 📌 Plan de acción priorizado")
        st.markdown(f"<p style='color:{TEXT_SEC}'>Ítems que requieren atención, ordenados por impacto.</p>",
                    unsafe_allow_html=True)

        pendientes = []
        for area, items in checklist.items():
            for codigo, desc, prioridad in items:
                val = st.session_state.get(f"chk_{codigo}", "❌ No cumple")
                if val in ("❌ No cumple", "⚠️ En proceso"):
                    pendientes.append({
                        "Estado": val, "Área": area.split("—")[0].strip(),
                        "Acción requerida": desc, "Prioridad": prioridad,
                        "_ord": {"Alta": 0, "Media": 1, "Baja": 2}[prioridad]
                    })

        pendientes.sort(key=lambda x: (x["_ord"], x["Estado"]))

        if not pendientes:
            st.success("🎉 ¡Excelente! No hay ítems pendientes en el checklist.")
        else:
            # Agrupar por prioridad
            for nivel in ["Alta", "Media", "Baja"]:
                grupo_items = [p for p in pendientes if p["Prioridad"] == nivel]
                if not grupo_items:
                    continue
                color = DANGER if nivel == "Alta" else (WARN if nivel == "Media" else TEXT_SEC)
                st.markdown(f"<p style='color:{color};font-weight:600;font-size:.9rem;margin:.8rem 0 .3rem'>⚡ Prioridad {nivel} — {len(grupo_items)} ítem(s)</p>",
                            unsafe_allow_html=True)
                for p in grupo_items:
                    estado_color = DANGER if p["Estado"] == "❌ No cumple" else WARN
                    st.markdown(f"""<div style="background:{BG_CARD};border-left:3px solid {estado_color};
                        border-radius:6px;padding:.6rem 1rem;margin-bottom:.4rem">
                        <p style="color:#E8F4FD;font-size:.86rem;margin:0">{p['Acción requerida']}</p>
                        <p style="color:{TEXT_SEC};font-size:.75rem;margin:.2rem 0 0">{p['Área']} · {p['Estado']}</p>
                        </div>""", unsafe_allow_html=True)

        # Servicios de asesoría disponibles
        st.markdown("---")
        st.markdown("#### 💼 Servicios de asesoría disponibles")
        servicios = [
            ("🔄", "Convergencia NIIF", "Transición completa al nuevo marco contable con plan de trabajo detallado."),
            ("📝", "Políticas Contables", "Generación del manual de políticas contables adaptado a tu sector y actividad."),
            ("📖", "Manuales de Procedimientos", "Documentación de procesos contables y financieros para tu equipo."),
            ("⚖️", "Re-expresión de Estados", "Ajuste y presentación de estados financieros bajo NIIF con períodos comparativos."),
            ("🔍", "Auditoría NIA", "Auditoría financiera bajo Normas Internacionales de Auditoría."),
            ("🏛️", "Información a Entidades", "Preparación de reportes para Supersociedades, SIC, DIAN y demás entidades."),
        ]
        cols = st.columns(2)
        for i, (icono, titulo, desc) in enumerate(servicios):
            cols[i % 2].markdown(f"""<div style="background:{BG_CARD};border:1px solid {BORDER};
                border-radius:8px;padding:.7rem 1rem;margin-bottom:.5rem">
                <p style="color:{ACCENT};font-weight:600;margin:0 0 .2rem">{icono} {titulo}</p>
                <p style="color:{TEXT_SEC};font-size:.8rem;margin:0">{desc}</p>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 5 — REPORTE
    # ═══════════════════════════════════════════════════════════
    with tab5:
        grupo = st.session_state.get("niif_grupo", 2)
        checklist = get_checklist(grupo)
        nombre_emp = st.session_state.get("niif_nombre", "Mi Empresa")
        totales = st.session_state.get("niif_totales", (0, 0, 0, 0))
        total_items, total_cumple, total_proceso, total_no = totales
        pct_global = total_cumple / total_items * 100 if total_items > 0 else 0

        st.markdown("### 📄 Reporte de diagnóstico")
        st.markdown(f"<p style='color:{TEXT_SEC}'>Genera el reporte para compartir con tu contador o junta directiva.</p>",
                    unsafe_allow_html=True)

        # Vista previa
        fecha_hoy = datetime.now().strftime("%d de %B de %Y")
        g_label = f"Grupo {grupo} — {'NIIF para Pymes' if grupo == 2 else 'Contabilidad Simplificada' if grupo == 3 else 'NIIF Plenas'}"
        color_g, label_g = semaforo_color(pct_global)

        st.markdown(f"""<div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;padding:1.2rem 1.5rem">
            <p style="color:{ACCENT};font-weight:700;font-size:1.1rem;margin:0 0 .3rem">
                🏛️ Diagnóstico NIIF — {nombre_emp or 'Mi Empresa'}</p>
            <p style="color:{TEXT_SEC};font-size:.82rem;margin:0 0 .8rem">Generado el {fecha_hoy} · SalazAnalytics</p>
            <p style="color:{TEXT_SEC};font-size:.85rem;margin:0">Clasificación: <strong style="color:{ACCENT}">{g_label}</strong></p>
            <p style="color:{color_g};font-weight:700;font-size:1.2rem;margin:.4rem 0">
                {pct_global:.0f}% cumplimiento global — {label_g}</p>
            <p style="color:{TEXT_SEC};font-size:.82rem">
                ✅ Cumple: {total_cumple} · ⚠️ En proceso: {total_proceso} · ❌ Pendiente: {total_no}</p>
            </div>""", unsafe_allow_html=True)

        # Generar Excel
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Diagnóstico NIIF"

            # Estilos
            hdr_fill = PatternFill("solid", fgColor="0D1B2A")
            sub_fill = PatternFill("solid", fgColor="132030")
            hdr_font = Font(bold=True, color="00C2FF", size=11)
            sub_font = Font(bold=True, color="E8F4FD", size=10)
            normal_font = Font(color="E8F4FD", size=9)
            thin = Border(
                left=Side(style='thin', color='1a3a5c'),
                right=Side(style='thin', color='1a3a5c'),
                bottom=Side(style='thin', color='1a3a5c'),
            )

            # Encabezado
            ws.merge_cells("A1:E1")
            ws["A1"] = f"DIAGNÓSTICO NIIF — {nombre_emp or 'Mi Empresa'}"
            ws["A1"].font = Font(bold=True, color="00C2FF", size=14)
            ws["A1"].fill = hdr_fill
            ws["A1"].alignment = Alignment(horizontal="center")

            ws.merge_cells("A2:E2")
            ws["A2"] = f"Generado: {fecha_hoy} | Clasificación: {g_label} | Cumplimiento: {pct_global:.0f}%"
            ws["A2"].font = Font(color="7B9BB5", size=10)
            ws["A2"].fill = hdr_fill
            ws["A2"].alignment = Alignment(horizontal="center")

            ws.append([])
            headers = ["Área", "Ítem", "Prioridad", "Estado", "Observaciones"]
            ws.append(headers)
            for i, h in enumerate(headers, 1):
                cell = ws.cell(row=4, column=i)
                cell.font = hdr_font
                cell.fill = hdr_fill
                cell.alignment = Alignment(horizontal="center")
                cell.border = thin

            row = 5
            STATUS_COLORS = {
                "✅ Cumple": "00FFB3",
                "⚠️ En proceso": "FFD93D",
                "❌ No cumple": "FF6B6B",
                "➖ No aplica": "7B9BB5",
            }
            for area, items in checklist.items():
                for codigo, desc, prioridad in items:
                    val = st.session_state.get(f"chk_{codigo}", "❌ No cumple")
                    p_color = "FF6B6B" if prioridad == "Alta" else ("FFD93D" if prioridad == "Media" else "7B9BB5")
                    s_color = STATUS_COLORS.get(val, "7B9BB5")
                    data = [area.split("—")[0].strip(), desc, prioridad, val, ""]
                    ws.append(data)
                    for col in range(1, 6):
                        cell = ws.cell(row=row, column=col)
                        cell.fill = sub_fill
                        cell.font = Font(color=s_color if col == 4 else ("FF6B6B" if (col == 3 and prioridad == "Alta") else "E8F4FD"), size=9)
                        cell.border = thin
                        cell.alignment = Alignment(wrap_text=True, vertical="top")
                    row += 1

            ws.column_dimensions["A"].width = 28
            ws.column_dimensions["B"].width = 55
            ws.column_dimensions["C"].width = 12
            ws.column_dimensions["D"].width = 18
            ws.column_dimensions["E"].width = 30

            # Hoja de obligaciones
            ws2 = wb.create_sheet("Obligaciones Tributarias")
            ws2.merge_cells("A1:D1")
            ws2["A1"] = "OBLIGACIONES TRIBUTARIAS APLICABLES"
            ws2["A1"].font = Font(bold=True, color="00C2FF", size=12)
            ws2["A1"].fill = hdr_fill
            ws2["A1"].alignment = Alignment(horizontal="center")
            ws2.append([])
            ws2.append(["Obligación", "Aplica", "Criterio", "Periodicidad"])
            for col in range(1, 5):
                ws2.cell(row=3, column=col).font = hdr_font
                ws2.cell(row=3, column=col).fill = hdr_fill
            for codigo, nombre, criterio, periodicidad in OBLIGACIONES_TRIBUTARIAS:
                aplica = "✅ Sí" if st.session_state.get(f"trib_{codigo}", False) else "❌ No"
                ws2.append([nombre, aplica, criterio, periodicidad])
            ws2.column_dimensions["A"].width = 35
            ws2.column_dimensions["B"].width = 10
            ws2.column_dimensions["C"].width = 50
            ws2.column_dimensions["D"].width = 35

            buf = BytesIO()
            wb.save(buf)
            buf.seek(0)

            st.download_button(
                label="📥 Descargar reporte Excel",
                data=buf,
                file_name=f"Diagnostico_NIIF_{(nombre_emp or 'empresa').replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error generando Excel: {e}")

        st.markdown(f"""<div style="background:{BG_CARD};border-left:4px solid {ACCENT};
            border-radius:8px;padding:.8rem 1.2rem;margin-top:1rem">
            <p style="color:{ACCENT};font-weight:600;margin:0 0 .2rem">💡 ¿Necesitas asesoría?</p>
            <p style="color:{TEXT_SEC};font-size:.84rem;margin:0">
            En SalazAnalytics te acompañamos en convergencia NIIF, políticas contables,
            re-expresión de estados y auditoría bajo NIA. Escríbenos para una propuesta personalizada.</p>
            </div>""", unsafe_allow_html=True)
