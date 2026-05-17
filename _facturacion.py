import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
import io

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

        styles = getSampleStyleSheet()
        COLOR_DARK  = colors.HexColor('#0D1B2A')
        COLOR_CYAN  = colors.HexColor('#00C2FF')
        COLOR_GRAY  = colors.HexColor('#7B9BB5')
        COLOR_LIGHT = colors.HexColor('#E8F4FD')

        style_titulo = ParagraphStyle('titulo', fontSize=22, textColor=COLOR_DARK, fontName='Helvetica-Bold', spaceAfter=4)
        style_sub    = ParagraphStyle('sub',    fontSize=10, textColor=COLOR_GRAY, fontName='Helvetica', spaceAfter=2)
        style_label  = ParagraphStyle('label',  fontSize=9,  textColor=COLOR_GRAY, fontName='Helvetica-Bold')
        style_value  = ParagraphStyle('value',  fontSize=10, textColor=COLOR_DARK, fontName='Helvetica')
        style_right  = ParagraphStyle('right',  fontSize=10, textColor=COLOR_DARK, fontName='Helvetica', alignment=TA_RIGHT)

        story = []

        header_data = [[
            Paragraph(factura['empresa_nombre'], style_titulo),
            Paragraph(f"FACTURA No.<br/><font color='#00C2FF' size=18><b>{factura['numero']}</b></font>", style_right)
        ]]
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(header_table)
        story.append(Spacer(1, 4))

        for info in [factura.get('empresa_nit',''), factura.get('empresa_direccion',''),
                     factura.get('empresa_telefono',''), factura.get('empresa_email','')]:
            if info:
                story.append(Paragraph(info, style_sub))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=COLOR_CYAN))
        story.append(Spacer(1, 8))

        info_data = [
            [Paragraph("FACTURAR A:", style_label), Paragraph("", style_label),
             Paragraph("FECHA FACTURA:", style_label), Paragraph(str(factura['fecha']), style_value)],
            [Paragraph(factura['cliente_nombre'], style_value), Paragraph("", style_label),
             Paragraph("VENCIMIENTO:", style_label), Paragraph(str(factura['fecha_vence']), style_value)],
        ]
        if factura.get('cliente_nit'):
            info_data.append([Paragraph(f"NIT/CC: {factura['cliente_nit']}", style_value),
                              Paragraph("",""), Paragraph("",""), Paragraph("","")])
        if factura.get('cliente_email'):
            info_data.append([Paragraph(f"Email: {factura['cliente_email']}", style_value),
                              Paragraph("",""), Paragraph("",""), Paragraph("","")])

        info_table = Table(info_data, colWidths=[2.5*inch, 0.5*inch, 1.8*inch, 1.7*inch])
        info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 12))

        table_data = [['DESCRIPCION', 'CANT', 'VALOR UNIT.', 'IVA %', 'TOTAL']]
        subtotal = 0
        total_iva = 0
        for item in factura['items']:
            sub_item = item['cantidad'] * item['valor_unitario']
            iva_item = sub_item * item['iva'] / 100
            total_item = sub_item + iva_item
            subtotal += sub_item
            total_iva += iva_item
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
            ('TEXTCOLOR', (0,0), (-1,0), COLOR_CYAN),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_LIGHT, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, COLOR_GRAY),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 12))

        total = subtotal + total_iva
        totales_data = [
            ['', 'Subtotal:', f"${subtotal:,.0f}"],
            ['', 'IVA:', f"${total_iva:,.0f}"],
            ['', 'TOTAL:', f"${total:,.0f}"],
        ]
        totales_table = Table(totales_data, colWidths=[3.5*inch, 1.8*inch, 1.7*inch])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,1), 'Helvetica'),
            ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,1), 10),
            ('FONTSIZE', (0,2), (-1,2), 13),
            ('TEXTCOLOR', (2,2), (2,2), COLOR_CYAN),
            ('LINEABOVE', (1,2), (-1,2), 1.5, COLOR_CYAN),
            ('TOPPADDING', (0,0), (-1,-1), 4),
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
        story.append(Paragraph("Generado por SalazAnalytics · salazanalytics.com",
                               ParagraphStyle('footer', fontSize=8, textColor=COLOR_GRAY, alignment=TA_CENTER)))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error PDF: {e}")
        return None

def show():
    st.markdown("## Facturacion")

    if "facturas"      not in st.session_state: st.session_state["facturas"] = []
    if "items_factura" not in st.session_state: st.session_state["items_factura"] = []

    tab1, tab2, tab3 = st.tabs(["Nueva Factura", "Historial", "Configuracion Empresa"])

    with tab3:
        st.markdown("### Datos de tu empresa")
        emp_nombre = st.text_input("Nombre o razon social", value=st.session_state.get("emp_nombre",""), key="cfg_nombre")
        emp_nit    = st.text_input("NIT",                   value=st.session_state.get("emp_nit",""),    key="cfg_nit")
        emp_dir    = st.text_input("Direccion",             value=st.session_state.get("emp_dir",""),    key="cfg_dir")
        emp_tel    = st.text_input("Telefono",              value=st.session_state.get("emp_tel",""),    key="cfg_tel")
        emp_email  = st.text_input("Email",                 value=st.session_state.get("emp_email",""),  key="cfg_email")
        emp_ciudad = st.text_input("Ciudad",                value=st.session_state.get("emp_ciudad","Pereira"), key="cfg_ciudad")

        if st.button("Guardar datos empresa", type="primary", key="btn_guardar_empresa"):
            st.session_state["emp_nombre"] = emp_nombre
            st.session_state["emp_nit"]    = emp_nit
            st.session_state["emp_dir"]    = emp_dir
            st.session_state["emp_tel"]    = emp_tel
            st.session_state["emp_email"]  = emp_email
            st.session_state["emp_ciudad"] = emp_ciudad
            st.success("Datos de empresa guardados correctamente.")

    with tab1:
        st.markdown("### Datos del cliente")
        c1, c2 = st.columns(2)
        with c1:
            cli_nombre = st.text_input("Nombre o razon social del cliente", key="cli_nombre")
            cli_nit    = st.text_input("NIT / Cedula del cliente",           key="cli_nit")
        with c2:
            cli_email = st.text_input("Email del cliente",       key="cli_email")
            cli_dir   = st.text_input("Direccion del cliente",   key="cli_dir")

        st.divider()
        st.markdown("### Datos de la factura")
        c1, c2, c3 = st.columns(3)
        with c1:
            num_factura  = st.text_input("Numero de factura", value=f"FV-{datetime.now().strftime('%Y%m%d')}-001", key="num_fac")
        with c2:
            fecha_factura = st.date_input("Fecha", value=date.today(), key="fecha_fac")
        with c3:
            fecha_vence   = st.date_input("Fecha de vencimiento", key="fecha_vence")

        st.divider()
        st.markdown("### Productos y servicios")

        with st.form("form_item", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1.5, 1])
            with c1: desc  = st.text_input("Descripcion")
            with c2: cant  = st.number_input("Cantidad", min_value=1, value=1)
            with c3: valor = st.number_input("Valor unitario", min_value=0, value=0, step=1000)
            with c4: iva   = st.selectbox("IVA", [0, 5, 19])
            submitted = st.form_submit_button("Agregar item")
            if submitted:
                if desc and valor > 0:
                    st.session_state["items_factura"].append({
                        "descripcion": desc,
                        "cantidad": cant,
                        "valor_unitario": valor,
                        "iva": iva
                    })
                    st.success(f"Item agregado: {desc}")
                else:
                    st.warning("Completa la descripcion y el valor.")

        if st.session_state["items_factura"]:
            df_items = pd.DataFrame(st.session_state["items_factura"])
            df_items["Total"] = df_items["cantidad"] * df_items["valor_unitario"] * (1 + df_items["iva"]/100)
            st.dataframe(df_items, use_container_width=True)

            subtotal  = sum(i["cantidad"]*i["valor_unitario"] for i in st.session_state["items_factura"])
            total_iva = sum(i["cantidad"]*i["valor_unitario"]*i["iva"]/100 for i in st.session_state["items_factura"])
            total     = subtotal + total_iva

            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", f"${subtotal:,.0f}")
            c2.metric("IVA",      f"${total_iva:,.0f}")
            c3.metric("Total",    f"${total:,.0f}")

            if st.button("Limpiar items", key="limpiar"):
                st.session_state["items_factura"] = []
                st.rerun()
        else:
            subtotal = total_iva = total = 0

        notas = st.text_area("Notas adicionales (opcional)", key="notas_fac")

        st.divider()
        if st.button("Generar Factura PDF", type="primary", key="btn_generar"):
            if not cli_nombre:
                st.warning("Ingresa el nombre del cliente.")
            elif not st.session_state["items_factura"]:
                st.warning("Agrega al menos un producto o servicio.")
            else:
                factura = {
                    "numero":            num_factura,
                    "fecha":             fecha_factura,
                    "fecha_vence":       fecha_vence,
                    "empresa_nombre":    st.session_state.get("emp_nombre", "SalazAnalytics"),
                    "empresa_nit":       st.session_state.get("emp_nit", ""),
                    "empresa_direccion": st.session_state.get("emp_dir", ""),
                    "empresa_telefono":  st.session_state.get("emp_tel", ""),
                    "empresa_email":     st.session_state.get("emp_email", ""),
                    "cliente_nombre":    cli_nombre,
                    "cliente_nit":       cli_nit,
                    "cliente_email":     cli_email,
                    "cliente_direccion": cli_dir,
                    "items":             st.session_state["items_factura"].copy(),
                    "notas":             notas,
                    "total":             total
                }
                with st.spinner("Generando PDF..."):
                    pdf_bytes = generar_pdf_factura(factura)
                if pdf_bytes:
                    st.session_state["facturas"].append(factura)
                    b64  = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="factura_{num_factura}.pdf" style="display:inline-block;background:#00C2FF;color:#0D1B2A;font-weight:700;padding:.7rem 1.5rem;border-radius:8px;text-decoration:none;font-size:1rem;">Descargar Factura PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success(f"Factura {num_factura} generada.")
                    st.session_state["items_factura"] = []

    with tab2:
        st.markdown("### Historial de facturas")
        if not st.session_state["facturas"]:
            st.info("No hay facturas generadas aun.")
        else:
            for f in reversed(st.session_state["facturas"]):
                with st.expander(f"Factura {f['numero']} — {f['cliente_nombre']} — ${f['total']:,.0f}"):
                    st.write(f"Fecha: {f['fecha']} | Vence: {f['fecha_vence']}")
                    if st.button(f"Regenerar PDF", key=f"regen_{f['numero']}"):
                        pdf_bytes = generar_pdf_factura(f)
                        if pdf_bytes:
                            b64  = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{b64}" download="factura_{f["numero"]}.pdf" style="display:inline-block;background:#00C2FF;color:#0D1B2A;font-weight:700;padding:.5rem 1rem;border-radius:8px;text-decoration:none;">Descargar PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
