"""
_simulador_nomina.py  —  SalazAnalytics
Micro-activo: Simulador de Nómina Colombia 2026
SMMLV $1.750.905 · Auxilio transporte $249.095
Incremento 23% · Ley 2101/2021 · CST Art. 64
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

# ── Paleta ────────────────────────────────────────────────────────────────────
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
PALETTE  = [ACCENT, PURPLE, SUCCESS, DANGER, WARN, "#4ECDC4"]

# ── Constantes Colombia 2026 ──────────────────────────────────────────────────
SMMLV_2026      = 1_750_905
AUX_TRANS_2026  = 249_095
SMMLV_2025      = 1_423_500   # Para comparativo (aprox con 23% de incremento)
AUX_TRANS_2025  = 200_000

# Aportes seguridad social (% sobre salario)
SS = {
    "salud_emp":   0.085,   # empleador
    "salud_trab":  0.04,    # trabajador
    "pension_emp": 0.12,    # empleador
    "pension_trab":0.04,    # trabajador
    "arl": {                # Clases de riesgo
        "I   — Riesgo mínimo (0.522%)":   0.00522,
        "II  — Riesgo bajo (1.044%)":     0.01044,
        "III — Riesgo medio (2.436%)":    0.02436,
        "IV  — Riesgo alto (4.350%)":     0.04350,
        "V   — Riesgo máximo (6.960%)":   0.06960,
    },
}

# Parafiscales (sobre salario, solo aplica si empresa >= 10 trabajadores para SENA/ICBF)
PARAFISCALES = {
    "sena":  0.02,
    "icbf":  0.03,
    "caja":  0.04,
}

# Prestaciones sociales (provisión mensual sobre salario + aux trans si aplica)
PRESTACIONES = {
    "prima":           0.0833,   # 8.33%
    "cesantias":       0.0833,   # 8.33%
    "int_cesantias":   0.01,     # 1% mensual sobre cesantías (12% anual)
    "vacaciones":      0.0417,   # 4.17% solo sobre salario
}

NIVELES_RIESGO = list(SS["arl"].keys())


# ── Utilidades ────────────────────────────────────────────────────────────────
def fmt(v):
    try:
        return f"${v:,.0f}"
    except Exception:
        return str(v)


def card_html(titulo, valor, color=ACCENT, sub=""):
    sub_h = f"<p style='color:{TEXT_SEC};font-size:.72rem;margin:.1rem 0 0;'>{sub}</p>" if sub else ""
    return f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;
                padding:.9rem 1rem;text-align:center;">
        <p style="color:{TEXT_SEC};font-size:.74rem;margin:0 0 .2rem;">{titulo}</p>
        <p style="color:{color};font-weight:700;font-size:1.3rem;margin:0;">{valor}</p>
        {sub_h}
    </div>"""


def plot_base():
    return dict(paper_bgcolor=BG_DARK, plot_bgcolor=BG_DARK,
                font_color="#E8F4FD", legend=dict(bgcolor=BG_CARD))


# ── Motor de cálculo ──────────────────────────────────────────────────────────
def calcular_nomina(salario, riesgo_key, parafiscales=True, meses=1,
                    horas_extra_diurnas=0, horas_extra_nocturnas=0,
                    horas_extra_dominicales=0):
    """
    Retorna dict con todos los componentes de nómina (mensual).
    """
    # Auxilio de transporte: aplica si salario <= 2 SMMLV
    aux_trans = AUX_TRANS_2026 if salario <= 2 * SMMLV_2026 else 0

    # Horas extras (factor sobre valor hora ordinaria)
    v_hora = salario / 240  # 30 días × 8 horas
    h_extra = {
        "diurna":      horas_extra_diurnas    * v_hora * 1.25,
        "nocturna":    horas_extra_nocturnas   * v_hora * 1.75,
        "dominical":   horas_extra_dominicales * v_hora * 2.00,
    }
    total_hex = sum(h_extra.values())

    devengado = salario + aux_trans + total_hex

    # ── Deducciones trabajador ──────────────────────────────────────────────
    salud_trab   = salario * SS["salud_trab"]
    pension_trab = salario * SS["pension_trab"]
    total_deducido = salud_trab + pension_trab
    neto_trabajador = devengado - total_deducido

    # ── Aportes empleador ───────────────────────────────────────────────────
    arl_pct      = SS["arl"][riesgo_key]
    salud_emp    = salario * SS["salud_emp"]
    pension_emp  = salario * SS["pension_emp"]
    arl_emp      = salario * arl_pct

    sena  = salario * PARAFISCALES["sena"]  if parafiscales else 0
    icbf  = salario * PARAFISCALES["icbf"]  if parafiscales else 0
    caja  = salario * PARAFISCALES["caja"]

    # ── Prestaciones sociales (provisión mensual) ───────────────────────────
    base_prest = salario + aux_trans        # prima y cesantías incluyen aux trans
    prima      = base_prest * PRESTACIONES["prima"]
    cesantias  = base_prest * PRESTACIONES["cesantias"]
    int_ces    = cesantias  * PRESTACIONES["int_cesantias"]
    vacaciones = salario    * PRESTACIONES["vacaciones"]  # solo salario

    total_seg_social_emp = salud_emp + pension_emp + arl_emp
    total_parafiscales   = sena + icbf + caja
    total_prestaciones   = prima + cesantias + int_ces + vacaciones

    costo_total_emp = (salario + aux_trans + total_hex
                       + total_seg_social_emp
                       + total_parafiscales
                       + total_prestaciones)

    factor = costo_total_emp / salario if salario > 0 else 0

    return {
        # Devengado
        "salario":            salario,
        "aux_trans":          aux_trans,
        "hex_diurna":         h_extra["diurna"],
        "hex_nocturna":       h_extra["nocturna"],
        "hex_dominical":      h_extra["dominical"],
        "total_hex":          total_hex,
        "devengado":          devengado,
        # Deducciones trabajador
        "salud_trab":         salud_trab,
        "pension_trab":       pension_trab,
        "total_deducido":     total_deducido,
        "neto_trabajador":    neto_trabajador,
        # Aportes empleador
        "salud_emp":          salud_emp,
        "pension_emp":        pension_emp,
        "arl_emp":            arl_emp,
        "sena":               sena,
        "icbf":               icbf,
        "caja":               caja,
        "total_seg_social":   total_seg_social_emp,
        "total_parafiscales": total_parafiscales,
        # Prestaciones
        "prima":              prima,
        "cesantias":          cesantias,
        "int_cesantias":      int_ces,
        "vacaciones":         vacaciones,
        "total_prestaciones": total_prestaciones,
        # Totales
        "costo_total":        costo_total_emp,
        "factor_prestacional":factor,
    }


def calcular_liquidacion(salario, años_trabajados, meses_extra=0,
                          tipo_retiro="Sin justa causa"):
    """
    Calcula liquidación y/o indemnización según CST Art. 64.
    """
    aux_trans   = AUX_TRANS_2026 if salario <= 2 * SMMLV_2026 else 0
    base_prest  = salario + aux_trans
    fraccion    = meses_extra / 12

    prima_prop  = base_prest * 0.0833 * 12 * fraccion
    ces_prop    = base_prest * 0.0833 * 12 * fraccion
    int_ces     = ces_prop * 0.12
    vac_prop    = salario  * 0.0417 * 12 * fraccion

    # Indemnización por despido sin justa causa
    indem = 0
    if tipo_retiro == "Sin justa causa":
        limite_10_smmlv = 10 * SMMLV_2026
        if años_trabajados < 1:
            dias = 30 if salario <= limite_10_smmlv else 20
        else:
            if salario <= limite_10_smmlv:
                dias = 30 + 20 * (años_trabajados - 1 + fraccion)
            else:
                dias = 20 + 15 * (años_trabajados - 1 + fraccion)
        indem = (salario / 30) * dias

    total = prima_prop + ces_prop + int_ces + vac_prop + indem
    return {
        "prima_prop":     prima_prop,
        "cesantias_prop": ces_prop,
        "int_cesantias":  int_ces,
        "vacaciones_prop":vac_prop,
        "indemnizacion":  indem,
        "total":          total,
    }


# ════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
def show():
    st.markdown("## 👥 Simulador de Nómina Colombia 2026")
    st.markdown(
        f"<p style='color:{TEXT_SEC}'>SMMLV <strong style='color:{ACCENT}'>$1.750.905</strong> · "
        f"Aux. transporte <strong style='color:{ACCENT}'>$249.095</strong> · "
        f"Incremento <strong style='color:{WARN}'>+23%</strong> vs 2025</p>",
        unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💼 Calculadora Individual",
        "👥 Simulador de Planta",
        "📊 Impacto del 23%",
        "⚖️ Despido vs. Retención",
        "🎯 Punto de Equilibrio",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — CALCULADORA INDIVIDUAL
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💼 Costo real de un empleado")
        st.markdown(f"<p style='color:{TEXT_SEC};font-size:.87rem;'>"
                    f"Calcula el costo total mensual incluyendo seguridad social, "
                    f"parafiscales y provisión de prestaciones.</p>",
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            cargo = st.text_input("Cargo / nombre", value="Empleado", key="ci_cargo")
            salario = st.number_input(
                "Salario mensual ($)", min_value=SMMLV_2026,
                value=SMMLV_2026, step=50_000, format="%d", key="ci_sal",
                help=f"Mínimo SMMLV 2026: {fmt(SMMLV_2026)}")
            parafiscales = st.checkbox("¿Empresa ≥ 10 trabajadores? (SENA/ICBF)",
                                       value=True, key="ci_para")
        with c2:
            riesgo = st.selectbox("Nivel de riesgo ARL", NIVELES_RIESGO, key="ci_riesgo")
            hex_diurnas     = st.number_input("Horas extra diurnas/mes",     0, 96, 0, key="ci_hd")
            hex_nocturnas   = st.number_input("Horas extra nocturnas/mes",   0, 96, 0, key="ci_hn")
        with c3:
            hex_dom = st.number_input("Horas extra dominicales/mes", 0, 48, 0, key="ci_hdom")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:{BG_DEEP};border:1px solid {BORDER};"
                f"border-radius:8px;padding:.8rem;font-size:.82rem;color:{TEXT_SEC};'>"
                f"<b style='color:{ACCENT}'>Referencia 2026</b><br>"
                f"SMMLV: {fmt(SMMLV_2026)}<br>"
                f"Aux. transporte: {fmt(AUX_TRANS_2026)}<br>"
                f"Total mínimo: {fmt(SMMLV_2026 + AUX_TRANS_2026)}</div>",
                unsafe_allow_html=True)

        n = calcular_nomina(salario, riesgo, parafiscales,
                            horas_extra_diurnas=hex_diurnas,
                            horas_extra_nocturnas=hex_nocturnas,
                            horas_extra_dominicales=hex_dom)

        st.divider()
        st.markdown(f"#### Resumen — {cargo}")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card_html("Salario + aux. transporte",
                              fmt(n["salario"] + n["aux_trans"]), TEXT_SEC,
                              "devengado base"), unsafe_allow_html=True)
        c2.markdown(card_html("Neto trabajador",
                              fmt(n["neto_trabajador"]), SUCCESS,
                              "lo que recibe"), unsafe_allow_html=True)
        c3.markdown(card_html("Costo total empleador",
                              fmt(n["costo_total"]), DANGER,
                              "lo que paga la empresa"), unsafe_allow_html=True)
        c4.markdown(card_html("Factor prestacional",
                              f"{n['factor_prestacional']:.2f}x", WARN,
                              "costo real / salario"), unsafe_allow_html=True)

        # Desglose completo
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Devengado")
            data_dev = {
                "Concepto": ["Salario base", "Aux. transporte",
                             "H.E. diurnas", "H.E. nocturnas", "H.E. dominicales"],
                "Valor": [n["salario"], n["aux_trans"],
                          n["hex_diurna"], n["hex_nocturna"], n["hex_dominical"]],
            }
            df_dev = pd.DataFrame(data_dev)
            df_dev["Valor"] = df_dev["Valor"].apply(fmt)
            st.dataframe(df_dev, use_container_width=True, hide_index=True)

            st.markdown("##### Deducciones trabajador")
            data_ded = {
                "Concepto": ["Salud (4%)", "Pensión (4%)", "TOTAL DEDUCIDO"],
                "Valor": [n["salud_trab"], n["pension_trab"], n["total_deducido"]],
            }
            df_ded = pd.DataFrame(data_ded)
            df_ded["Valor"] = df_ded["Valor"].apply(fmt)
            st.dataframe(df_ded, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("##### Aportes empleador")
            data_emp = {
                "Concepto": [
                    "Salud (8.5%)", "Pensión (12%)", "ARL",
                    "SENA (2%)", "ICBF (3%)", "Caja comp. (4%)",
                    "Prima servicios", "Cesantías", "Int. cesantías", "Vacaciones",
                    "TOTAL COSTO ADICIONAL",
                ],
                "Valor": [
                    n["salud_emp"], n["pension_emp"], n["arl_emp"],
                    n["sena"], n["icbf"], n["caja"],
                    n["prima"], n["cesantias"], n["int_cesantias"], n["vacaciones"],
                    n["costo_total"] - n["salario"] - n["aux_trans"] - n["total_hex"],
                ],
            }
            df_emp = pd.DataFrame(data_emp)
            df_emp["Valor"] = df_emp["Valor"].apply(fmt)
            st.dataframe(df_emp, use_container_width=True, hide_index=True)

        # Gráfico composición del costo
        labels = ["Salario", "Aux. transporte", "Seg. social emp.",
                  "Parafiscales", "Prestaciones sociales"]
        values = [n["salario"], n["aux_trans"], n["total_seg_social"],
                  n["total_parafiscales"], n["total_prestaciones"]]
        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.45, marker_colors=PALETTE,
            textinfo="label+percent"))
        fig.update_layout(title=f"Composición del costo — {cargo}",
                          **plot_base())
        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — SIMULADOR DE PLANTA
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 👥 Costo total de tu planta de personal")

        if "planta_empleados" not in st.session_state:
            st.session_state["planta_empleados"] = [
                {"cargo": "Gerente", "salario": 5_000_000, "cantidad": 1},
                {"cargo": "Operario",  "salario": SMMLV_2026, "cantidad": 3},
                {"cargo": "Vendedor",  "salario": 2_000_000, "cantidad": 2},
            ]

        with st.form("form_planta", clear_on_submit=True):
            fc1, fc2, fc3 = st.columns([3, 2, 1])
            ncargo   = fc1.text_input("Cargo", placeholder="Ej: Operario")
            nsal     = fc2.number_input("Salario ($)", min_value=SMMLV_2026,
                                        value=SMMLV_2026, step=50_000, format="%d")
            ncant    = fc3.number_input("Cant.", min_value=1, value=1)
            ok = st.form_submit_button("➕ Agregar cargo", type="primary",
                                       use_container_width=True)
            if ok and ncargo.strip():
                st.session_state["planta_empleados"].append(
                    {"cargo": ncargo.strip(), "salario": int(nsal), "cantidad": int(ncant)})
                st.rerun()

        planta = st.session_state["planta_empleados"]
        riesgo_planta = st.selectbox("Nivel de riesgo ARL (planta)",
                                     NIVELES_RIESGO, key="plt_riesgo")
        parafiscales_plt = st.checkbox("¿Empresa ≥ 10 trabajadores?",
                                       value=True, key="plt_para")

        if planta:
            filas = []
            for emp in planta:
                n = calcular_nomina(emp["salario"], riesgo_planta, parafiscales_plt)
                filas.append({
                    "Cargo":             emp["cargo"],
                    "Cantidad":          emp["cantidad"],
                    "Salario unitario":  fmt(emp["salario"]),
                    "Costo unit./mes":   fmt(n["costo_total"]),
                    "Costo total/mes":   fmt(n["costo_total"] * emp["cantidad"]),
                    "Costo anual":       fmt(n["costo_total"] * emp["cantidad"] * 12),
                    "_costo_mes":        n["costo_total"] * emp["cantidad"],
                })

            df_planta = pd.DataFrame(filas)
            total_mes = df_planta["_costo_mes"].sum()
            total_año = total_mes * 12

            st.dataframe(df_planta.drop(columns=["_costo_mes"]),
                         use_container_width=True, hide_index=True)

            c1, c2, c3 = st.columns(3)
            c1.markdown(card_html("Total empleados",
                                  str(sum(e["cantidad"] for e in planta)),
                                  ACCENT), unsafe_allow_html=True)
            c2.markdown(card_html("Costo nómina mensual",
                                  fmt(total_mes), DANGER,
                                  "incluyendo todas las cargas"), unsafe_allow_html=True)
            c3.markdown(card_html("Costo nómina anual",
                                  fmt(total_año), DANGER,
                                  "provisiones + seguridad social"), unsafe_allow_html=True)

            # Gráfico costo por cargo
            fig = px.bar(df_planta, x="Cargo", y="_costo_mes",
                         color="Cargo", color_discrete_sequence=PALETTE,
                         template="plotly_dark",
                         title="Costo mensual total por cargo",
                         labels={"_costo_mes": "Costo mensual ($)"})
            fig.update_layout(**plot_base())
            st.plotly_chart(fig, use_container_width=True)

            if st.button("🗑️ Limpiar planta", key="btn_clear_planta"):
                st.session_state["planta_empleados"] = []
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — IMPACTO DEL 23%
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📊 Impacto del incremento del 23% en tu nómina")
        st.markdown(
            f"<div style='background:{BG_CARD};border-left:4px solid {WARN};"
            f"border-radius:8px;padding:1rem 1.2rem;margin-bottom:1rem;'>"
            f"<p style='color:{WARN};font-weight:600;margin:0;'>⚠️ Contexto 2026</p>"
            f"<p style='color:#E8F4FD;font-size:.9rem;margin:.3rem 0 0;'>"
            f"El SMMLV subió de <b>{fmt(SMMLV_2025)}</b> a <b>{fmt(SMMLV_2026)}</b> — "
            f"un incremento del <b>+23%</b>. Para muchos empresarios, esto representa "
            f"el mayor impacto en nómina en años recientes.</p>"
            f"</div>", unsafe_allow_html=True)

        st.markdown("#### Simula el impacto en tu empresa")
        c1, c2 = st.columns(2)
        with c1:
            n_empleados_smmlv = st.number_input(
                "Empleados en SMMLV", 0, 500, 5, key="imp_smmlv",
                help="Empleados que ganan exactamente el salario mínimo")
            n_empleados_medio = st.number_input(
                "Empleados entre 1 y 2 SMMLV", 0, 500, 3, key="imp_medio")
            n_empleados_alto  = st.number_input(
                "Empleados > 2 SMMLV", 0, 500, 2, key="imp_alto")
        with c2:
            sal_medio = st.number_input(
                "Salario promedio 1-2 SMMLV ($)",
                min_value=SMMLV_2026, max_value=2*SMMLV_2026,
                value=int(1.5 * SMMLV_2026), step=50_000, format="%d", key="imp_sal_med")
            sal_alto = st.number_input(
                "Salario promedio > 2 SMMLV ($)",
                min_value=2*SMMLV_2026, max_value=20*SMMLV_2026,
                value=4*SMMLV_2026, step=100_000, format="%d", key="imp_sal_alt")
            riesgo_imp = st.selectbox("Nivel de riesgo ARL",
                                      NIVELES_RIESGO, key="imp_riesgo")

        # Calcular 2025 vs 2026
        def costo_2025(salario_2026, cantidad):
            sal_2025 = salario_2026 / 1.23
            n = calcular_nomina(sal_2025, riesgo_imp)
            return n["costo_total"] * cantidad

        def costo_2026(salario_2026, cantidad):
            n = calcular_nomina(salario_2026, riesgo_imp)
            return n["costo_total"] * cantidad

        grupos = [
            ("SMMLV",    SMMLV_2026,  n_empleados_smmlv),
            ("1-2 SMMLV", sal_medio,  n_empleados_medio),
            ("> 2 SMMLV", sal_alto,   n_empleados_alto),
        ]

        filas_imp = []
        total_2025 = total_2026 = 0
        for nombre, sal, cant in grupos:
            if cant == 0:
                continue
            c25 = costo_2025(sal, cant)
            c26 = costo_2026(sal, cant)
            delta = c26 - c25
            total_2025 += c25
            total_2026 += c26
            filas_imp.append({
                "Grupo": nombre,
                "Cantidad": cant,
                "Costo mensual 2025": fmt(c25),
                "Costo mensual 2026": fmt(c26),
                "Incremento mensual": fmt(delta),
                "Incremento anual":   fmt(delta * 12),
                "% cambio":           f"+{(delta/c25*100):.1f}%" if c25 > 0 else "N/A",
            })

        if filas_imp:
            st.dataframe(pd.DataFrame(filas_imp),
                         use_container_width=True, hide_index=True)

            delta_total = total_2026 - total_2025
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(card_html("Nómina mensual 2025", fmt(total_2025), TEXT_SEC), unsafe_allow_html=True)
            c2.markdown(card_html("Nómina mensual 2026", fmt(total_2026), DANGER), unsafe_allow_html=True)
            c3.markdown(card_html("Incremento mensual",  fmt(delta_total), WARN,
                                  f"+{delta_total/total_2025*100:.1f}% más"), unsafe_allow_html=True)
            c4.markdown(card_html("Incremento anual",    fmt(delta_total * 12), DANGER,
                                  "impacto total en el año"), unsafe_allow_html=True)

            # Gráfico comparativo
            grupos_nombres = [f["Grupo"] for f in filas_imp]
            vals_2025 = [costo_2025(g[1], g[2]) for g in grupos if g[2] > 0]
            vals_2026 = [costo_2026(g[1], g[2]) for g in grupos if g[2] > 0]

            fig = go.Figure()
            fig.add_bar(x=grupos_nombres, y=vals_2025, name="2025", marker_color=TEXT_SEC)
            fig.add_bar(x=grupos_nombres, y=vals_2026, name="2026", marker_color=DANGER)
            fig.update_layout(barmode="group", title="Costo nómina 2025 vs 2026",
                              xaxis_title="Grupo salarial", yaxis_title="$ mensual",
                              **plot_base())
            st.plotly_chart(fig, use_container_width=True)

            # Recomendaciones
            st.markdown("#### 💡 Alternativas para el empresario")
            alternativas = [
                ("🔄", "Contrato por prestación de servicios",
                 "Para roles no permanentes. Elimina parafiscales y prestaciones. "
                 "Asegúrate de que no haya subordinación para evitar sanciones."),
                ("⏰", "Reducción de jornada (Ley 2101/2021)",
                 "La jornada laboral se reduce gradualmente a 42h/semana. "
                 "Permite ajustar costos sin despidos."),
                ("🤖", "Automatización de procesos repetitivos",
                 "Evalúa qué tareas pueden automatizarse antes de contratar "
                 "o como alternativa a roles en SMMLV."),
                ("📈", "Incremento de productividad por empleado",
                 "Si el incremento es del 23%, el objetivo es aumentar la "
                 "productividad al menos en ese porcentaje para mantener márgenes."),
            ]
            for icono, titulo, desc in alternativas:
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid {BORDER};
                            border-radius:8px;padding:.9rem 1.1rem;margin-bottom:.6rem;">
                    <p style="color:{ACCENT};font-weight:600;margin:0 0 .3rem;">
                        {icono} {titulo}</p>
                    <p style="color:{TEXT_SEC};font-size:.86rem;margin:0;">{desc}</p>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — DESPIDO VS. RETENCIÓN
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚖️ ¿Despedir o retener? Análisis de costo real")
        st.markdown(
            f"<p style='color:{TEXT_SEC};font-size:.87rem;'>"
            f"Antes de tomar la decisión, calcula el costo real de cada opción. "
            f"Muchas veces retener es más económico que despedir.</p>",
            unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            sal_ret = st.number_input("Salario del empleado ($)",
                                      min_value=SMMLV_2026, value=SMMLV_2026,
                                      step=50_000, format="%d", key="ret_sal")
            años_serv = st.number_input("Años de servicio", 0, 40, 2, key="ret_años")
            meses_serv = st.number_input("Meses adicionales", 0, 11, 6, key="ret_meses")
        with c2:
            tipo_retiro = st.selectbox("Tipo de retiro",
                                       ["Sin justa causa", "Con justa causa",
                                        "Renuncia voluntaria"], key="ret_tipo")
            meses_retener = st.slider("¿Cuántos meses más retenerlo?",
                                      1, 24, 6, key="ret_meses_ret")
        with c3:
            riesgo_ret = st.selectbox("Nivel ARL", NIVELES_RIESGO, key="ret_riesgo")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:{BG_DEEP};border:1px solid {BORDER};"
                f"border-radius:8px;padding:.8rem;font-size:.82rem;color:{TEXT_SEC};'>"
                f"<b style='color:{ACCENT}'>Art. 64 CST</b><br>"
                f"Despido sin justa causa:<br>"
                f"≤ 1 año → 30 días salario<br>"
                f"> 1 año → 30d + 20d/año adicional<br>"
                f"(si salario ≤ 10 SMMLV)</div>",
                unsafe_allow_html=True)

        liq = calcular_liquidacion(sal_ret, años_serv, meses_serv, tipo_retiro)
        n_ret = calcular_nomina(sal_ret, riesgo_ret)
        costo_retener = n_ret["costo_total"] * meses_retener

        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"#### 🚪 Costo de despedir HOY")
            data_liq = {
                "Concepto": [
                    "Prima proporcional", "Cesantías proporcionales",
                    "Intereses sobre cesantías", "Vacaciones proporcionales",
                    "Indemnización (Art. 64)" if tipo_retiro == "Sin justa causa" else "Sin indemnización",
                    "TOTAL LIQUIDACIÓN",
                ],
                "Valor": [
                    liq["prima_prop"], liq["cesantias_prop"],
                    liq["int_cesantias"], liq["vacaciones_prop"],
                    liq["indemnizacion"], liq["total"],
                ],
            }
            df_liq = pd.DataFrame(data_liq)
            df_liq["Valor"] = df_liq["Valor"].apply(fmt)
            st.dataframe(df_liq, use_container_width=True, hide_index=True)

            st.markdown(
                card_html("Total a pagar si despide HOY",
                          fmt(liq["total"]), DANGER,
                          "incluye indemnización si aplica"),
                unsafe_allow_html=True)

        with c2:
            st.markdown(f"#### 🤝 Costo de retener {meses_retener} meses más")
            liq_futura = calcular_liquidacion(
                sal_ret, años_serv,
                meses_serv + meses_retener, tipo_retiro)
            costo_ret_total = costo_retener + liq_futura["total"]

            data_ret = {
                "Concepto": [
                    f"Nómina mensual × {meses_retener} meses",
                    "Liquidación futura (proyectada)",
                    "COSTO TOTAL (retener + liquidar después)",
                ],
                "Valor": [costo_retener, liq_futura["total"], costo_ret_total],
            }
            df_ret = pd.DataFrame(data_ret)
            df_ret["Valor"] = df_ret["Valor"].apply(fmt)
            st.dataframe(df_ret, use_container_width=True, hide_index=True)

            st.markdown(
                card_html(f"Total si retiene {meses_retener} meses y luego despide",
                          fmt(costo_ret_total), WARN,
                          "nómina + liquidación futura"),
                unsafe_allow_html=True)

        # Veredicto
        diferencia = costo_ret_total - liq["total"]
        st.divider()
        if liq["total"] < costo_ret_total:
            cv, iv = DANGER, "💡"
            msg = (f"Despedir hoy cuesta <b>{fmt(liq['total'])}</b> vs. "
                   f"retener {meses_retener} meses que costaría <b>{fmt(costo_ret_total)}</b>. "
                   f"Diferencia de <b>{fmt(diferencia)}</b>. "
                   f"<b>Considera si el empleado genera ese valor en {meses_retener} meses.</b>")
        else:
            cv, iv = SUCCESS, "✅"
            msg = (f"Retener {meses_retener} meses es más económico. "
                   f"El costo de retener ({fmt(costo_ret_total)}) es menor que "
                   f"liquidar hoy ({fmt(liq['total'])}). "
                   f"<b>Retener genera {fmt(abs(diferencia))} de ahorro.</b>")

        st.markdown(f"""
        <div style="background:{BG_CARD};border-left:4px solid {cv};
                    border-radius:10px;padding:1.2rem;margin-top:.5rem;">
            <p style="color:{cv};font-weight:700;font-size:1rem;margin:0;">
                {iv} Análisis financiero</p>
            <p style="color:#E8F4FD;font-size:.92rem;margin:.4rem 0 0;">{msg}</p>
        </div>""", unsafe_allow_html=True)

        # Gráfico comparativo
        fig = go.Figure(go.Bar(
            x=["Despedir HOY", f"Retener {meses_retener} meses\ny liquidar después"],
            y=[liq["total"], costo_ret_total],
            marker_color=[DANGER if liq["total"] <= costo_ret_total else SUCCESS,
                          SUCCESS if liq["total"] <= costo_ret_total else DANGER],
            text=[fmt(liq["total"]), fmt(costo_ret_total)],
            textposition="outside"))
        fig.update_layout(title="Comparativo de costos: despedir vs. retener",
                          yaxis_title="$ COP", **plot_base())
        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — PUNTO DE EQUILIBRIO NÓMINA
    # ════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### 🎯 ¿Cuánto debes vender para cubrir tu nómina?")
        st.markdown(
            f"<p style='color:{TEXT_SEC};font-size:.87rem;'>"
            f"Calcula el punto de equilibrio considerando la nómina como "
            f"costo fijo mensual.</p>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            costo_nom_mes = st.number_input(
                "Costo total de nómina mensual ($)",
                min_value=0, value=int(SMMLV_2026 * 1.65 * 5),
                step=100_000, format="%d", key="pe_nomina",
                help="Puedes calcularlo en la pestaña 'Simulador de Planta'")
            otros_fijos = st.number_input(
                "Otros costos fijos mensuales ($)",
                min_value=0, value=2_000_000, step=100_000, format="%d",
                key="pe_fijos",
                help="Arriendo, servicios, créditos, etc.")
        with c2:
            margen_bruto = st.slider(
                "Margen bruto del negocio (%)", 5, 90, 35, key="pe_margen",
                help="(Ventas - Costo de ventas) / Ventas × 100")
            precio_venta = st.number_input(
                "Precio promedio de venta por unidad ($)",
                min_value=1_000, value=50_000, step=1_000, format="%d",
                key="pe_precio")

        total_fijos = costo_nom_mes + otros_fijos
        pe_ventas = total_fijos / (margen_bruto / 100) if margen_bruto > 0 else 0
        pe_unidades = pe_ventas / precio_venta if precio_venta > 0 else 0
        pct_nomina = costo_nom_mes / total_fijos * 100 if total_fijos > 0 else 0

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card_html("Costos fijos totales", fmt(total_fijos), TEXT_SEC,
                              "nómina + otros fijos"), unsafe_allow_html=True)
        c2.markdown(card_html("Ventas mínimas necesarias", fmt(pe_ventas), ACCENT,
                              f"con margen del {margen_bruto}%"), unsafe_allow_html=True)
        c3.markdown(card_html("Unidades mínimas a vender", f"{pe_unidades:,.0f}",
                              SUCCESS, f"a {fmt(precio_venta)}/unidad"), unsafe_allow_html=True)
        c4.markdown(card_html("% de ventas que es nómina",
                              f"{pct_nomina:.1f}%", WARN,
                              "saludable < 30%"), unsafe_allow_html=True)

        # Curva del punto de equilibrio
        ventas_range = np.linspace(0, pe_ventas * 2.5, 300)
        ingresos = ventas_range
        costos = total_fijos + ventas_range * (1 - margen_bruto / 100)
        utilidad = ingresos - costos

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ventas_range / 1e6, y=ingresos / 1e6,
                                 mode="lines", name="Ingresos",
                                 line=dict(color=SUCCESS, width=2)))
        fig.add_trace(go.Scatter(x=ventas_range / 1e6, y=costos / 1e6,
                                 mode="lines", name="Costos totales",
                                 line=dict(color=DANGER, width=2)))
        fig.add_vline(x=pe_ventas / 1e6, line_dash="dash", line_color=ACCENT,
                      annotation_text=f"PE: {fmt(pe_ventas)}",
                      annotation_font_color=ACCENT)
        fig.add_hrect(y0=0, y1=total_fijos / 1e6,
                      fillcolor="rgba(255,107,107,0.07)", layer="below",
                      line_width=0, annotation_text="Zona pérdida",
                      annotation_font_color=DANGER,
                      annotation_position="top right")
        fig.update_layout(
            title="Punto de equilibrio — Nómina como costo fijo",
            xaxis_title="Ventas (millones $)",
            yaxis_title="Millones $",
            **plot_base())
        st.plotly_chart(fig, use_container_width=True)

        # Impacto del incremento 23% en el PE
        st.markdown("#### Impacto del +23% en el punto de equilibrio")
        costo_nom_2025 = costo_nom_mes / 1.23
        total_fijos_2025 = costo_nom_2025 + otros_fijos
        pe_2025 = total_fijos_2025 / (margen_bruto / 100) if margen_bruto > 0 else 0
        delta_pe = pe_ventas - pe_2025

        c1, c2, c3 = st.columns(3)
        c1.markdown(card_html("PE antes del incremento (2025)", fmt(pe_2025), TEXT_SEC), unsafe_allow_html=True)
        c2.markdown(card_html("PE después del incremento (2026)", fmt(pe_ventas), DANGER), unsafe_allow_html=True)
        c3.markdown(card_html("Ventas adicionales requeridas", fmt(delta_pe), WARN,
                              "para mantener el mismo margen"), unsafe_allow_html=True)
