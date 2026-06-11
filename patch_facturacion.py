"""
patch_facturacion.py
Agrega el tab "⚡ Factura Electrónica" a _facturacion.py
Uso: python3 patch_facturacion.py /home/ec2-user/salazanalytics-mvp/_facturacion.py
"""
import sys, shutil

APP = sys.argv[1] if len(sys.argv) > 1 else "_facturacion.py"
shutil.copy2(APP, APP + ".bak_fe")
print(f"Backup: {APP}.bak_fe")

with open(APP, encoding="utf-8") as f:
    content = f.read()

# 1. Agregar tab_fe a la lista de tabs
OLD_TABS = '    tab_agente, tab1, tab_pos, tab2, tab3 = st.tabs([\n        "🤖 Agente IA", "📝 Nueva Factura", "🧾 Tiquete POS", "📂 Historial", "⚙️ Mi Empresa"\n    ])'
NEW_TABS = '    tab_agente, tab1, tab_pos, tab2, tab3, tab_fe = st.tabs([\n        "🤖 Agente IA", "📝 Nueva Factura", "🧾 Tiquete POS", "📂 Historial", "⚙️ Mi Empresa", "⚡ Factura Electrónica"\n    ])'

if OLD_TABS not in content:
    print("ERROR: No encontré la línea de tabs. Verifica el archivo.")
    sys.exit(1)

content = content.replace(OLD_TABS, NEW_TABS)
print("✅ Tab agregado a la lista")

# 2. Contenido del nuevo tab — se agrega antes del último cierre de show()
TAB_FE_CONTENT = '''
    # ══════════════════════════════════════════
    # TAB FACTURA ELECTRÓNICA — Guía y proveedores
    # ══════════════════════════════════════════
    with tab_fe:
        UVT_2026 = 52_374
        UMBRAL_PN = 3_500 * UVT_2026  # ~$183.3M

        st.markdown("### ⚡ Factura Electrónica en Colombia")
        st.markdown(
            "<p style='color:#7B9BB5'>Todo lo que necesitas saber para cumplir con la DIAN "
            "y elegir la mejor opción para tu empresa.</p>",
            unsafe_allow_html=True)

        # ── Calculadora de obligación ──────────────────────────────
        st.markdown("---")
        st.markdown("#### 🔎 ¿Estoy obligado a facturar electrónicamente?")

        tipo_persona = st.radio("Tipo de persona",
            ["Jurídica (empresa, SAS, Ltda., SA...)", "Natural (comerciante independiente)"],
            key="fe_tipo", horizontal=True)

        obligado = False
        if "Jurídica" in tipo_persona:
            obligado = True
            st.markdown(
                f"<div style='background:#00FFB322;border-left:4px solid #00FFB3;"
                f"border-radius:6px;padding:.7rem 1rem;margin:.5rem 0'>"
                f"<p style='color:#00FFB3;font-weight:700;margin:0'>✅ Sí estás obligado</p>"
                f"<p style='color:#E8F4FD;font-size:.85rem;margin:.2rem 0 0'>"
                f"Todas las personas jurídicas deben facturar electrónicamente sin importar "
                f"su tamaño o nivel de ingresos.</p></div>",
                unsafe_allow_html=True)
        else:
            ingresos = st.number_input(
                "Ingresos brutos del año anterior (COP)",
                min_value=0, step=1_000_000, value=0,
                key="fe_ingresos",
                help=f"Umbral 2026: ${UMBRAL_PN:,.0f} (3.500 UVT × ${UVT_2026:,})")
            regimen_simple = st.checkbox("¿Estás inscrito en el Régimen SIMPLE de Tributación?",
                                         key="fe_simple")
            if ingresos >= UMBRAL_PN or regimen_simple:
                obligado = True
                razon = "tus ingresos superan 3.500 UVT" if ingresos >= UMBRAL_PN else "estás en el Régimen SIMPLE"
                st.markdown(
                    f"<div style='background:#00FFB322;border-left:4px solid #00FFB3;"
                    f"border-radius:6px;padding:.7rem 1rem;margin:.5rem 0'>"
                    f"<p style='color:#00FFB3;font-weight:700;margin:0'>✅ Sí estás obligado</p>"
                    f"<p style='color:#E8F4FD;font-size:.85rem;margin:.2rem 0 0'>"
                    f"Porque {razon}. Debes habilitarte ante la DIAN.</p></div>",
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='background:#FFD93D22;border-left:4px solid #FFD93D;"
                    f"border-radius:6px;padding:.7rem 1rem;margin:.5rem 0'>"
                    f"<p style='color:#FFD93D;font-weight:700;margin:0'>⚠️ Aún no estás obligado</p>"
                    f"<p style='color:#E8F4FD;font-size:.85rem;margin:.2rem 0 0'>"
                    f"Pero se recomienda habilitarte voluntariamente — muchos clientes grandes "
                    f"solo aceptan facturas electrónicas. Umbral 2026: "
                    f"${UMBRAL_PN:,.0f}.</p></div>",
                    unsafe_allow_html=True)

        # ── Diferencia factura electrónica vs tiquete POS ─────────
        st.markdown("---")
        st.markdown("#### 📋 Factura electrónica vs. Tiquete POS — ¿cuál necesitas?")
        col1, col2 = st.columns(2)
        col1.markdown(
            "<div style='background:#132030;border:1px solid #1a3a5c;border-radius:8px;"
            "padding:.9rem 1rem;height:100%'>"
            "<p style='color:#00C2FF;font-weight:700;margin:0 0 .5rem'>🧾 Tiquete POS</p>"
            "<p style='color:#E8F4FD;font-size:.84rem;margin:0'>Para ventas al detal donde el "
            "comprador NO necesita deducir IVA ni costos. El módulo de Tiquete POS de esta app "
            "genera estos documentos en formato 80mm. <strong>No requiere habilitación DIAN.</strong></p>"
            "</div>", unsafe_allow_html=True)
        col2.markdown(
            "<div style='background:#132030;border:1px solid #1a3a5c;border-radius:8px;"
            "padding:.9rem 1rem;height:100%'>"
            "<p style='color:#00FFB3;font-weight:700;margin:0 0 .5rem'>⚡ Factura Electrónica</p>"
            "<p style='color:#E8F4FD;font-size:.84rem;margin:0'>Para ventas a empresas o personas "
            "que necesitan soportar costos o deducir IVA. Debe estar validada por la DIAN con CUFE "
            "(código único). <strong>Requiere habilitación y software autorizado.</strong></p>"
            "</div>", unsafe_allow_html=True)

        # ── Pasos para habilitarse ─────────────────────────────────
        st.markdown("---")
        st.markdown("#### 🚀 Cómo habilitarte ante la DIAN — paso a paso")
        pasos = [
            ("1", "Regístrate en el RUT", "Si no tienes RUT activo o necesitas actualizar tu actividad económica, hazlo en dian.gov.co antes de continuar."),
            ("2", "Elige tu modalidad", "Facturador Gratuito DIAN (sin costo, ideal para bajo volumen) o Proveedor Tecnológico Autorizado (Siigo, Alegra, ContaPyme — más automatización)."),
            ("3", "Solicita habilitación", "En el portal DIAN: Transaccional → Factura Electrónica → Habilitar como Facturador Electrónico. Debes enviar facturas de prueba."),
            ("4", "Envía el set de pruebas", "La DIAN te asigna un set de pruebas (aprox. 50 facturas de prueba). Debes generarlas y enviarlas desde tu software elegido."),
            ("5", "Recibe tu habilitación", "Una vez aprobado el set, quedas habilitado y puedes emitir facturas electrónicas reales con validez legal."),
        ]
        for num, titulo, desc in pasos:
            st.markdown(
                f"<div style='background:#132030;border-left:4px solid #00C2FF;"
                f"border-radius:6px;padding:.7rem 1rem;margin-bottom:.5rem;display:flex;gap:.8rem'>"
                f"<span style='color:#00C2FF;font-weight:700;font-size:1.1rem;min-width:24px'>{num}.</span>"
                f"<div><p style='color:#E8F4FD;font-weight:600;margin:0 0 .15rem'>{titulo}</p>"
                f"<p style='color:#7B9BB5;font-size:.83rem;margin:0'>{desc}</p></div></div>",
                unsafe_allow_html=True)

        # ── Comparativo de proveedores ─────────────────────────────
        st.markdown("---")
        st.markdown("#### 🏢 Proveedores tecnológicos autorizados por la DIAN")
        st.markdown(
            "<p style='color:#7B9BB5;font-size:.83rem'>Cuando estés listo para contratar, "
            "estos son los más usados por Pymes colombianas:</p>",
            unsafe_allow_html=True)

        proveedores = [
            {
                "nombre": "Facturador Gratuito DIAN",
                "precio": "Gratis",
                "precio_color": "#00FFB3",
                "ideal": "Empresas con bajo volumen de facturas (hasta ~200/mes)",
                "pros": ["Sin costo", "Directamente en portal DIAN", "Válido legalmente"],
                "contras": ["Proceso manual", "Sin integración contable", "Sin automatización"],
                "link": "https://catalogo-vpfe.dian.gov.co/",
                "link_label": "Ir al portal DIAN",
            },
            {
                "nombre": "Alegra",
                "precio": "Desde $60,000/mes",
                "precio_color": "#FFD93D",
                "ideal": "Pequeñas empresas que quieren facturar + contabilidad básica",
                "pros": ["Fácil de usar", "App móvil", "Integración contable", "API disponible"],
                "contras": ["Costo mensual", "Funciones avanzadas en planes superiores"],
                "link": "https://alegra.com/colombia/",
                "link_label": "Ver planes Alegra",
            },
            {
                "nombre": "Siigo",
                "precio": "Desde $80,000/mes",
                "precio_color": "#FFD93D",
                "ideal": "Empresas medianas con necesidades contables y de nómina",
                "pros": ["Contabilidad completa", "Nómina electrónica", "Amplio soporte"],
                "contras": ["Más costoso", "Curva de aprendizaje mayor"],
                "link": "https://siigo.com/",
                "link_label": "Ver planes Siigo",
            },
            {
                "nombre": "ContaPyme",
                "precio": "Consultar",
                "precio_color": "#7B9BB5",
                "ideal": "Empresas que buscan solución local con soporte en Colombia",
                "pros": ["Soporte local", "Módulos especializados", "Parametrizable"],
                "contras": ["Interfaz más tradicional", "Precio variable según módulos"],
                "link": "https://contapyme.com.co/",
                "link_label": "Ver ContaPyme",
            },
        ]

        cols = st.columns(2)
        for i, p in enumerate(proveedores):
            with cols[i % 2]:
                pros_html  = "".join(f"<li style='color:#00FFB3;font-size:.8rem'>{x}</li>" for x in p["pros"])
                cons_html  = "".join(f"<li style='color:#FF6B6B;font-size:.8rem'>{x}</li>" for x in p["contras"])
                st.markdown(
                    f"<div style='background:#132030;border:1px solid #1a3a5c;border-radius:10px;"
                    f"padding:1rem;margin-bottom:.8rem'>"
                    f"<p style='color:#E8F4FD;font-weight:700;font-size:.95rem;margin:0 0 .2rem'>{p['nombre']}</p>"
                    f"<p style='color:{p['precio_color']};font-weight:600;font-size:.9rem;margin:0 0 .4rem'>{p['precio']}</p>"
                    f"<p style='color:#7B9BB5;font-size:.78rem;margin:0 0 .5rem'>{p['ideal']}</p>"
                    f"<ul style='margin:.3rem 0;padding-left:1rem'>{pros_html}</ul>"
                    f"<ul style='margin:.3rem 0;padding-left:1rem'>{cons_html}</ul>"
                    f"<a href='{p['link']}' target='_blank' style='display:inline-block;margin-top:.5rem;"
                    f"background:#00C2FF22;color:#00C2FF;border:1px solid #00C2FF55;border-radius:20px;"
                    f"padding:3px 14px;font-size:.78rem;text-decoration:none;font-weight:600'>"
                    f"🔗 {p['link_label']}</a>"
                    f"</div>",
                    unsafe_allow_html=True)

        # ── Nota final ─────────────────────────────────────────────
        st.markdown(
            "<div style='background:#132030;border-left:4px solid #00C2FF;"
            "border-radius:8px;padding:.9rem 1.2rem;margin-top:.5rem'>"
            "<p style='color:#00C2FF;font-weight:600;margin:0 0 .2rem'>"
            "💡 ¿Necesitas ayuda para habilitarte?</p>"
            "<p style='color:#7B9BB5;font-size:.84rem;margin:0'>"
            "En SalazAnalytics te orientamos en el proceso de habilitación ante la DIAN, "
            "elección del proveedor tecnológico y configuración inicial de la factura electrónica "
            "según tu actividad económica.</p></div>",
            unsafe_allow_html=True)
'''

# Insertar antes del último cierre de show() — buscamos el último "with tab2:" o "with tab3:"
# Insertamos justo antes del final de la función show
INSERT_BEFORE = "    # ══════════════════════════════════════════\n    # TAB HISTORIAL"
if INSERT_BEFORE not in content:
    # fallback: buscar la última aparición de "with tab2:"
    INSERT_BEFORE = "    with tab2:"

idx = content.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: no encontré punto de inserción. Revisar manualmente.")
    sys.exit(1)

content = content[:idx] + TAB_FE_CONTENT + "\n" + content[idx:]
print("✅ Contenido del tab insertado")

with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ {APP} actualizado correctamente.")
print(f"   Backup en: {APP}.bak_fe")

# Verificación de sintaxis
import ast
try:
    ast.parse(content)
    print("✅ Sintaxis Python correcta")
except SyntaxError as e:
    print(f"❌ Error de sintaxis: {e}")
