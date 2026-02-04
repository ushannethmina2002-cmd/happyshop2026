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
    conn = sqlite3.connect('crypto_elite_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, pnl TEXT, img_url TEXT, time TEXT, msg_id TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS support (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, msg TEXT, reply TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('admin_pw', '2008')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

def apply_premium_style():
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e11; color: #eaecef; }
        [data-testid="stSidebar"] { background-color: #1e2329 !important; border-right: 1px solid #363c44; }
        .signal-card { background: #1e2329; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #363c44; }
        .stButton>button { background-color: #f0b90b !important; color: black !important; font-weight: bold; border-radius: 8px; width: 100%; border: none; }
        .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
        .stTabs [data-baseweb="tab"] { color: #848e9c; }
        .stTabs [aria-selected="true"] { color: #f0b90b; border-bottom-color: #f0b90b; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. CORE LOGIC ---
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

# --- 4. UI COMPONENTS ---
st.set_page_config(page_title="Crypto Elite Pro", layout="wide")
apply_premium_style()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_ui():
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=70)
        st.title("Elite Login")
        email = st.text_input("Email").lower()
        pw = st.text_input("Password", type="password")
        if st.button("LOG IN"):
            if email == "ushan2008@gmail.com" and pw == "2008":
                st.session_state.update({"logged_in": True, "is_admin": True, "user_email": email})
                st.rerun()
            elif "@gmail.com" in email:
                st.session_state.update({"logged_in": True, "is_admin": False, "user_email": email})
                st.rerun()

# --- 5. ADMIN VIEW ---
def admin_panel():
    st.title("⚡ ADMIN CONTROL CENTER")
    sync_telegram()
    
    tab1, tab2, tab3 = st.tabs(["📊 Performance", "📢 Manage Signals", "💬 Support Inbox"])
    
    with tab1:
        df_all = pd.read_sql("SELECT * FROM signals", db_conn)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Signals", len(df_all))
        active = len(df_all[df_all['status'] == 'Active'])
        c2.metric("Active Signals", active)
        c3.metric("Platform Status", "Online")
        
    with tab2:
        st.subheader("Signal Database")
        edited_df = st.data_editor(df_all, num_rows="dynamic", key="editor")
        if st.button("Update Database"):
            edited_df.to_sql('signals', db_conn, if_exists='replace', index=False)
            st.success("Database Updated!")

    with tab3:
        st.subheader("User Support Tickets")
        msgs = pd.read_sql("SELECT * FROM support WHERE reply IS NULL", db_conn)
        if msgs.empty: st.info("No pending messages.")
        for _, r in msgs.iterrows():
            with st.chat_message("user"):
                st.write(f"**From:** {r['email']}\n\n{r['msg']}")
                reply = st.text_input("Your Reply", key=f"r_{r['id']}")
                if st.button("Send Reply", key=f"b_{r['id']}"):
                    db_conn.cursor().execute("UPDATE support SET reply=? WHERE id=?", (reply, r['id']))
                    db_conn.commit()
                    st.rerun()

# --- 6. USER VIEW ---
def user_dashboard():
    sync_telegram()
    st.sidebar.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=50)
    menu = st.sidebar.selectbox("Navigation", ["🎯 Signals", "📊 Market", "🧮 Calculator", "💬 Support"])

    if menu == "🎯 Signals":
        st.title("🎯 LIVE VIP SIGNALS")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        for _, row in df.iterrows():
            badge = "#2ebd85" if row['side'] == "LONG" else "#f6465d"
            st.markdown(f"""<div class="signal-card"><span style="background:{badge}; padding:3px 10px; border-radius:4px; font-weight:bold;">{row['side']}</span>
            <h2 style="margin:10px 0;">{row['pair']}</h2><p>Entry: <b>{row['entry']}</b> | TP: <b>{row['tp']}</b> | SL: <b>{row['sl']}</b></p></div>""", unsafe_allow_html=True)

    elif menu == "📊 Market":
        st.title("📊 MARKET ANALYSIS")
        components.html('<div id="c" style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize": true,"symbol": "BINANCE:BTCUSDT","theme": "dark","container_id": "c"});</script></div>', height=500)
        components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js" async>{"colorTheme":"dark","width":"100%","height":500}</script>', height=500)

    elif menu == "🧮 Calculator":
        st.title("🧮 RISK CALCULATOR")
        bal = st.number_input("Account Balance ($)", 100.0)
        risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
        if st.button("Calculate"):
            st.success(f"Recommended Position: **${(bal * risk / 100) / 0.02:.2f}**")

    elif menu == "💬 Support":
        st.title("💬 LIVE SUPPORT")
        with st.form("sup"):
            m = st.text_area("How can we help?")
            if st.form_submit_button("SEND"):
                db_conn.cursor().execute("INSERT INTO support (email, msg, time) VALUES (?,?,?)", (st.session_state.user_email, m, datetime.now().strftime("%H:%M")))
                db_conn.commit()
                st.toast("Sent!")

# --- EXECUTION ---
if not st.session_state.logged_in: login_ui()
else:
    if st.sidebar.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()
    admin_panel() if st.session_state.is_admin else user_dashboard()

