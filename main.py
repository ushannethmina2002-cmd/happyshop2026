import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE ---
class FinalEngine:
    def __init__(self):
        # Database එක අලුතින්ම පටන් ගමු (v12.1)
        self.conn = sqlite3.connect('vip_stable_v12_1.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, app_name TEXT, theme_color TEXT, welcome_msg TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT)''')
        
        # Default Settings
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO config VALUES (1, 'ELITE VIP PRO', '#f0b90b', 'Welcome to Institutional Terminal')")
        
        # Admin Account Setup
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry) VALUES (?,?,?,?)", 
                  ('ushannethmina2002@gmail.com', h, 'ADMIN', '2099-12-31'))
        self.conn.commit()

db = FinalEngine()
config = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. GLOBAL UI ---
st.set_page_config(page_title=config['app_name'], layout="wide")
main_color = config['theme_color']

st.markdown(f"""
<style>
    .stApp {{ background: #05070a; color: #e1e4e8; }}
    .stButton>button {{ background: {main_color} !important; color: black !important; font-weight: bold; border-radius: 8px; }}
    .card {{ background: rgba(255,255,255,0.03); border-radius: 12px; padding: 20px; border-left: 5px solid {main_color}; margin-bottom: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DASHBOARD VIEWS ---

def user_dashboard():
    st.title(f"📈 {config['app_name']} - Member Hub")
    st.info(config['welcome_msg'])
    
    t1, t2 = st.tabs(["🎯 VIP SIGNALS", "📊 LIVE CHART"])
    with t1:
        sigs = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db.conn)
        if sigs.empty: st.write("Waiting for professional signals...")
        for _, s in sigs.iterrows():
            st.markdown(f"<div class='card'><h3>{s['pair']} | {s['type']}</h3><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p><p>{s['reason']}</p></div>", unsafe_allow_html=True)
    with t2:
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)

def admin_dashboard():
    st.title("🛡️ ADMIN COMMAND TOWER")
    tab1, tab2, tab3 = st.tabs(["Post Signal", "User Control", "App Settings ⚙️"])
    
    with tab1:
        with st.form("sig_form"):
            p = st.text_input("Asset Pair")
            t = st.selectbox("Type", ["LONG", "SHORT"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            r = st.text_area("Analysis")
            if st.form_submit_button("PUBLISH SIGNAL"):
                db.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, reason) VALUES (?,?,?,?,?,?)", (p, t, e, tp, sl, r))
                db.conn.commit(); st.success("Signal Sent Successfully!")

    with tab2:
        with st.form("usr_form"):
            u = st.text_input("New Member Email")
            k = st.text_input("Access Key")
            if st.form_submit_button("ACTIVATE MEMBER"):
                h = hashlib.sha256(k.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                db.conn.cursor().execute("INSERT INTO users (email, key, role, expiry) VALUES (?,?,?,?)", (u, h, 'USER', exp))
                db.conn.commit(); st.success(f"User {u} Activated!")

    with tab3:
        st.subheader("Global App Control")
        with st.form("cfg_form"):
            name = st.text_input("App Name", value=config['app_name'])
            clr = st.color_picker("Brand Color", value=config['theme_color'])
            msg = st.text_area("Welcome Message", value=config['welcome_msg'])
            if st.form_submit_button("SAVE CHANGES"):
                db.conn.cursor().execute("UPDATE config SET app_name=?, theme_color=?, welcome_msg=? WHERE id=1", (name, clr, msg))
                db.conn.commit(); st.rerun()

# --- 4. AUTH & NAVIGATION ---

if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.title("SECURE LOGIN")
        email_in = st.text_input("Email")
        key_in = st.text_input("Key", type="password")
        if st.button("AUTHENTICATE"):
            h_in = hashlib.sha256(key_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND key=?", (email_in, h_in)).fetchone()
            if res:
                st.session_state.auth = {"email": email_in, "role": res[0]}
                st.rerun()
            else: st.error("Login Denied.")
else:
    # සයිඩ්බාර් එකේ ලොග් අවුට් බටන් එක
    if st.sidebar.button("🚪 Logout"):
        st.session_state.auth = None
        st.rerun()
    
    # ඇඩ්මින්ට පමණක් පෙනෙන Switch Button එක
    if st.session_state.auth['role'] == 'ADMIN':
        st.sidebar.divider()
        st.sidebar.subheader("👑 Admin Options")
        view_mode = st.sidebar.toggle("Switch to User View", value=False)
        
        if view_mode:
            user_dashboard()
        else:
            admin_dashboard()
    else:
        # සාමාන්‍ය යූසර්ට පෙනෙන Dashboard එක
        user_dashboard()
