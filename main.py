import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. CORE SECURITY & DATABASE ---
class EnterpriseVault:
    def __init__(self):
        # Database name for the final build
        self.conn = sqlite3.connect('vip_intel_core.db', check_same_thread=False)
        self.init_db()
        self.ensure_admin()

    def init_db(self):
        c = self.conn.cursor()
        # Identity Management (Users)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, expiry TEXT)''')
        # Institutional Signals (Read-only for users)
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, source TEXT, 
            reason TEXT, timestamp TEXT, status TEXT)''')
        self.conn.commit()

    def hash_pw(self, password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def ensure_admin(self):
        """Pre-seeding your admin account"""
        c = self.conn.cursor()
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = self.hash_pw("192040090") 
            c.execute("INSERT INTO users (username, password, role, status, expiry) VALUES (?,?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE', 'NEVER'))
            self.conn.commit()

    def verify_auth(self, u, p):
        c = self.conn.cursor()
        h_p = self.hash_pw(p)
        c.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, h_p))
        return c.fetchone()

vault = EnterpriseVault()

# --- 2. PREMIUM UI/UX SYSTEM ---
st.set_page_config(page_title="CRYPTO ELITE | VIP", layout="wide", initial_sidebar_state="expanded")

def apply_institutional_design():
    # Real Crypto Icons for Floating Effect
    logos = ["https://cryptologos.cc/logos/bitcoin-btc-logo.png", "https://cryptologos.cc/logos/ethereum-eth-logo.png"]
    bg_html = "".join([f'<img src="{random.choice(logos)}" class="bg-icon" style="left:{random.randint(5,95)}%; animation-delay:{random.randint(0,10)}s;">' for _ in range(10)])

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    .stApp {{ background: #080a0c; color: #e1e4e8; font-family: 'Plus Jakarta Sans', sans-serif; }}
    
    /* Background Animation */
    .bg-icon {{ position: fixed; bottom: -100px; width: 40px; opacity: 0.05; animation: floatUp 25s linear infinite; z-index:-1; }}
    @keyframes floatUp {{ 0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }} 10% {{ opacity: 0.08; }} 100% {{ transform: translateY(-120vh) rotate(360deg); opacity: 0; }} }}

    /* Professional Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px; backdrop-filter: blur(15px); margin-bottom: 20px;
    }}
    .neon-gold {{ color: #f0b90b; text-shadow: 0 0 10px rgba(240, 185, 11, 0.3); font-weight: 800; }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #f0b90b, #ffca28) !important;
        color: black !important; font-weight: 800 !important; border-radius: 12px !important; border: none !important;
    }}
    </style>
    <div class="bg-animation">{bg_html}</div>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD MODULES ---
def render_signals():
    st.markdown("<h2 class='neon-gold'>🎯 Institutional Signal Stream</h2>", unsafe_allow_html=True)
    st.caption("Real-time market awareness events. This is for educational decision support only.")
    
    signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", vault.conn)
    if signals.empty:
        st.info("Market Radar: Scanning for institutional liquidity. No active events.")
        return

    for _, s in signals.iterrows():
        color = "#00ff88" if "Bullish" in s['type'] or "Trend" in s['type'] else "#f0b90b"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:22px; font-weight:800; color:white;">{s['pair']}</span>
                <span style="background:rgba(240,185,11,0.1); color:#f0b90b; padding:4px 15px; border-radius:50px; font-size:11px; font-weight:800; border:1px solid #f0b90b55;">{s['type']}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:15px; margin:20px 0; text-align:center;">
                <div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:12px;"><small>TIMEFRAME</small><br><b>{s['timeframe']}</b></div>
                <div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:12px;"><small>CONFIDENCE</small><br><b>{s['confidence']}</b></div>
                <div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:12px;"><small>SOURCE</small><br><b>{s['source']}</b></div>
            </div>
            <div style="background:rgba(240,185,11,0.03); padding:15px; border-radius:12px; border-left:4px solid #f0b90b;">
                <small style="color:#f0b90b; font-weight:800;">INTELLIGENCE CONTEXT</small>
                <p style="margin-top:5px; font-size:14px; line-height:1.6;">{s['reason']}</p>
            </div>
            <p style="font-size:10px; color:#555; margin-top:15px; text-align:right;">ID: #{s['id']} | Published at {s['timestamp']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 4. ADMIN CONTROL ---
def render_admin():
    st.markdown("<h2 class='neon-gold'>🛡️ Command Center</h2>", unsafe_allow_html=True)
    menu = st.sidebar.selectbox("Sub-Menu", ["Broadcast Signal", "VIP User Management"])

    if menu == "Broadcast Signal":
        with st.form("broadcast_form"):
            p = st.text_input("Asset Pair (e.g. BTC/USDT)")
            t = st.selectbox("Signal Category", ["Trend Detection", "Volatility Alert", "Liquidity Gap", "Institutional Move"])
            col1, col2 = st.columns(2)
            tf = col1.text_input("Timeframe (e.g. 4H, Daily)")
            conf = col2.select_slider("Confidence", ["LOW", "MEDIUM", "HIGH", "INSTITUTIONAL"])
            reason = st.text_area("Detailed Market Analysis & Why this appeared")
            if st.form_submit_button("Publish To VIP Feed"):
                vault.conn.cursor().execute("INSERT INTO signals (pair, type, timeframe, confidence, source, reason, timestamp, status) VALUES (?,?,?,?,?,?,?,?)",
                                            (p, t, tf, conf, "VIP Core Desk", reason, datetime.now().strftime("%H:%M"), "ACTIVE"))
                vault.conn.commit(); st.success("Broadcast Live!")

    elif menu == "VIP User Management":
        st.subheader("Add New VIP Member")
        with st.form("add_vip"):
            u = st.text_input("Member Email")
            p = st.text_input("Set Security Key", type="password")
            if st.form_submit_button("Grant VIP Access"):
                try:
                    h = vault.hash_pw(p)
                    vault.conn.cursor().execute("INSERT INTO users (username, password, role, status, expiry) VALUES (?,?,?,?,?)",
                                                (u, h, 'USER', 'ACTIVE', '30 Days'))
                    vault.conn.commit(); st.success(f"VIP Access enabled for {u}")
                except: st.error("This member is already registered.")

# --- 5. LOGIC & AUTH ---
apply_institutional_design()

if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; font-weight:800; font-size:45px;'>ELITE PORTAL</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#848e9c; margin-bottom:40px;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            u = st.text_input("Institutional Email")
            p = st.text_input("Security Password", type="password")
            if st.button("AUTHENTICATE"):
                res = vault.verify_auth(u, p)
                if res:
                    st.session_state.auth = {"user": u, "role": res[0]}
                    st.rerun()
                else: st.error("Access Denied: Invalid Credentials")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        st.markdown(f"### 🔐 SESSION ACTIVE")
        st.markdown(f"**Account:** `{st.session_state.auth['user']}`")
        st.markdown(f"**Level:** <span class='neon-gold'>{st.session_state.auth['role']}</span>", unsafe_allow_html=True)
        st.divider()
        nav = st.radio("Intelligence Modules", ["Signal Radar", "Market Academy"])
        if st.session_state.auth['role'] == 'ADMIN':
            st.divider()
            if st.button("🛠️ OPEN COMMAND CENTER"): st.session_state.mode = "ADMIN"
            if st.button("🔙 EXIT COMMAND CENTER"): st.session_state.mode = "USER"
        
        if st.button("LOGOUT"): st.session_state.auth = None; st.rerun()

    if getattr(st.session_state, 'mode', 'USER') == "ADMIN":
        render_admin()
    else:
        if nav == "Signal Radar": render_signals()
        else: st.info("Academy module coming soon: Professional Risk Management Course.")
