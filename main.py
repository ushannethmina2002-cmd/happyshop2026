import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. CORE DATABASE & DYNAMIC SETTINGS ---
class EliteEngine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v5_final.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        # Settings Table (App Name, Logo, Message)
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, 
            announcement TEXT, theme_color TEXT)''')
        # Identity Management
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT)''')
        # Signals Table
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, reason TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        # Default Settings
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'CRYPTO ELITE', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'Welcome to the Institutional Intelligence Portal', '#f0b90b')")
        
        # Admin Account (ඔයාගේ තොරතුරු)
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, role, status) VALUES (?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE'))
        self.conn.commit()

    def get_settings(self):
        return pd.read_sql("SELECT * FROM settings WHERE id=1", self.conn).iloc[0]

engine = EliteEngine()

# --- 2. DYNAMIC UI SYSTEM ---
app_config = engine.get_settings()

st.set_page_config(page_title=app_config['app_name'], layout="wide")

def apply_custom_style():
    color = app_config['theme_color']
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    .stApp {{ background: #080a0c; color: #e1e4e8; font-family: 'Plus Jakarta Sans', sans-serif; }}
    .neon-text {{ color: {color}; text-shadow: 0 0 10px {color}55; font-weight: 800; }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
    }}
    .stButton>button {{
        background: {color} !important; color: black !important; font-weight: 800 !important;
        border-radius: 10px !important; width: 100%; border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MODULES ---
def render_user_dashboard():
    col1, col2 = st.columns([0.1, 0.9])
    with col1: st.image(app_config['logo_url'], width=60)
    with col2: st.markdown(f"<h1 class='neon-text'>{app_config['app_name']}</h1>", unsafe_allow_html=True)
    
    st.info(f"📢 {app_config['announcement']}")
    
    # Signal Display Logic
    signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
    if signals.empty:
        st.write("No active intelligence events.")
    for _, s in signals.iterrows():
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between;">
                <b style="font-size:20px;">{s['pair']}</b>
                <span style="color:{app_config['theme_color']}; font-weight:bold;">{s['type']}</span>
            </div>
            <p style="margin-top:10px; font-size:14px;">{s['reason']}</p>
            <small style="color:#666;">Timeframe: {s['timeframe']} | Confidence: {s['confidence']}</small>
        </div>
        """, unsafe_allow_html=True)

def render_admin_panel():
    st.title("🛡️ Institutional Admin Terminal")
    tab1, tab2, tab3 = st.tabs(["🎨 App Identity", "🎯 Signals", "👥 Users"])

    with tab1:
        st.subheader("Edit App Appearance")
        with st.form("identity_form"):
            new_name = st.text_input("App Name", value=app_config['app_name'])
            new_logo = st.text_input("Logo URL", value=app_config['logo_url'])
            new_msg = st.text_area("Global Announcement", value=app_config['announcement'])
            new_color = st.color_picker("Theme Primary Color", value=app_config['theme_color'])
            
            if st.form_submit_button("Save Global Changes"):
                engine.conn.cursor().execute(
                    "UPDATE settings SET app_name=?, logo_url=?, announcement=?, theme_color=? WHERE id=1",
                    (new_name, new_logo, new_msg, new_color)
                )
                engine.conn.commit()
                st.success("App Identity Updated! Refreshing...")
                st.rerun()

    with tab2:
        st.subheader("Broadcast New Signal")
        with st.form("signal_form"):
            p = st.text_input("Pair"); t = st.selectbox("Type", ["Trend", "Volatility", "Breakout"])
            tf = st.text_input("Timeframe"); c = st.select_slider("Confidence", ["Low", "High"])
            r = st.text_area("Analysis Context")
            if st.form_submit_button("Publish"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, timeframe, confidence, reason, timestamp) VALUES (?,?,?,?,?,?)",
                                            (p, t, tf, c, r, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Signal Live!")

    with tab3:
        st.subheader("User Access Control")
        # මෙතනින් යූසර්ලා ඇඩ් කරන්න සහ මකන්න පුළුවන් (කලින් කෝඩ් එකේ වගේමයි)
        pass

# --- 4. AUTH & NAVIGATION ---
apply_custom_style()

if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    _, login_box, _ = st.columns([1, 1.2, 1])
    with login_box:
        st.image(app_config['logo_url'], width=100)
        st.title(app_config['app_name'])
        u = st.text_input("Email")
        p = st.text_input("Key", type="password")
        if st.button("Access Portal"):
            hashed = hashlib.sha256(p.encode()).hexdigest()
            c = engine.conn.cursor()
            c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hashed))
            res = c.fetchone()
            if res:
                st.session_state.user = {"email": u, "role": res[0]}
                st.rerun()
            else: st.error("Access Denied.")
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    if st.session_state.user['role'] == 'ADMIN':
        mode = st.sidebar.radio("Navigation", ["User View", "Admin Control"])
        if mode == "Admin Control": render_admin_panel()
        else: render_user_dashboard()
    else:
        render_user_dashboard()
