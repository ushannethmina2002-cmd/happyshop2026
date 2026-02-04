import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE ---
class EliteV7Engine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v7_complete.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, 
            announcement TEXT, theme_color TEXT, sentiment TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, expiry_date DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, reason TEXT, chart_url TEXT,
            result TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'ELITE VIP INTEL', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'Welcome to v7 Institutional Terminal', '#f0b90b', 'NEUTRAL')")
        
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            long_expiry = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d')
            c.execute("INSERT INTO users (username, password, role, status, expiry_date) VALUES (?,?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE', long_expiry))
        self.conn.commit()

engine = EliteV7Engine()
config = pd.read_sql("SELECT * FROM settings WHERE id=1", engine.conn).iloc[0]

# --- 2. PREMIUM UI ---
st.set_page_config(page_title=config['app_name'], layout="wide")
color = config['theme_color']

st.markdown(f"""
<style>
    .stApp {{ background: #080a0c; color: #e1e4e8; font-family: 'Inter', sans-serif; }}
    .glass-card {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 15px; padding: 25px; margin-bottom: 20px; }}
    .sentiment-box {{ padding: 10px; border-radius: 10px; text-align: center; font-weight: 800; background: {color}22; color: {color}; border: 1px solid {color}55; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DASHBOARD ---
def render_dashboard():
    st.markdown(f"<h1 style='color:{color};'>{config['app_name']}</h1>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 2])
    with col_a: st.markdown(f"<div class='sentiment-box'>MARKET SENTIMENT: {config['sentiment']}</div>", unsafe_allow_html=True)
    with col_b: st.components.v1.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)
    
    st.info(f"📢 {config['announcement']}")

    signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
    for _, s in signals.iterrows():
        with st.container():
            st.markdown(f"<div class='glass-card'><h3>{s['pair']} | {s['type']}</h3><p>{s['reason']}</p></div>", unsafe_allow_html=True)
            if s['chart_url']: st.image(s['chart_url'])

# --- 4. ADMIN CONTROL (VIP MANAGEMENT ADDED) ---
def render_admin():
    st.title("🛡️ Admin Command Center")
    t1, t2, t3 = st.tabs(["Signal Broadcaster", "VIP Member Management", "App Settings"])

    with t1:
        with st.form("sig_v7"):
            pair = st.text_input("Pair")
            stype = st.selectbox("Event", ["Breakout", "Trend", "Liquidity"])
            c_url = st.text_input("Chart Image URL (Optional)")
            reason = st.text_area("Analysis")
            if st.form_submit_button("Broadcast"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, timeframe, confidence, reason, chart_url, result, timestamp) VALUES (?,?,?,?,?,?,?,?)",
                                            (pair, stype, "4H", "High", reason, c_url, "PENDING", datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Signal Sent!")

    with t2:
        st.subheader("Add New VIP Member")
        with st.form("new_vip_form"):
            new_email = st.text_input("VIP Member Email")
            new_key = st.text_input("Set Security Key (Password)", type="password")
            duration = st.number_input("Access Duration (Days)", min_value=1, value=30)
            if st.form_submit_button("Create VIP Account"):
                expiry = (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')
                hashed_key = hashlib.sha256(new_key.encode()).hexdigest()
                try:
                    engine.conn.cursor().execute("INSERT INTO users (username, password, role, status, expiry_date) VALUES (?,?,?,?,?)",
                                                (new_email, hashed_key, 'USER', 'ACTIVE', expiry))
                    engine.conn.commit()
                    st.success(f"Account Created for {new_email}! Key: {new_key} (Expires: {expiry})")
                except: st.error("User already exists.")
        
        st.divider()
        st.subheader("Current VIP Members")
        users_list = pd.read_sql("SELECT username, expiry_date, status FROM users WHERE role='USER'", engine.conn)
        st.dataframe(users_list, use_container_width=True)

    with t3:
        with st.form("sys_v7"):
            name = st.text_input("App Name", value=config['app_name'])
            sent = st.selectbox("Sentiment", ["FEAR", "NEUTRAL", "GREED"], index=1)
            if st.form_submit_button("Update Settings"):
                engine.conn.cursor().execute("UPDATE settings SET app_name=?, sentiment=? WHERE id=1", (name, sent))
                engine.conn.commit(); st.rerun()

# --- 5. LOGIN FLOW ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    _, lb, _ = st.columns([1, 1.2, 1])
    with lb:
        st.title(config['app_name'])
        u_in = st.text_input("Email")
        p_in = st.text_input("Security Key", type="password")
        if st.button("Enter VIP Portal"):
            h_in = hashlib.sha256(p_in.encode()).hexdigest()
            res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u_in, h_in)).fetchone()
            if res:
                if res[0] != 'ADMIN' and datetime.now() > datetime.strptime(res[1], '%Y-%m-%d'):
                    st.error("❌ Your VIP access has expired.")
                else:
                    st.session_state.user = {"email": u_in, "role": res[0]}
                    st.rerun()
            else: st.error("Invalid Email or Key.")
else:
    if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
    if st.session_state.user['role'] == 'ADMIN':
        mode = st.sidebar.radio("View", ["Admin", "User"])
        if mode == "Admin": render_admin()
        else: render_dashboard()
    else: render_dashboard()
