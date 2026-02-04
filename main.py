import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE (FORCE RE-INITIALIZE) ---
class GodEngineV10:
    def __init__(self):
        # අලුත් නමකින් ඩේටාබේස් එක හදන්න (එතකොට පරණ ඒවා එක්ක පැටලෙන්නේ නෑ)
        self.conn = sqlite3.connect('vip_god_v10_2.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Settings
        c.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, name TEXT, color TEXT)''')
        # Users (සියලුම columns හරියටම තියෙනවා)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, 
            key TEXT, 
            expiry DATE, 
            role TEXT,
            status TEXT)''')
        # Signals
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, 
            reason TEXT, chart TEXT, timestamp TEXT)''')
        
        # Default Data
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO config VALUES (1, 'ELITE TERMINAL v10', '#f0b90b')")
        
        # Admin Seed
        admin_email = "ushannethmina2002@gmail.com"
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, expiry, role, status) VALUES (?,?,?,?,?)", 
                  (admin_email, h, '2099-12-31', 'ADMIN', 'ACTIVE'))
        self.conn.commit()

db = GodEngineV10()
config = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. THEME & UI ---
st.set_page_config(page_title=config['name'], layout="wide")
color = config['color']

st.markdown(f"""
<style>
    .stApp {{ background: #05070a; color: #e1e4e8; }}
    .stButton>button {{ background: {color} !important; color: black !important; width: 100%; border-radius: 8px; font-weight: bold; }}
    .card {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin-bottom: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. VIEWS ---
def admin_panel():
    st.title("🛡️ Admin Command Center")
    t1, t2 = st.tabs(["Signals", "Users"])
    with t1:
        with st.form("sig"):
            p = st.text_input("Pair")
            t = st.selectbox("Type", ["LONG", "SHORT"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            r = st.text_area("Analysis")
            if st.form_submit_button("PUBLISH"):
                db.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, reason, timestamp) VALUES (?,?,?,?,?,?,?)",
                                        (p, t, e, tp, sl, r, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Signal Sent!")
    with t2:
        with st.form("usr"):
            u = st.text_input("User Email")
            k = st.text_input("User Key")
            if st.form_submit_button("ADD VIP"):
                hashed = hashlib.sha256(k.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                db.conn.cursor().execute("INSERT INTO users (email, key, expiry, role, status) VALUES (?,?,?,?,?)", (u, hashed, exp, 'USER', 'ACTIVE'))
                db.conn.commit(); st.success("VIP Added!")

def user_panel():
    st.title(f"📈 {config['name']}")
    st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:400px;"></div>', height=410)
    st.subheader("🎯 Active Signals")
    sigs = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db.conn)
    for _, s in sigs.iterrows():
        st.markdown(f"<div class='card'><h4>{s['pair']} | {s['type']}</h4><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p></div>", unsafe_allow_html=True)

# --- 4. AUTH FLOW ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.subheader("VIP Institutional Login")
        e_in = st.text_input("Email")
        k_in = st.text_input("Key", type="password")
        if st.button("AUTHENTICATE"):
            h_in = hashlib.sha256(k_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role, expiry FROM users WHERE email=? AND key=?", (e_in, h_in)).fetchone()
            if res:
                st.session_state.user = {"email": e_in, "role": res[0]}
                st.rerun()
            else: st.error("Login Failed.")
else:
    if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
    if st.session_state.user['role'] == 'ADMIN':
        m = st.sidebar.radio("Nav", ["Admin", "User"])
        if m == "Admin": admin_panel()
        else: user_panel()
    else: user_panel()
