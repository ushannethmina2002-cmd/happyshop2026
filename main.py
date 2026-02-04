import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta

# --- 1. CORE ENGINE (CLEAN & ROBUST) ---
class InstitutionalEngine:
    def __init__(self):
        # අලුත් DB නමකින් පටන් ගමු
        self.conn = sqlite3.connect('vip_ultra_v11.db', check_same_thread=False)
        self.init_db()
        self.seed_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, name TEXT, color TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT, time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS intel (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, itype TEXT, time TEXT)''')
        self.conn.commit()

    def seed_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO config VALUES (1, 'ELITE PRO HUB', '#f0b90b')")
        
        admin_mail = "ushannethmina2002@gmail.com"
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry) VALUES (?,?,?,?)", 
                  (admin_mail, h, 'ADMIN', '2099-12-31'))
        self.conn.commit()

db = InstitutionalEngine()
config = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. GLOBAL STYLING ---
st.set_page_config(page_title=config['name'], layout="wide")
color = config['color']

st.markdown(f"""
<style>
    .stApp {{ background: #05070a; color: #e1e4e8; }}
    .card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; border-left: 5px solid {color}; margin-bottom: 15px; }}
    .stButton>button {{ background: {color} !important; color: black !important; font-weight: bold; width: 100%; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LIVE MODULES ---
def fetch_news():
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        return res['Data'][:6]
    except: return []

# --- 4. ADMIN INTERFACE (50+ FEATURES COMPATIBLE) ---
def render_admin():
    st.title("🛡️ Institutional Admin Control")
    t1, t2, t3, t4 = st.tabs(["Signals", "User Management", "Whale Intel", "Settings"])

    with t1:
        with st.form("signal_form"):
            c1, c2 = st.columns(2)
            pair = c1.text_input("Asset Pair")
            mode = c2.selectbox("Mode", ["LONG 🚀", "SHORT 🩸"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            reason = st.text_area("Analysis Details")
            if st.form_submit_button("PUBLISH SIGNAL"):
                db.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, reason, time) VALUES (?,?,?,?,?,?,?)",
                                        (pair, mode, e, tp, sl, reason, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Signal Live!")

    with t2:
        with st.form("user_add"):
            u_mail = st.text_input("Member Email")
            u_key = st.text_input("Set Security Key")
            if st.form_submit_button("ACTIVATE VIP"):
                h = hashlib.sha256(u_key.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                db.conn.cursor().execute("INSERT INTO users (email, key, role, expiry) VALUES (?,?,?,?)", (u_mail, h, 'USER', exp))
                db.conn.commit(); st.success(f"Member Activated until {exp}")

    with t3:
        with st.form("intel_form"):
            title = st.text_input("Alert Headline")
            body = st.text_area("Alert Content")
            itype = st.selectbox("Category", ["WHALE ALERT 🐋", "URGENT NEWS 📰"])
            if st.form_submit_button("PUSH ALERT"):
                db.conn.cursor().execute("INSERT INTO intel (title, body, itype, time) VALUES (?,?,?,?)", (title, body, itype, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Pushed to Members!")

# --- 5. USER INTERFACE (30+ FEATURES COMPATIBLE) ---
def render_user():
    st.markdown(f"<h1 style='color:{color}'>{config['name']}</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 VIP SIGNALS", "📰 GLOBAL NEWS", "🐋 WHALE ALERTS", "📈 LIVE CHART"])

    with tab1:
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db.conn)
        if signals.empty: st.info("Waiting for institutional signals...")
        for _, s in signals.iterrows():
            st.markdown(f"<div class='card'><h3>{s['pair']} | {s['type']}</h3><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p><p>{s['reason']}</p></div>", unsafe_allow_html=True)

    with tab2:
        news = fetch_news()
        for n in news:
            st.markdown(f"<div class='card'><h4>{n['title']}</h4><p>{n['body'][:150]}...</p><a href='{n['url']}' target='_blank'>Read Full Story →</a></div>", unsafe_allow_html=True)

    with tab3:
        alerts = pd.read_sql("SELECT * FROM intel ORDER BY id DESC", db.conn)
        for _, a in alerts.iterrows():
            st.warning(f"🕒 {a['time']} | {a['itype']} \n\n **{a['title']}**: {a['body']}")

    with tab4:
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)

# --- 6. AUTH FLOW ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.title("LOGIN")
        e_in = st.text_input("Institutional Email")
        k_in = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE"):
            h = hashlib.sha256(k_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role, expiry FROM users WHERE email=? AND key=?", (e_in, h)).fetchone()
            if res:
                st.session_state.auth = {"email": e_in, "role": res[0]}
                st.rerun()
            else: st.error("Access Denied.")
else:
    if st.sidebar.button("Logout"): st.session_state.auth = None; st.rerun()
    if st.session_state.auth['role'] == 'ADMIN':
        choice = st.sidebar.radio("Menu", ["Admin Tower", "Member Hub"])
        if choice == "Admin Tower": render_admin()
        else: render_user()
    else: render_user()
