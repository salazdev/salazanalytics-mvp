import streamlit as st
import hashlib
from pathlib import Path
import importlib.util
import sys
import base64

st.set_page_config(
    page_title="SalazAnalytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

css = """
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0D1B2A; color: #E8F4FD; }
section[data-testid="stSidebar"] { background: #0a1520; border-right: 1px solid #1a3a5c; }
div[data-testid="metric-container"] { background: #132030; border: 1px solid #1a3a5c; border-radius: 12px; padding: 1rem; }
div[data-testid="metric-container"] label { color: #7B9BB5 !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #00C2FF !important; font-size: 1.6rem; font-weight: 700; }
.stButton > button { background: #00C2FF; color: #0D1B2A; font-weight: 600; border: none; border-radius: 8px; padding: 0.6rem 1.4rem; }
.stTabs [data-baseweb="tab-list"] { background: #132030; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #7B9BB5; border-radius: 6px; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: #00C2FF; color: #0D1B2A; font-weight: 600; }
div[data-testid="stFileUploader"] { background: #132030; border: 2px dashed #1a3a5c; border-radius: 12px; padding: 1rem; }
.chat-user { background: #1a3a5c; border-radius: 12px 12px 4px 12px; padding: 10px 14px; margin: 6px 0; }
.chat-ai { background: #132030; border-left: 3px solid #00C2FF; border-radius: 4px 12px 12px 12px; padding: 10px 14px; margin: 6px 0; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def load_db():
    return load_module("db", Path(__file__).parent / "_db.py")

def mostrar_logo(width=220):
    logo_path = Path(__file__).parent / "logo-salazanalytics.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{data}" '
            f'style="width:{width}px;display:block;margin:0 auto;">',
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h2 style='color:#00C2FF;text-align:center;'>SalazAnalytics</h2>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOGIN / REGISTRO
# ─────────────────────────────────────────────

def pantalla_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        mostrar_logo(200)
        st.markdown("<br>", unsafe_allow_html=True)
        tab_in, tab_reg = st.tabs(["Ingresar", "Registrar empresa"])

        with tab_in:
            st.markdown("<p style='color:#7B9BB5;font-size:.88rem;text-align:center'>"
                        "Accede con el correo de tu empresa.</p>", unsafe_allow_html=True)
            email = st.text_input("Correo", key="li_email", placeholder="empresa@correo.com")
            pwd   = st.text_input("Contraseña", type="password", key="li_pwd")
            if st.button("Ingresar", type="primary", use_container_width=True, key="btn_li"):
                if email and pwd:
                    db  = load_db()
                    emp = db.empresa_login(email, pwd)
                    if emp:
                        st.session_state.update({"logged_in": True, "empresa": emp, "nit": emp["nit"]})
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos.")
                else:
                    st.warning("Completa los campos.")

            with st.expander("Acceso interno SalazAnalytics"):
                u = st.text_input("Usuario", key="adm_u")
                p = st.text_input("Contraseña", type="password", key="adm_p")
                INTERNOS = {
                    "admin": hashlib.sha256("salaz2025".encode()).hexdigest(),
                    "demo":  hashlib.sha256("demo123".encode()).hexdigest(),
                }
                if st.button("Entrar", key="btn_adm"):
                    if u in INTERNOS and INTERNOS[u] == hashlib.sha256(p.encode()).hexdigest():
                        emp = {"nit": "SALAZ-ADMIN", "nombre": "SalazAnalytics",
                               "email": "admin@salazanalytics.com", "plan": "admin",
                               "ciudad": "Pereira", "actividad": "Servicios profesionales y consultoría",
                               "regimen": "SIMPLE", "direccion": "", "telefono": ""}
                        st.session_state.update({"logged_in": True, "empresa": emp, "nit": emp["nit"]})
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")

        with tab_reg:
            st.markdown("<p style='color:#7B9BB5;font-size:.88rem;text-align:center'>"
                        "30 días gratis. Sin tarjeta de crédito.</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                rn = st.text_input("Razón social", key="rn")
                ri = st.text_input("NIT", key="ri", placeholder="900123456")
                rc = st.text_input("Ciudad", key="rc", value="Pereira")
            with c2:
                re = st.text_input("Correo", key="re")
                rp = st.text_input("Contraseña", type="password", key="rp")
                rp2= st.text_input("Confirmar contraseña", type="password", key="rp2")
            if st.button("Crear cuenta gratuita", type="primary", use_container_width=True, key="btn_reg"):
                if not all([rn, ri, re, rp]):
                    st.warning("Completa todos los campos.")
                elif rp != rp2:
                    st.error("Las contraseñas no coinciden.")
                elif len(rp) < 6:
                    st.warning("Mínimo 6 caracteres.")
                else:
                    db = load_db()
                    if db.empresa_crear(ri, rn, re, rp, ciudad=rc):
                        st.success("Cuenta creada. Ingresa con tu correo y contraseña.")
                    else:
                        st.error("Ya existe una cuenta con ese NIT o correo.")

        st.markdown("<p style='color:#7B9BB5;font-size:.75rem;text-align:center;margin-top:1rem'>"
                    "<a href='https://salazanalytics.com/contacto' target='_blank' "
                    "style='color:#00C2FF;text-decoration:none;'>¿Necesitas ayuda?</a></p>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MI EMPRESA
# ─────────────────────────────────────────────

def pantalla_mi_empresa():
    empresa = st.session_state.get("empresa", {})
    nit     = st.session_state.get("nit", "")
    st.markdown("## ⚙️ Mi Empresa")
    st.markdown("<p style='color:#7B9BB5'>Configura los datos que aparecen en tus facturas "
                "y cálculos tributarios.</p>", unsafe_allow_html=True)

    tab_d, tab_p = st.tabs(["Datos", "Contraseña"])
    ACTIVIDADES = ["Servicios profesionales y consultoría","Actividades comerciales",
                   "Actividades industriales","Servicios financieros",
                   "Restaurantes y hoteles","Transporte","Construcción","Salud","Educación"]

    with tab_d:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nombre / razón social", value=empresa.get("nombre",""), key="me_nombre")
            st.text_input("NIT", value=nit, disabled=True)
            st.text_input("Dirección", value=empresa.get("direccion",""), key="me_dir")
            st.text_input("Ciudad", value=empresa.get("ciudad","Pereira"), key="me_ciudad")
        with c2:
            st.text_input("Correo", value=empresa.get("email",""), key="me_email")
            st.text_input("Teléfono", value=empresa.get("telefono",""), key="me_tel")
            regs = ["SIMPLE","Ordinario","Persona Natural"]
            st.selectbox("Régimen", regs,
                         index=regs.index(empresa.get("regimen","SIMPLE")), key="me_regimen")
            idx = ACTIVIDADES.index(empresa.get("actividad",ACTIVIDADES[0])) \
                  if empresa.get("actividad") in ACTIVIDADES else 0
            st.selectbox("Actividad principal", ACTIVIDADES, index=idx, key="me_actividad")

        if st.button("💾 Guardar", type="primary", key="btn_me_save"):
            db = load_db()
            db.empresa_actualizar(nit,
                nombre=st.session_state["me_nombre"],
                email=st.session_state["me_email"],
                ciudad=st.session_state["me_ciudad"],
                direccion=st.session_state["me_dir"],
                telefono=st.session_state["me_tel"],
                regimen=st.session_state["me_regimen"],
                actividad=st.session_state["me_actividad"],
            )
            emp_upd = db.empresa_get(nit)
            if emp_upd:
                st.session_state["empresa"] = emp_upd
            st.success("✅ Datos guardados.")

    with tab_p:
        pa = st.text_input("Contraseña actual", type="password", key="pa")
        pn = st.text_input("Nueva contraseña",  type="password", key="pn")
        pc = st.text_input("Confirmar nueva",   type="password", key="pc")
        if st.button("🔒 Cambiar contraseña", type="primary", key="btn_chpass"):
            if not all([pa, pn, pc]):
                st.warning("Completa todos los campos.")
            elif pn != pc:
                st.error("Las contraseñas nuevas no coinciden.")
            elif len(pn) < 6:
                st.warning("Mínimo 6 caracteres.")
            else:
                db = load_db()
                if db.empresa_login(empresa.get("email",""), pa):
                    db.empresa_cambiar_password(nit, pn)
                    st.success("✅ Contraseña actualizada.")
                else:
                    st.error("La contraseña actual no es correcta.")

# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────

def app_principal():
    base    = Path(__file__).parent
    empresa = st.session_state.get("empresa", {})
    nit     = st.session_state.get("nit", "")

    with st.sidebar:
        mostrar_logo(180)
        st.markdown(f"""
        <div style="background:#0a1520;border:1px solid #1a3a5c;border-radius:8px;
                    padding:.7rem 1rem;margin:.8rem 0;text-align:center;">
            <p style="color:#7B9BB5;font-size:.72rem;margin:0;">Empresa</p>
            <p style="color:#00C2FF;font-weight:600;font-size:.85rem;margin:0;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                {empresa.get('nombre','SalazAnalytics')}</p>
            <p style="color:#7B2FBE;font-size:.7rem;margin:0;">
                NIT {nit} · {empresa.get('plan','básico').upper()}</p>
        </div>""", unsafe_allow_html=True)

        st.divider()

        page = st.radio("Menu", [
            "🏠 Inicio", "⚖️ Revisoria y Cumplimiento", "🔮 Mirofish Predictor",
            "📊 Dashboards Financieros", "📗 Auditoria de Excel",
            "💬 Consultor Contable IA", "⚙️ Automatizacion n8n",
            "🔍 Anomalias", "📑 Exportar", "🧾 Facturacion",
            "📒 Contabilidad", "🏢 Mi Empresa",
        ], label_visibility="collapsed", key="pagina_actual")

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.markdown("<p style='color:#7B9BB5;font-size:.72rem;text-align:center'>"
                    "salazanalytics.com</p>", unsafe_allow_html=True)

    if   "Inicio"       in page: load_module("home",          base/"_home.py").show()
    elif "Revisor"      in page: load_module("pdf_ia",         base/"_pdf_ia.py").show()
    elif "Mirofish"     in page: load_module("ml_prediccion",  base/"_ml_prediccion.py").show()
    elif "Dashboards"   in page: load_module("dashboards",     base/"_dashboards.py").show()
    elif "Excel"        in page: load_module("excel_ia",       base/"_excel_ia.py").show()
    elif "Consultor"    in page: load_module("chat_datos",     base/"_chat_datos.py").show()
    elif "Anomalias"    in page: load_module("anomalias",      base/"_anomalias.py").show()
    elif "Exportar"     in page: load_module("exportar",       base/"_exportar.py").show()
    elif "Factura"      in page: load_module("facturacion",    base/"_facturacion.py").show()
    elif "Contabilidad" in page: load_module("contabilidad",   base/"_contabilidad.py").show()
    elif "Mi Empresa"   in page: pantalla_mi_empresa()

if not st.session_state.get("logged_in"):
    pantalla_login()
else:
    app_principal()
