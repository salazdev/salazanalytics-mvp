import streamlit as st
import hashlib
from pathlib import Path
import importlib.util
import sys
import base64

LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="260" height="70" viewBox="0 0 260 70">
  <line x1="10" y1="35" x2="25" y2="35" stroke="#1a3a5c" stroke-width="1.5"/>
  <polyline points="25,35 30,35 34,18 39,52 44,28 49,42 53,35 70,35" fill="none" stroke="#00C2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="34" cy="18" r="3" fill="#7B2FBE"/>
  <circle cx="44" cy="28" r="2" fill="#00C2FF"/>
  <line x1="70" y1="35" x2="80" y2="35" stroke="#1a3a5c" stroke-width="1.5"/>
  <text x="88" y="41" fill="#E8F4FD" font-family="Segoe UI,Arial,sans-serif" font-size="24" font-weight="700" letter-spacing="-0.5">Salaz<tspan fill="#00C2FF">Analytics</tspan></text>
  <text x="89" y="55" fill="#7B9BB5" font-family="Segoe UI,Arial,sans-serif" font-size="9" letter-spacing="4">DATA  INTELLIGENCE</text>
</svg>'''

LOGO_B64 = base64.b64encode(LOGO_SVG.encode()).decode()
LOGO_HTML = f'<img src="data:image/svg+xml;base64,{LOGO_B64}" style="width:100%;max-width:220px;margin:0 auto;display:block;">'

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
div[data-testid="stFileUploader"] { background: #1
