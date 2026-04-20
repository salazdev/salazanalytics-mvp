import streamlit as st
import hashlib

st.set_page_config(
    page_title="SalazAnalytics",
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
div[data-testid="metric-container"] { background: #132030; border: 1px solid #1a3a5c; border-radius: 12px; padding: 1rem; }
div[data-testid="metric-container"] label { color: #7B9BB5 !important; font-size: 0.8rem; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #00C2FF !important; font-size: 1.6rem; font-weight: 700; }
.stButton > button { background: #00C2FF; color: #0D1B2A; font-weight: 600; border: none; border-radius: 8px; padding: 0.6rem 1.4rem; transition: all 0.2s; }
.stButton > button:hover { background: #33CDFF; transform: translateY(-1px); }
.stTabs [data-baseweb="tab-list"] { background: #132030; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #7B9BB5; border-radius: 6px; }
.stTabs [d
