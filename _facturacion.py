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
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_LIGHT, color
