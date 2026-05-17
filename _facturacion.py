import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
import io
import json
import re

# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────

def generar_pdf_factura(factura):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)

        COLOR_DARK  = colors.HexColor('#0D1B2A')
        COLOR_CYAN  = colors.HexColor('#00C2FF')
        COLOR_GRAY  = colors.HexColor('#7B9BB5')
        COLOR_LIGHT = colors.HexColor('#E8F4FD')

        style_titulo = ParagraphStyle('titulo', fontSize=22, textColor=COLOR_DARK,
                                      fontName='Helvetica-Bold', spaceAfter=4)
        style_sub    = ParagraphStyle('sub',    fontSize=10, textColor=COLOR_GRAY,
                                      fontName='Helvetica', spaceAfter=2)
        style_label  = ParagraphStyle('label',  fontSize=9,  textColor=COLOR_GRAY,
                                      fontName='Helvetica-Bold')
        style_value  = ParagraphStyle('value',  fontSize=10, textColor=COLOR_DARK,
                                      fontName='Helvetica')
        style_right  = ParagraphStyle('right',  fontSize=10, textColor=COLOR_DARK,
                                      fontName='Helvetica', alignment=TA_RIGHT)

        story = []

        # Header
        header_data = [[
            Paragraph(factura['empresa_nombre'], style_titulo),
            Paragraph(f"FACTURA No.<br/><font color='#00C2FF' size=18><b>{factura['numero']}</b></font>", style_right)
        ]]
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(header_table)
        story.append(Spacer(1, 4))

        for key, prefix in [('empresa_nit','NIT: '), ('empresa_direccion',''), ('empresa_telefono','Tel: '), ('empresa_email','')]:
            if factura.get(key):
                story.append(Paragraph(f"{prefix}{factura[key]}", style_sub))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=COLOR_CYAN))
        story.append(Spacer(1, 8))

        # Cliente y fechas
        info_data = [
            [Paragraph("FACTURAR A:", style_label), Paragraph("", style_label),
             Paragraph("FECHA FACTURA:", style_label), Paragraph(str(factura['fecha']), style_value)],
            [Paragraph(factura['cliente_nombre'], style_value), Paragraph("", style_label),
             Paragraph("FECHA VENCIMIENTO:", style_label), Paragraph(str(factura['fecha_vence']), style_value)],
        ]
        for key, prefix in [('cliente_nit','NIT/CC: '), ('cliente_email','Email: ')]:
            if factura.get(key):
                info_data.append([Paragraph(f"{prefix}{factura[key]}", style_value),
                                  Paragraph("",""), Paragraph("",""), Paragraph("","")])

        info_table = Table(info_data, colWidths=[2.5*inch, 0.5*inch, 1.8*inch, 1.7*inch])
        info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 12))

        # Items
        table_data = [['DESCRIPCIÓN', 'CANT', 'VALOR UNIT.', 'IVA %', 'TOTAL']]
        for item in factura['items']:
            total_item = item['cantidad'] * item['valor_unitario'] * (1 + item['iva']/100)
            table_data.append([
                item['descripcion'],
                str(item['cantidad']),
                f"${item['valor_unitario']:,.0f}",
                f"{item['iva']}%",
                f"${total_item:,.0f}"
            ])

        items_table = Table(table_data, colWidths=[3.0*inch, 0.7*inch, 1.2*inch, 0.7*inch, 1.4*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_DARK),
            ('TEXTCOLOR',  (0,0), (-1,0), COLOR_CYAN),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,0), 9),
            ('ALIGN',      (1,0), (-1,-1), 'RIGHT'),
            ('ALIGN',      (0,0), (0,-1),  'LEFT'),
            ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',   (0,1), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_LIGHT, colors.white]),
            ('GRID',       (0,0), (-1,-1), 0.5, COLOR_GRAY),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 12))

        # Totales
        subtotal  = sum(i['cantidad'] * i['valor_unitario'] for i in factura['items'])
        total_iva = sum(i['cantidad'] * i['valor_unitario'] * i['iva']/100 for i in factura['items'])
        total     = subtotal + total_iva

        totales_data = [
            ['', 'Subtotal:', f"${subtotal:,.0f}"],
            ['', 'IVA:',      f"${total_iva:,.0f}"],
            ['', 'TOTAL:',    f"${total:,.0f}"],
        ]
        totales_table = Table(totales_data, colWidths=[3.5*inch, 1.8*inch, 1.7*inch])
        totales_table.setStyle(TableStyle([
            ('ALIGN',    (1,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,1),  'Helvetica'),
            ('FONTNAME', (0,2), (-1,2),  'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,1),  10),
            ('FONTSIZE', (0,2), (-1,2),  13),
            ('TEXTCOLOR', (2,2), (2,2),  COLOR_CYAN),
            ('LINEABOVE', (1,2), (-1,2), 1.5, COLOR_CYAN),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(totales_table)

        if factura.get('notas'):
            story.append(Spacer(1, 16))
            story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_GRAY))
            story.append(Spacer(1, 6))
            story.append(Paragraph("NOTAS:", style_label))
            story.append(Paragraph(factura['notas'], style_value))

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CYAN))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "Generado por SalazAnalytics · salazanalytics.com",
            ParagraphStyle('footer', fontSize=8, textColor=COLOR_GRAY, alignment=TA_CENTER)
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except ImportError:
        return None


# ─────────────────────────────────────────────
# SUPER AGENTE IA — parsea lenguaje natural a factura
# ─────────────────────────────────────────────

def agente_facturar(mensaje_usuario, empresa_info: dict) -> dict:
    """
    Llama a Claude para extraer datos de factura desde lenguaje natural.
    Retorna dict con: cliente, items sugeridos, notas.
    """
    import anthropic

    system_prompt = """Eres el Agente de Facturación de SalazAnalytics, un asistente experto en facturación para pequeñas empresas colombianas.

Tu tarea es extraer información de facturación desde mensajes en lenguaje natural y devolver SOLO un JSON válido con esta estructura exacta:

{
  "cliente_nombre": "string",
  "cliente_nit": "string o vacío",
  "cliente_email": "string o vacío",
  "cliente_dir": "string o vacío",
  "items": [
    {
      "descripcion": "string",
      "cantidad": número entero,
      "valor_unitario": número entero en pesos colombianos,
      "iva": 0 o 5 o 19
    }
  ],
  "notas": "string o vacío",
  "mensaje_agente": "string corto de confirmación amigable en español"
}

Reglas importantes:
- Si el IVA no se menciona, usa 19 para servicios profesionales, 0 para servicios médicos o educativos.
- Los valores siempre en pesos colombianos (COP).
- Si falta información, usa valores vacíos o razonables.
- El campo "mensaje_agente" es un mensaje amigable confirmando lo que entendiste.
- NO incluyas markdown, solo el JSON puro."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": mensaje_usuario}]
    )

    raw = response.content[0].text.strip()
    # Limpiar posibles backticks
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def agente_consejo_negocio(historial_facturas: list, empresa_info: dict) -> str:
    """
    Analiza el historial de facturas y da consejos de negocio.
    """
    import anthropic

    if not historial_facturas:
        return ""

    resumen = []
    for f in historial_facturas[-10:]:  # últimas 10
        resumen.append({
            "cliente": f.get("cliente_nombre", ""),
            "total": f.get("total", 0),
            "fecha": str(f.get("fecha", "")),
            "items_count": len(f.get("items", []))
        })

    system_prompt = """Eres un asesor de negocios experto en pequeñas empresas colombianas. 
Analiza el historial de facturación y da 2-3 consejos concretos y accionables en máximo 4 líneas.
Sé directo, útil y usa emojis moderadamente. Responde en español."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Historial: {json.dumps(resumen, ensure_ascii=False)}"}]
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────────
# HELPERS SESSION STATE
# ─────────────────────────────────────────────

def _init_state():
    defaults = {
        "facturas": [],
        "items_factura": [],
        "emp_nombre": "",
        "emp_nit": "",
        "emp_dir": "",
        "emp_tel": "",
        "emp_email": "",
        "emp_ciudad": "Pereira",
        "agente_procesando": False,
        "agente_resultado": None,
        "agente_error": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _empresa_info() -> dict:
    return {
        "nombre": st.session_state.get("emp_nombre", ""),
        "nit":    st.session_state.get("emp_nit", ""),
        "dir":    st.session_state.get("emp_dir", ""),
        "tel":    st.session_state.get("emp_tel", ""),
        "email":  st.session_state.get("emp_email", ""),
        "ciudad": st.session_state.get("emp_ciudad", "Pereira"),
    }

def _calcular_totales(items):
    subtotal  = sum(i["cantidad"] * i["valor_unitario"] for i in items)
    total_iva = sum(i["cantidad"] * i["valor_unitario"] * i["iva"] / 100 for i in items)
    return subtotal, total_iva, subtotal + total_iva

def _btn_descarga_pdf(pdf_bytes, num_factura, label="⬇️ Descargar Factura PDF"):
    b64  = base64.b64encode(pdf_bytes).decode()
    href = (
        f'<a href="data:application/pdf;base64,{b64}" '
        f'download="factura_{num_factura}.pdf" '
        f'style="display:inline-block;background:#00C2FF;color:#0D1B2A;font-weight:700;'
        f'padding:.7rem 1.5rem;border-radius:8px;text-decoration:none;font-size:1rem;">'
        f'{label}</a>'
    )
    st.markdown(href, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def show():
    _init_state()

    # ── Encabezado ──
    st.markdown("## 🧾 Facturación Electrónica")
    st.markdown(
        "<p style='color:#7B9BB5'>Crea facturas profesionales en PDF · "
        "o díselo al Agente IA y él la arma por ti.</p>",
        unsafe_allow_html=True
    )

    tab_agente, tab1, tab2, tab3 = st.tabs([
        "🤖 Agente IA", "📝 Nueva Factura", "📂 Historial", "⚙️ Mi Empresa"
    ])

    # ══════════════════════════════════════════
    # TAB CONFIGURACIÓN EMPRESA  (bug fix: keys explícitas)
    # ══════════════════════════════════════════
    with tab3:
        st.markdown("### Datos de tu empresa")
        st.markdown(
            "<p style='color:#7B9BB5;font-size:.85rem'>"
            "Estos datos aparecen en todas tus facturas.</p>",
            unsafe_allow_html=True
        )

        # FIX: usamos variables locales con key única y guardamos SOLO al presionar botón
        c1, c2 = st.columns(2)
        with c1:
            v_nombre  = st.text_input("Nombre o razón social", value=st.session_state["emp_nombre"], key="inp_emp_nombre")
            v_nit     = st.text_input("NIT",                    value=st.session_state["emp_nit"],    key="inp_emp_nit")
            v_dir     = st.text_input("Dirección",              value=st.session_state["emp_dir"],    key="inp_emp_dir")
        with c2:
            v_tel     = st.text_input("Teléfono",               value=st.session_state["emp_tel"],    key="inp_emp_tel")
            v_email   = st.text_input("Email",                  value=st.session_state["emp_email"],  key="inp_emp_email")
            v_ciudad  = st.text_input("Ciudad",                 value=st.session_state["emp_ciudad"], key="inp_emp_ciudad")

        # FIX: el botón actualiza el estado y NO hace rerun
        if st.button("💾 Guardar datos empresa", type="primary", key="btn_guardar_empresa"):
            st.session_state["emp_nombre"]  = st.session_state["inp_emp_nombre"]
            st.session_state["emp_nit"]     = st.session_state["inp_emp_nit"]
            st.session_state["emp_dir"]     = st.session_state["inp_emp_dir"]
            st.session_state["emp_tel"]     = st.session_state["inp_emp_tel"]
            st.session_state["emp_email"]   = st.session_state["inp_emp_email"]
            st.session_state["emp_ciudad"]  = st.session_state["inp_emp_ciudad"]
            st.success("✅ Datos guardados correctamente.")

        # Vista previa
        if st.session_state["emp_nombre"]:
            st.divider()
            st.markdown("**Vista previa en factura:**")
            st.info(
                f"**{st.session_state['emp_nombre']}**  \n"
                f"NIT: {st.session_state['emp_nit']}  \n"
                f"{st.session_state['emp_dir']} · {st.session_state['emp_ciudad']}  \n"
                f"Tel: {st.session_state['emp_tel']} · {st.session_state['emp_email']}"
            )

    # ══════════════════════════════════════════
    # TAB AGENTE IA
    # ══════════════════════════════════════════
    with tab_agente:
        st.markdown("### 🤖 Agente de Facturación IA")
        st.markdown(
            "<p style='color:#7B9BB5'>"
            "Cuéntale al agente a quién facturas y qué vendiste — él arma la factura por ti.</p>",
            unsafe_allow_html=True
        )

        # Ejemplos
        with st.expander("💡 Ver ejemplos de lo que puedes escribir"):
            st.markdown("""
- *"Factura a Juan Pérez NIT 900123456, consultoría de 3 horas a $150.000 cada una, con IVA"*
- *"Cobrar a Ferretería El Tornillo 2 cajas de tuercas a $85.000, sin IVA"*
- *"Factura a María López email maria@gmail.com, diseño de logo $800.000 más IVA, y manejo de redes sociales 1 mes $600.000 más IVA"*
- *"Servicio de contabilidad mensual a Empresa ABC por $500.000 IVA incluido, notas: pago a 30 días"*
            """)

        mensaje = st.text_area(
            "Describe la factura en tus propias palabras:",
            placeholder="Ej: Factura a Droguería Central NIT 860012345, venta de 5 botiquines a $45.000 cada uno sin IVA...",
            height=120,
            key="agente_mensaje"
        )

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            btn_agente = st.button("🚀 Crear factura con IA", type="primary", key="btn_agente")

        if btn_agente:
            if not mensaje.strip():
                st.warning("Escribe la descripción de la factura primero.")
            else:
                with st.spinner("El agente está procesando tu factura..."):
                    try:
                        resultado = agente_facturar(mensaje, _empresa_info())
                        st.session_state["agente_resultado"] = resultado
                        st.session_state["agente_error"] = ""
                    except Exception as e:
                        st.session_state["agente_resultado"] = None
                        st.session_state["agente_error"] = str(e)

        # Resultado del agente
        if st.session_state.get("agente_error"):
            st.error(f"Error del agente: {st.session_state['agente_error']}")

        if st.session_state.get("agente_resultado"):
            r = st.session_state["agente_resultado"]

            st.success(f"🤖 {r.get('mensaje_agente', 'Factura lista para revisar.')}")
            st.divider()

            # Mostrar y editar lo que extrajo el agente
            st.markdown("#### ✏️ Revisa y ajusta antes de generar")

            c1, c2 = st.columns(2)
            with c1:
                ag_cli_nombre = st.text_input("Cliente",  value=r.get("cliente_nombre",""), key="ag_cli_nombre")
                ag_cli_nit    = st.text_input("NIT/CC",   value=r.get("cliente_nit",""),    key="ag_cli_nit")
            with c2:
                ag_cli_email  = st.text_input("Email",    value=r.get("cliente_email",""),  key="ag_cli_email")
                ag_cli_dir    = st.text_input("Dirección",value=r.get("cliente_dir",""),    key="ag_cli_dir")

            ag_num = st.text_input(
                "Número de factura",
                value=f"FV-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state['facturas'])+1:03d}",
                key="ag_num_factura"
            )
            c1, c2 = st.columns(2)
            with c1:
                ag_fecha       = st.date_input("Fecha",           value=date.today(), key="ag_fecha")
            with c2:
                ag_fecha_vence = st.date_input("Fecha vencimiento", value=date.today(), key="ag_fecha_vence")

            ag_notas = st.text_area("Notas", value=r.get("notas",""), key="ag_notas")

            # Items del agente
            st.markdown("**Items extraídos:**")
            items_agente = r.get("items", [])
            if items_agente:
                df_ag = pd.DataFrame(items_agente)
                df_ag["Total"] = df_ag["cantidad"] * df_ag["valor_unitario"] * (1 + df_ag["iva"]/100)
                st.dataframe(df_ag, use_container_width=True)

                sub, iva_t, tot = _calcular_totales(items_agente)
                c1, c2, c3 = st.columns(3)
                c1.metric("Subtotal", f"${sub:,.0f}")
                c2.metric("IVA",      f"${iva_t:,.0f}")
                c3.metric("Total",    f"${tot:,.0f}")

            if st.button("📄 Generar PDF con estos datos", type="primary", key="btn_gen_agente"):
                if not ag_cli_nombre:
                    st.warning("El agente no detectó el nombre del cliente. Complétalo.")
                elif not items_agente:
                    st.warning("No se detectaron items. Describe mejor los productos o servicios.")
                else:
                    _, _, tot = _calcular_totales(items_agente)
                    factura = {
                        "numero":           ag_num,
                        "fecha":            ag_fecha,
                        "fecha_vence":      ag_fecha_vence,
                        "empresa_nombre":   st.session_state.get("emp_nombre", "SalazAnalytics"),
                        "empresa_nit":      st.session_state.get("emp_nit", ""),
                        "empresa_direccion":st.session_state.get("emp_dir", ""),
                        "empresa_telefono": st.session_state.get("emp_tel", ""),
                        "empresa_email":    st.session_state.get("emp_email", ""),
                        "cliente_nombre":   ag_cli_nombre,
                        "cliente_nit":      ag_cli_nit,
                        "cliente_email":    ag_cli_email,
                        "cliente_direccion":ag_cli_dir,
                        "items":            items_agente,
                        "notas":            ag_notas,
                        "total":            tot,
                    }
                    with st.spinner("Generando PDF..."):
                        pdf_bytes = generar_pdf_factura(factura)

                    if pdf_bytes:
                        st.session_state["facturas"].append(factura)
                        _btn_descarga_pdf(pdf_bytes, ag_num)
                        st.success(f"✅ Factura {ag_num} generada.")
                        st.session_state["agente_resultado"] = None
                    else:
                        st.error("Error generando PDF. Verifica que reportlab esté instalado.")

        # Consejos de negocio
        if st.session_state["facturas"]:
            st.divider()
            with st.expander("💡 Consejos de negocio basados en tus facturas"):
                if st.button("Analizar mi facturación", key="btn_consejos"):
                    with st.spinner("Analizando..."):
                        try:
                            consejo = agente_consejo_negocio(
                                st.session_state["facturas"], _empresa_info()
                            )
                            st.markdown(consejo)
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ══════════════════════════════════════════
    # TAB NUEVA FACTURA (manual) — bug fixes
    # ══════════════════════════════════════════
    with tab1:
        st.markdown("### Datos del cliente")
        c1, c2 = st.columns(2)
        with c1:
            cli_nombre = st.text_input("Nombre o razón social del cliente", key="m_cli_nombre")
            cli_nit    = st.text_input("NIT / Cédula del cliente",          key="m_cli_nit")
        with c2:
            cli_email  = st.text_input("Email del cliente",   key="m_cli_email")
            cli_dir    = st.text_input("Dirección del cliente", key="m_cli_dir")

        st.divider()
        st.markdown("### Datos de la factura")
        c1, c2, c3 = st.columns(3)
        with c1:
            num_factura = st.text_input(
                "Número de factura",
                value=f"FV-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state['facturas'])+1:03d}",
                key="m_num_factura"
            )
        with c2:
            fecha_factura = st.date_input("Fecha",               value=date.today(), key="m_fecha")
        with c3:
            fecha_vence   = st.date_input("Fecha de vencimiento", value=date.today(), key="m_fecha_vence")

        st.divider()
        st.markdown("### Productos y servicios")

        c1, c2, c3, c4 = st.columns([3, 1, 1.5, 1])
        with c1:
            desc  = st.text_input("Descripción", key="m_desc_item")
        with c2:
            cant  = st.number_input("Cantidad",       min_value=1, value=1,    key="m_cant_item")
        with c3:
            valor = st.number_input("Valor unitario", min_value=0, value=0, step=1000, key="m_valor_item")
        with c4:
            iva   = st.selectbox("IVA %", [0, 5, 19], key="m_iva_item")

        if st.button("➕ Agregar item", key="btn_agregar_item"):
            if not desc:
                st.warning("Escribe la descripción del producto o servicio.")
            elif valor <= 0:
                st.warning("El valor unitario debe ser mayor a 0.")
            else:
                # FIX: leer desde session_state (así sobrevive al rerun)
                st.session_state["items_factura"].append({
                    "descripcion":    st.session_state["m_desc_item"],
                    "cantidad":       st.session_state["m_cant_item"],
                    "valor_unitario": st.session_state["m_valor_item"],
                    "iva":            st.session_state["m_iva_item"],
                })
                st.rerun()

        # Mostrar items
        if st.session_state["items_factura"]:
            st.markdown("**Items agregados:**")
            df_items = pd.DataFrame(st.session_state["items_factura"])
            df_items["Total"] = df_items["cantidad"] * df_items["valor_unitario"] * (1 + df_items["iva"]/100)

            # Botones de eliminar por fila
            for i, item in enumerate(st.session_state["items_factura"]):
                col_desc, col_tot, col_del = st.columns([4, 2, 1])
                total_item = item["cantidad"] * item["valor_unitario"] * (1 + item["iva"]/100)
                col_desc.markdown(f"**{item['descripcion']}** × {item['cantidad']}")
                col_tot.markdown(f"${total_item:,.0f}")
                if col_del.button("🗑️", key=f"del_item_{i}", help="Eliminar"):
                    st.session_state["items_factura"].pop(i)
                    st.rerun()

            sub, iva_t, tot = _calcular_totales(st.session_state["items_factura"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", f"${sub:,.0f}")
            c2.metric("IVA",      f"${iva_t:,.0f}")
            c3.metric("Total",    f"${tot:,.0f}")

            if st.button("🗑️ Limpiar todos los items", key="btn_limpiar"):
                st.session_state["items_factura"] = []
                st.rerun()

        notas = st.text_area(
            "Notas adicionales (opcional)",
            placeholder="Formas de pago, observaciones...",
            key="m_notas"
        )

        st.divider()
        if st.button("📄 Generar Factura PDF", type="primary", key="btn_generar_manual"):
            if not cli_nombre:
                st.warning("Ingresa el nombre del cliente.")
            elif not st.session_state["items_factura"]:
                st.warning("Agrega al menos un producto o servicio.")
            else:
                # FIX: calcular total aquí siempre
                sub, iva_t, tot = _calcular_totales(st.session_state["items_factura"])
                factura = {
                    "numero":           num_factura,
                    "fecha":            fecha_factura,
                    "fecha_vence":      fecha_vence,
                    "empresa_nombre":   st.session_state.get("emp_nombre", "SalazAnalytics"),
                    "empresa_nit":      st.session_state.get("emp_nit", ""),
                    "empresa_direccion":st.session_state.get("emp_dir", ""),
                    "empresa_telefono": st.session_state.get("emp_tel", ""),
                    "empresa_email":    st.session_state.get("emp_email", ""),
                    "cliente_nombre":   cli_nombre,
                    "cliente_nit":      cli_nit,
                    "cliente_email":    cli_email,
                    "cliente_direccion":cli_dir,
                    "items":            st.session_state["items_factura"].copy(),
                    "notas":            notas,
                    "total":            tot,
                }
                with st.spinner("Generando PDF..."):
                    pdf_bytes = generar_pdf_factura(factura)

                if pdf_bytes:
                    st.session_state["facturas"].append(factura)
                    _btn_descarga_pdf(pdf_bytes, num_factura)
                    st.success(f"✅ Factura {num_factura} generada exitosamente.")
                    st.session_state["items_factura"] = []
                else:
                    st.error("Error generando PDF. Verifica que reportlab esté instalado.")

    # ══════════════════════════════════════════
    # TAB HISTORIAL
    # ══════════════════════════════════════════
    with tab2:
        st.markdown("### Historial de facturas")
        if not st.session_state["facturas"]:
            st.info("No hay facturas generadas aún.")
        else:
            # Métricas rápidas
            total_facturado = sum(f.get("total", 0) for f in st.session_state["facturas"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total facturas",    len(st.session_state["facturas"]))
            c2.metric("Total facturado",   f"${total_facturado:,.0f}")
            c3.metric("Promedio factura",  f"${total_facturado // len(st.session_state['facturas']):,.0f}")

            st.divider()

            for f in reversed(st.session_state["facturas"]):
                with st.expander(
                    f"📄 {f['numero']} · {f['cliente_nombre']} · ${f.get('total',0):,.0f} · {f['fecha']}"
                ):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Cliente:** {f['cliente_nombre']}")
                    c1.write(f"**NIT:** {f.get('cliente_nit','—')}")
                    c2.write(f"**Fecha:** {f['fecha']}")
                    c2.write(f"**Vence:** {f['fecha_vence']}")

                    if f.get("items"):
                        df = pd.DataFrame(f["items"])
                        df["Total"] = df["cantidad"] * df["valor_unitario"] * (1 + df["iva"]/100)
                        st.dataframe(df, use_container_width=True)

                    if st.button(f"⬇️ Descargar PDF", key=f"regen_{f['numero']}"):
                        pdf_bytes = generar_pdf_factura(f)
                        if pdf_bytes:
                            _btn_descarga_pdf(pdf_bytes, f["numero"], label=f"📥 {f['numero']}.pdf")
