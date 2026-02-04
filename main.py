import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE (RE-BUILT TO FIX 'NONE' ERROR) ---
class EliteMasterEngine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v9_master.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, theme_color TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, expiry_date DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, reason TEXT, chart_url TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        # Default Settings
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'ELITE VIP TERMINAL', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', '#f0b90b')")
        
        # Admin Account (ඔයාගේ)
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", 
                      (admin_email, hashed, 'ADMIN', '2030-01-01'))
        self.conn.commit()

    def load_config(self):
        # මෙය 'None' Error එක වැළැක්වීමට භාවිතා කරන ආරක්ෂිත ක්‍රමයයි
        df = pd.read_sql("SELECT * FROM settings WHERE id=1", self.conn)
        if not df.empty:
            return df.iloc[0]
        return {"app_name": "ELITE VIP", "theme_color": "#f0b90b", "logo_url": ""}

engine = EliteMasterEngine()
config = engine.load_config()

# --- 2. UI STYLING ---
st.set_page_config(page_title=config['app_name'], layout="wide")
main_color = config['theme_color']

st.markdown(f"""
<style>
    .stApp {{ background: #050709; color: #e1e4e8; }}
    .neon-text {{ color: {main_color}; text-shadow: 0 0 10px {main_color}55; font-weight: 800; }}
    .glass-card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
    .stButton>button {{ background: {main_color} !important; color: black !important; font-weight: bold; width: 100%; border: none; }}
</style>
""", unsafe_allow_html=True)

# --- 3. VIEWS ---
def user_dashboard():
    st.markdown(f"<h1 class='neon-text'>{config['app_name']}</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🎯 SIGNALS", "📈 LIVE CHART"])
    
    with tab1:
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
        if signals.empty: st.info("No signals found.")
        for _, s in signals.iterrows():
            st.markdown(f"<div class='glass-card'><h3>{s['pair']} | {s['type']}</h3><p>{s['reason']}</p></div>", unsafe_allow_html=True)
            if s['chart_url']: st.image(s['chart_url'])
            
    with tab2:
        st.components.v1.html('<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"});</script><div id="tv" style="height:500px;"></div>', height=510)

def admin_dashboard():
    st.markdown("<h1 class='neon-text'>🛡️ ADMIN PANEL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🚀 SIGNALS", "👥 MEMBERS"])
    
    with t1:
        with st.form("sig"):
            p = st.text_input("Pair")
            t = st.selectbox("Type", ["LONG", "SHORT"])
            r = st.text_area("Analysis")
            c_url = st.text_input("Chart Link")
            if st.form_submit_button("SEND"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, reason, chart_url, timestamp) VALUES (?,?,?,?,?)",
                                            (p, t, r, c_url, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Sent!")
                
    with t2:
        with st.form("user"):
            u = st.text_input("Email")
            p = st.text_input("Key")
            if st.form_submit_button("ADD USER"):
                h = hashlib.sha256(p.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                engine.conn.cursor().execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", (u, h, 'USER', exp))
                engine.conn.commit(); st.success("User Added!")

# --- 4. AUTH & LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>VIP PORTAL</h2>", unsafe_allow_html=True)
        u_id = st.text_input("Email")
        p_id = st.text_input("Security Key", type="password")
        if st.button("LOGIN"):
            h_id = hashlib.sha256(p_id.encode()).hexdigest()
            res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u_id, h_id)).fetchone()
            if res:
                st.session_state.auth = {"email": u_id, "role": res[0]}
                st.rerun()
            else: st.error("Invalid Credentials")
else:
    if st.sidebar.button("LOGOUT"): st.session_state.auth = None; st.rerun()
    if st.session_state.auth['role'] == 'ADMIN':
        mode = st.sidebar.radio("Nav", ["Admin", "User"])
        if mode == "Admin": admin_dashboard()
        else: user_dashboard()
    else:
        user_dashboard()
