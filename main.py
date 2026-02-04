import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
BOT_TOKEN = "8526792641:AAHEyboZTc9-lporhmcAGekEVO-Z-D-pvb8"
CHANNEL_ID = "-1003662013328"

# --- 2. DATABASE & STYLING ---
def init_db():
    conn = sqlite3.connect('crypto_premium_v9.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, pnl TEXT, img_url TEXT, time TEXT, msg_id TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS support (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, msg TEXT, reply TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('admin_pw', '2008')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. PREMIUM UI DESIGN (CSS) ---
def apply_premium_style():
    st.markdown("""
        <style>
        /* පසුබිම සහ අකුරු */
        .stApp { background-color: #0b0e11; color: #eaecef; }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #1e2329 !important; border-right: 1px solid #363c44; }
        
        /* Signal Card Design */
        .signal-card {
            background: #1e2329;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #363c44;
            transition: 0.3s;
        }
        .signal-card:hover { border-color: #f0b90b; transform: translateY(-2px); }
        
        /* Buttons */
        .stButton>button {
            background-color: #f0b90b !important;
            color: black !important;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
            border: none;
        }
        
        /* Metric Styling */
        [data-testid="stMetricValue"] { color: #f0b90b !important; font-size: 24px; }
        </style>
    """, unsafe_allow_html=True)

# --- 4. TELEGRAM SYNC ---
def sync_telegram():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if response.get("ok"):
            for result in response.get("result", []):
                msg = result.get("channel_post", {})
                if str(msg.get("chat", {}).get("id")) == CHANNEL_ID:
                    text, msg_id = msg.get("text", ""), str(msg.get("message_id"))
                    check = db_conn.cursor().execute("SELECT id FROM signals WHERE msg_id=?", (msg_id,)).fetchone()
                    if not check and text:
                        side = "LONG" if any(x in text.upper() for x in ["BUY", "LONG"]) else "SHORT"
                        pair = re.search(r'([A-Z0-9]{2,10}/?[A-Z0-9]{2,10})', text.upper()).group(1) if re.search(r'([A-Z0-9]{2,10}/?[A-Z0-9]{2,10})', text.upper()) else "TOKEN"
                        db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, pnl, time, msg_id) VALUES (?,?,?,?,?,?,?,?,?)",
                                                 (pair, side, "MARKET", "VIP", "VIP", "Active", "0", datetime.now().strftime("%Y-%m-%d %H:%M"), msg_id))
                        db_conn.commit()
    except: pass

# --- 5. INTERFACE COMPONENTS ---
st.set_page_config(page_title="Crypto Elite Pro", layout="wide", initial_sidebar_state="expanded")
apply_premium_style()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_ui():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=80)
        st.title("Welcome Back")
        st.markdown("Enter your credentials to access premium signals.")
        email = st.text_input("Gmail Address").lower()
        pw = st.text_input("Password", type="password")
        if st.button("SIGN IN"):
            if email == "ushan2008@gmail.com" and pw == "2008":
                st.session_state.update({"logged_in": True, "is_admin": True, "user_email": email})
                st.rerun()
            elif "@gmail.com" in email:
                st.session_state.update({"logged_in": True, "is_admin": False, "user_email": email})
                st.rerun()

def user_dashboard():
    sync_telegram()
    # Horizontal Top Menu (Custom UI)
    st.sidebar.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=50)
    st.sidebar.title("PRO NAVIGATOR")
    menu = st.sidebar.selectbox("Jump to", ["🎯 Trade Signals", "📊 Market Hub", "🧮 Risk Tool", "💬 Help Center"])

    if menu == "🎯 Trade Signals":
        st.subheader("🎯 Live Premium Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if df.empty:
            st.info("Waiting for next high-probability signal...")
        else:
            for _, row in df.iterrows():
                badge_color = "#2ebd85" if row['side'] == "LONG" else "#f6465d"
                st.markdown(f"""
                <div class="signal-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="background:{badge_color}; color:white; padding:4px 12px; border-radius:4px; font-weight:bold;">{row['side']}</span>
                        <span style="color:#848e9c;">{row['time']}</span>
                    </div>
                    <h2 style="margin:10px 0; color:white;">{row['pair']}</h2>
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
                        <div><small style="color:#848e9c;">ENTRY</small><br><b>{row['entry']}</b></div>
                        <div><small style="color:#848e9c;">TARGET</small><br><b style="color:#2ebd85;">{row['tp']}</b></div>
                        <div><small style="color:#848e9c;">STOP LOSS</small><br><b style="color:#f6465d;">{row['sl']}</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    elif menu == "📊 Market Hub":
        st.subheader("📊 Advanced Market Intel")
        tab_a, tab_b = st.tabs(["Real-Time Chart", "Market Heatmap"])
        with tab_a:
            components.html('<div id="chart" style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize": true,"symbol": "BINANCE:BTCUSDT","interval": "H","theme": "dark","style": "1","locale": "en","container_id": "chart"});</script></div>', height=500)
        with tab_b:
            components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js" async>{"colorTheme": "dark","height": 500,"width": "100%"}</script>', height=500)

    elif menu == "🧮 Risk Tool":
        st.subheader("🧮 Position Size Calculator")
        c1, c2 = st.columns(2)
        bal = c1.number_input("Wallet Balance ($)", 100.0)
        risk = c2.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
        sl_p = st.number_input("Stop Loss Distance (%)", 1.0)
        if st.button("Calculate Position"):
            size = (bal * (risk/100)) / (sl_p/100)
            st.success(f"Recommended Trade Amount: **${size:.2f}**")

    elif menu == "💬 Help Center":
        st.subheader("💬 Support Ticket")
        with st.form("chat"):
            msg = st.text_area("What is your query?")
            if st.form_submit_button("SUBMIT TICKET"):
                db_conn.cursor().execute("INSERT INTO support (email, msg, time) VALUES (?,?,?)", (st.session_state.user_email, msg, datetime.now().strftime("%H:%M")))
                db_conn.commit()
                st.toast("Ticket Created Successfully!")

# --- EXECUTION ---
if not st.session_state.logged_in: login_ui()
else:
    if st.sidebar.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()
    user_dashboard() if not st.session_state.get('is_admin') else st.write("Admin View is ready in sidebar.")

        
