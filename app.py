import streamlit as st
import hashlib
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import sys
sys.path.insert(0, ".")

st.set_page_config(
    page_title="SalazAnalytics — Plataforma de Análisis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0D1B2A; color: #E8F4FD; }
section[data-testid="stSidebar"] { background: #0a1520; border-right: 1px solid #1a3a5c; }
.sidebar-logo { text-align: center; padding: 1.5rem 0 1rem; }
.sidebar-logo h2 { color: #00C2FF; font-size: 1.4rem; font-weight: 700; margin: 0; }
.sidebar-logo p  { color: #7B9BB5; font-size: 0.75rem; margin: 0; }
div[data-testid="metric-container"] { background: #132030; border: 1px solid #1a3a5c; border-radius: 12px; padding: 1rem; }
div[data-testid="metric-container"] label { color: #7B9BB5 !important; font-size: 0.8rem; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #00C2FF !important; font-size: 1.6rem; font-weight: 700; }
.stButton > button { background: #00C2FF; color: #0D1B2A; font-weight: 600; border: none; border-radius: 8px; padding: 0.6rem 1.4rem; transition: all 0.2s; }
.stButton > button:hover { background: #33CDFF; transform: translateY(-1px); }
.stTabs [data-baseweb="tab-list"] { background: #132030; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #7B9BB5; border-radius: 6px; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: #00C2FF; color: #0D1B2A; font-weight: 600; }
div[data-testid="stFileUploader"] { background: #132030; border: 2px dashed #1a3a5c; border-radius: 12px; padding: 1rem; }
div[data-testid="stFileUploader"]:hover { border-color: #00C2FF; }
details { background: #132030; border: 1px solid #1a3a5c; border-radius: 8px; }
.chat-user { background: #1a3a5c; border-radius: 12px 12px 4px 12px; padding: 10px 14px; margin: 6px 0; }
.chat-ai   { background: #132030; border-left: 3px solid #00C2FF; border-radius: 4px 12px 12px 12px; padding: 10px 14px; margin: 6px 0; }
.login-box { max-width: 420px; margin: 4rem auto; background: #132030; border: 1px solid #1a3a5c; border-radius: 16px; padding: 2.5rem; text-align: center; }
.login-box h1 { color: #00C2FF; font-size: 1.8rem; margin-bottom: .3rem; }
.login-box p  { color: #7B9BB5; font-size: .9rem; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

USUARIOS = {
    "admin": hashlib.sha256("salaz2025".encode()).hexdigest(),
    "demo":  hashlib.sha256("demo123".encode()).hexdigest(),
}

ROLES = {
    "admin": "Administrador",
    "demo":  "Cliente Demo",
}

def check_password(usuario: str, password: str) -> bool:
    if usuario not in USUARIOS:
        return False
    return USUARIOS[usuario] == hashlib.sha256(password.encode()).hexdigest()

def pantalla_login():
    st.markdown("""
    <div class="login-box">
        <h1>📊 SalazAnalytics</h1>
        <p>Ingresa tus credenciales para acceder a la plataforma</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
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
                   style="color:#00C2FF;text-decoration:none;">
                   Solicita acceso aquí
                </a>
            </p>
        </div>
        """, unsafe_allow_html=True)

def app_principal():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>📊 SalazAnalytics</h2>
            <p>Plataforma de Análisis con IA</p>
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

        page = st.radio(
            "Módulos",
            [
                "🏠  Inicio",
                "📗  Análisis de Excel",
                "📄  Análisis de PDF",
                "💬  Chat con tus datos",
                "📈  Dashboards",
                "🤖  Predicción con ML",
                "🔍  Detección de anomalías",
                "📑  Exportar Reporte",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("<p style='color:#7B9BB5;font-size:.75rem;text-align:center'>salazanalytics.com</p>",
                    unsafe_allow_html=True)

    if   "Inicio"      in page: from pages import home;          home.show()
    elif "Excel"       in page: from pages import excel_ia;      excel_ia.show()
    elif "PDF"         in page: from pages import pdf_ia;        pdf_ia.show()
    elif "Chat"        in page: from pages import chat_datos;    chat_datos.show()
    elif "Dashboards"  in page: from pages import dashboards;    dashboards.show()
    elif "Predicción"  in page: from pages import ml_prediccion; ml_prediccion.show()
    elif "anomalías"   in page: from pages import anomalias;     anomalias.show()
    elif "Exportar"    in page: from pages import exportar;      exportar.show()

if not st.session_state.get("logged_in"):
    pantalla_login()
else:
    app_principal()
