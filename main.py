import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests # නිවුස් ගෙන්වා ගැනීමට
from datetime import datetime, timedelta

# --- 1. CORE ENGINE ---
class EliteV8Engine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v8_final.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, sentiment TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, expiry_date DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, reason TEXT, chart_url TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'ELITE VIP HUB', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'NEUTRAL')")
        
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            long_expiry = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d')
            c.execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", (admin_email, hashed, 'ADMIN', long_expiry))
        self.conn.commit()

engine = EliteV8Engine()
config = pd.read_sql("SELECT * FROM settings WHERE id=1", engine.conn).iloc[0]

# --- 2. GLOBAL NEWS API ---
def get_crypto_news():
    # CryptoPanic වැනි API එකක් හරහා නිවුස් ගෙන්වීම (දැනට Demo Feed එකක් ලෙස)
    # ඇත්තම API Key එකක් පසුව සම්බන්ධ කළ හැක
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url).json()
        return response['Data'][:10] # අලුත්ම නිවුස් 10ක්
    except:
        return []

# --- 3. PREMIUM UI ---
st.set_page_config(page_title=config['app_name'], layout="wide")
color = "#f0b90b"

st.markdown(f"""
<style>
    .stApp {{ background: #080a0c; color: #e1e4e8; }}
    .news-card {{ background: #181a20; border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 4px solid {color}; }}
    .signal-card {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- 4. MODULES ---
def render_news():
    st.markdown("### 🌍 Global Market News")
    news_data = get_crypto_news()
    for news in news_data:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(news['imageurl'], use_container_width=True)
        with col2:
            st.markdown(f"""<div class='news-card'>
                <h4 style='margin:0;'>{news['title']}</h4>
                <p style='font-size:12px; color:#848e9c;'>Source: {news['source']} | {datetime.fromtimestamp(news['published_on']).strftime('%H:%M')}</p>
                <p style='font-size:14px;'>{news['body'][:150]}...</p>
                <a href='{news['url']}' target='_blank' style='color:{color}; text-decoration:none;'>Read Full Story →</a>
            </div>""", unsafe_allow_html=True)

def render_dashboard():
    st.markdown(f"<h1 style='color:{color}; text-align:center;'>{config['app_name']}</h1>", unsafe_allow_html=True)
    
    # ටැබ් මඟින් නිවුස් සහ සිග්නල් වෙන් කිරීම
    tab1, tab2 = st.tabs(["🎯 VIP SIGNALS", "📰 MARKET NEWS"])
    
    with tab1:
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
        for _, s in signals.iterrows():
            st.markdown(f"<div class='signal-card'><h3>{s['pair']} | {s['type']}</h3><p>{s['reason']}</p></div>", unsafe_allow_html=True)
            if s['chart_url']: st.image(s['chart_url'])

    with tab2:
        render_news()

# --- 5. ADMIN CONTROL ---
def render_admin():
    st.title("🛡️ Command Center v8")
    choice = st.sidebar.selectbox("Action", ["Manage Users", "Post Signal", "Settings"])
    
    if choice == "Manage Users":
        with st.form("add_user"):
            u = st.text_input("Member Email")
            p = st.text_input("Security Key")
            if st.form_submit_button("Grant VIP Access"):
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                h = hashlib.sha256(p.encode()).hexdigest()
                engine.conn.cursor().execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", (u, h, 'USER', exp))
                engine.conn.commit(); st.success("Access Granted!")

    elif choice == "Post Signal":
        with st.form("post_sig"):
            pair = st.text_input("Pair")
            reason = st.text_area("Analysis / Video Link (YouTube)")
            img = st.text_input("Chart Image URL")
            if st.form_submit_button("Broadcast"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, reason, chart_url, timestamp) VALUES (?,?,?,?,?)", (pair, "VIP ALERT", reason, img, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Sent!")

# --- 6. AUTHENTICATION ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    st.title("VIP LOGIN")
    u = st.text_input("Email")
    p = st.text_input("Key", type="password")
    if st.button("Access Hub"):
        h = hashlib.sha256(p.encode()).hexdigest()
        res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u, h)).fetchone()
        if res:
            st.session_state.user = {"role": res[0]}
            st.rerun()
        else: st.error("Denied")
else:
    if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
    if st.session_state.user['role'] == 'ADMIN':
        mode = st.sidebar.radio("View", ["Admin", "User"])
        if mode == "Admin": render_admin()
        else: render_dashboard()
    else: render_dashboard()
