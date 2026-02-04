import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. SECURE ARCHITECTURE ---
class IntelVault:
    def __init__(self):
        # Database එකක් අලුතින්ම හදනවා (intel_v4.db)
        self.conn = sqlite3.connect('intel_v4.db', check_same_thread=False)
        self.init_db()
        self.ensure_admin()

    def init_db(self):
        c = self.conn.cursor()
        # Identity Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT)''')
        # Professional Signal Table (New Structure)
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, source TEXT, 
            reason TEXT, timestamp TEXT, status TEXT)''')
        self.conn.commit()

    def hash_pw(self, password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def ensure_admin(self):
        """ඔයාගේ Email එක ඇඩ්මින් විදිහට Set කිරීම"""
        c = self.conn.cursor()
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            # ඔයා Screenshot එකේ පාවිච්චි කරපු Password එක: 192040090
            hashed = self.hash_pw("192040090") 
            c.execute("INSERT INTO users (username, password, role, status) VALUES (?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE'))
            self.conn.commit()

    def verify_auth(self, u, p):
        c = self.conn.cursor()
        h_p = self.hash_pw(p)
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, h_p))
        res = c.fetchone()
        return res[0] if res else None

vault = IntelVault()

# --- 2. PREMIUM UX SYSTEM ---
st.set_page_config(page_title="CRYPTO ELITE", layout="wide")

def apply_styling():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    .stApp { background-color: #0b0e11; color: #e1e4e8; font-family: 'Inter', sans-serif; }
    
    /* Institutional Signal Card */
    .intel-card {
        background: #181a20; border: 1px solid #2b2f36;
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
        transition: 0.3s;
    }
    .intel-card:hover { border-color: #f0b90b; background: #1e2126; }
    .status-tag { 
        padding: 4px 12px; border-radius: 4px; font-size: 10px; 
        font-weight: bold; background: #2b2f36; color: #f0b90b; 
    }
    .disclaimer { font-size: 11px; color: #848e9c; border-top: 1px solid #2b2f36; margin-top: 15px; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MODULES ---
def signal_stream():
    st.markdown("### 📡 Intelligence Awareness Stream")
    st.caption("Real-time data events from institutional desks. Educational use only.")
    
    # Database එකෙන් සිග්නල් කියවීම
    signals = pd.read_sql("SELECT * FROM signals WHERE status='ACTIVE' ORDER BY id DESC", vault.conn)
    
    if signals.empty:
        st.info("Market Awareness: No significant events detected at this moment.")
        return

    for _, s in signals.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="intel-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:18px; font-weight:600;">{s['pair']}</span>
                    <span class="status-tag">{s['type']}</span>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin: 15px 0;">
                    <div><small style="color:#848e9c;">TIMEFRAME</small><br><b>{s['timeframe']}</b></div>
                    <div><small style="color:#848e9c;">CONFIDENCE</small><br><b>{s['confidence']}</b></div>
                    <div><small style="color:#848e9c;">SOURCE</small><br><b>{s['source']}</b></div>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:6px;">
                    <small style="color:#f0b90b;">CONTEXT & ANALYSIS</small>
                    <p style="font-size:14px; margin:5px 0;">{s['reason']}</p>
                </div>
                <div class="disclaimer">
                    ⚠️ <b>NOT FINANCIAL ADVICE:</b> This event data is for educational awareness.
                </div>
            </div>
            """, unsafe_allow_html=True)

def admin_terminal():
    st.title("🛡️ Intelligence Control Tower")
    tab1, tab2 = st.tabs(["Publish Event", "Manage Personnel"])
    
    with tab1:
        with st.form("publish_signal"):
            col1, col2 = st.columns(2)
            pair = col1.text_input("Market/Pair (e.g. BTC/USDT)")
            sig_type = col2.selectbox("Event Type", ["Trend Detection", "Volatility Spike", "Liquidity Shift", "Narrative Change"])
            
            col3, col4 = st.columns(2)
            tf = col3.selectbox("Observation Scale", ["Intraday", "Short-term", "Mid-term", "Macro"])
            conf = col4.select_slider("Confidence Index", ["Low", "Moderate", "High", "Institutional"])
            
            source = st.text_input("Data Source", value="Global Intelligence Desk")
            reason = st.text_area("Why is this event appearing? (Contextual Explanation)")
            
            if st.form_submit_button("Broadcast to Network"):
                vault.conn.cursor().execute(
                    "INSERT INTO signals (pair, type, timeframe, confidence, source, reason, timestamp, status) VALUES (?,?,?,?,?,?,?,?)",
                    (pair, sig_type, tf, conf, source, reason, datetime.now().strftime("%H:%M"), "ACTIVE")
                )
                vault.conn.commit()
                st.success("Event Broadcasted Successfully.")

# --- 4. AUTH FLOW ---
apply_styling()

if 'user_auth' not in st.session_state:
    st.session_state.user_auth = None

if not st.session_state.user_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>CRYPTO ELITE</h1>", unsafe_allow_html=True)
        st.write("---")
        u = st.text_input("Institutional Email")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE"):
            role = vault.verify_auth(u, p)
            if role:
                st.session_state.user_auth = {"user": u, "role": role}
                st.rerun()
            else:
                st.error("Access Denied: Invalid Identity or Key.")
else:
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"**Clearance:** `{st.session_state.user_auth['role']}`")
        nav = st.radio("Intelligence Modules", ["Signal Stream", "Market Overview", "Admin Console"] if st.session_state.user_auth['role'] == 'ADMIN' else ["Signal Stream", "Market Overview"])
        if st.button("Terminate Session"):
            st.session_state.user_auth = None
            st.rerun()

    if nav == "Signal Stream":
        signal_stream()
    elif nav == "Admin Console":
        admin_terminal()
    else:
        st.write("Institutional Market Overview Dashboard Loading...")
