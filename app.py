import streamlit as st
import hashlib
from pathlib import Path
import importlib.util
import sys

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

USUARIOS = {
    "admin": hashlib.sha256("salaz2025".encode()).hexdigest(),
    "demo":  hashlib.sha256("demo123".encode()).hexdigest(),
}

ROLES = {
    "admin": "Administrador",
    "demo":  "Cliente Demo",
}

def check_password(usuario, password):
    if usuario not in USUARIOS:
        return False
    return USUARIOS[usuario] == hashlib.sha256(password.encode()).hexdigest()

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def pantalla_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:#132030;border:1px solid #1a3a5c;border-radius:16px;
                    padding:2.5rem;text-align:center;margin-bottom:2rem;">
            <h1 style="color:#00C2FF;font-size:1.8rem;margin-bottom:.3rem;">
                📊 SalazAnalytics</h1>
            <p style="color:#7B9BB5;font-size:.9rem;margin:0;">
                Ingresa tus credenciales para acceder</p>
        </div>
        """, unsafe_allow_html=True)
        usuario = st.text_input("👤 Usuario", placeholder="Tu usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Tu contraseña")
        if st.button("Ingresar a la plataforma", type="primary", use_container_width=True):
            if check_password(usuario, password):
                st.session_state["logged_in"] = True
                st.session_state["usuario"] = usuario
                st.session_state["rol"] = ROLES.get(usuario, "Cliente")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
        st.markdown("""
        <div style="text-align:center;margin-top:1rem;">
            <p style="color:#7B9BB5;font-size:.8rem;">
                ¿No tienes acceso?
                <a href="https://salazanalytics.com/contacto" target="_blank"
                   style="color:#00C2FF;text-decoration:none;">Solicita acceso aquí</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

def app_principal():
    base = Path(__file__).parent

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0 1rem;">
            <h2 style="color:#00C2FF;font-size:1.4rem;font-weight:700;margin:0;">
                📊 SalazAnalytics</h2>
            <p style="color:#7B9BB5;font-size:0.75rem;margin:0;">
                Plataforma de Análisis con IA</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#0a1520;border:1px solid #1a3a5c;border-radius:8px;
                    padding:.7rem 1rem;margin-bottom:1rem;text-align:center;">
            <p style="color:#7B9BB5;font-size:.75rem;margin:0;">Conectado como</p>
            <p style="color:#00C2FF;font-weight:600;font-size:.9rem;margin:0;">
                {st.session_state.get('usuario','')}</p>
            <p style="color:#7B2FBE;font-size:.72rem;margin:0;">
                {st.session_state.get('rol','')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        opciones = [
            "🏠 Inicio",
            "📗 Excel con IA",
            "📄 PDF con IA",
            "💬 Chat con datos",
            "📈 Dashboards",
            "🤖 Predicción ML",
            "🔍 Anomalías",
            "📑 Exportar",
        ]

        if "pagina_actual" not in st.session_state:
            st.session_state["pagina_actual"] = "🏠 Inicio"

        for opcion in opciones:
            if st.button(opcion, use_container_width=True, key=f"nav_{opcion}"):
                st.session_state["pagina_actual"] = opcion
                st.rerun()

        st.divider()

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown(
            "<p style='color:#7B9BB5;font-size:.75rem;text-align:center'>salazanalytics.com</p>",
            unsafe_allow_html=True)

    page = st.session_state.get("pagina_actual", "🏠 Inicio")
    
    if   "Inicio"     in page: load_module("home", base/"_home.py").show()
    elif "Excel"      in page: load_module("excel_ia", base/"_excel_ia.py").show()
    elif "PDF"        in page: load_module("pdf_ia", base/"_pdf_ia.py").show()
    elif "Chat"       in page: load_module("chat_datos", base/"_chat_datos.py").show()
    elif "Dashboards" in page: load_module("dashboards", base/"_dashboards.py").show()
    elif "Predicción" in page: load_module("ml_prediccion", base/"_ml_prediccion.py").show()
    elif "Anomalías"  in page: load_module("anomalias", base/"_anomalias.py").show()
    elif "Exportar"   in page: load_module("exportar", base/"_exportar.py").show()

if not st.session_state.get("logged_in"):
    pantalla_login()
else:
    app_principal()
