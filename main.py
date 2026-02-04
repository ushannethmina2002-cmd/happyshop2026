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

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_pro_final_v8.db', check_same_thread=False)
    c = conn.cursor()
    # Signals Table
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, 
                  tp TEXT, sl TEXT, status TEXT, pnl TEXT, img_url TEXT, time TEXT, msg_id TEXT UNIQUE)''')
    # Support Chat Table
    c.execute('''CREATE TABLE IF NOT EXISTS support 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, msg TEXT, reply TEXT, time TEXT)''')
    # Settings Table
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'Crypto Elite Pro Hub'), ('admin_pw', '2008')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

def get_setting(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else ""

# --- 3. AUTO SYNC FROM TELEGRAM ---
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
                        pair_match = re.search(r'([A-Z0-9]{2,10}/?[A-Z0-9]{2,10})', text.upper())
                        pair = pair_match.group(1) if pair_match else "SIGNAL"
                        db_conn.cursor().execute("""INSERT INTO signals (pair, side, entry, tp, sl, status, pnl, img_url, time, msg_id) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                  (pair, side, "Market", "VIP", "VIP", "Active", "0", "", datetime.now().strftime("%Y-%m-%d %H:%M"), msg_id))
                        db_conn.commit()
    except: pass

# --- 4. TRADINGVIEW WIDGETS ---
def tv_chart():
    components.html("""
        <div id="tv-chart" style="height:500px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">new TradingView.widget({"autosize": true,"symbol": "BINANCE:BTCUSDT","interval": "H","timezone": "Etc/UTC","theme": "dark","style": "1","locale": "en","toolbar_bg": "#f1f3f6","enable_publishing": false,"hide_side_toolbar": false,"allow_symbol_change": true,"container_id": "tv-chart"});</script></div>
    """, height=500)

def tv_analysis():
    components.html("""
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
        {"interval": "1h","width": "100%","isTransparent": false,"height": 450,"symbol": "BINANCE:BTCUSDT","showIntervalTabs": true,"displayMode": "single","locale": "en","theme": "dark"}
        </script>
    """, height=450)

def tv_heatmap():
    components.html("""
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js" async>
        {"dataSource": "Crypto","hasSymbolTooltip": true,"isTransparent": false,"symbolHighlight": true,"width": "100%","height": 500,"colorTheme": "dark","locale": "en"}
        </script>
    """, height=500)

# --- 5. PERSISTENT LOGIN LOGIC ---
st.set_page_config(page_title=get_setting('app_name'), layout="wide")

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def login():
    st.title(f"🔐 Welcome to {get_setting('app_name')}")
    st.info("වරක් ලොග් වූ පසු, ඔබ 'Logout' වන තෙක් මෙම බ්‍රවුසරය ඔබව මතක තබා ගනී.")
    
    email = st.text_input("Gmail Address").lower()
    pw = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and pw == get_setting('admin_pw'):
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.user_email = email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("වැරදි විස්තර, කරුණාකර නැවත උත්සාහ කරන්න.")

# --- 6. ADMIN & USER INTERFACES ---
def admin_panel():
    st.sidebar.title("Admin Panel")
    choice = st.sidebar.radio("Navigation", ["🏠 Stats", "📢 Signals", "💬 Inbox", "⚙️ Settings"])
    
    if choice == "🏠 Stats":
        st.title("📊 Platform Dashboard")
        df_sig = pd.read_sql("SELECT * FROM signals", db_conn)
        st.metric("Total Signals", len(df_sig))
        if not df_sig.empty:
            st.line_chart(df_sig.set_index('time')['pnl'])
        
    elif choice == "💬 Inbox":
        st.title("💬 User Messages")
        data = pd.read_sql("SELECT * FROM support WHERE reply IS NULL", db_conn)
        for i, r in data.iterrows():
            st.warning(f"From: {r['email']} | Msg: {r['msg']}")
            rep = st.text_input("Reply", key=f"r_{r['id']}")
            if st.button("Send Reply", key=f"b_{r['id']}"):
                db_conn.cursor().execute("UPDATE support SET reply=? WHERE id=?", (rep, r['id']))
                db_conn.commit()
                st.rerun()

    elif choice == "⚙️ Settings":
        st.title("⚙️ App Settings")
        new_name = st.text_input("App Name", get_setting('app_name'))
        new_pw = st.text_input("Admin Password", get_setting('admin_pw'))
        if st.button("Save Changes"):
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (new_name,))
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='admin_pw'", (new_pw,))
            db_conn.commit()
            st.success("Settings Updated!")

def user_dashboard():
    sync_telegram()
    st.sidebar.title(f"👋 {st.session_state.user_email}")
    menu = st.sidebar.selectbox("Menu", ["🎯 Live Signals", "📊 Market Analysis", "🧮 Calculator", "💬 Support Chat"])

    if menu == "🎯 Live Signals":
        st.title("🎯 Active Trading Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if not df.empty:
            for _, row in df.iterrows():
                color = "#00ffcc" if row['side'] == "LONG" else "#ff4b4b"
                st.markdown(f"<div style='border-left: 5px solid {color}; padding:15px; background:#1e2329; border-radius:10px; margin-bottom:10px;'><h3>{row['side']} {row['pair']}</h3><p>Entry: {row['entry']} | TP: {row['tp']} | SL: {row['sl']}</p></div>", unsafe_allow_html=True)
        else:
            st.info("දැනට සක්‍රිය සිග්නල් නොමැත.")

    elif menu == "📊 Market Analysis":
        st.title("📊 Real-Time Market Analysis")
        c1, c2 = st.columns([2, 1])
        with c1: tv_chart()
        with c2: tv_analysis()
        st.subheader("🔥 Crypto Heatmap")
        tv_heatmap()

    elif menu == "🧮 Calculator":
        st.title("🧮 Risk Management Calculator")
        bal = st.number_input("Account Balance ($)", 100.0)
        risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
        sl_dist = st.number_input("SL Distance (%)", 1.0)
        if st.button("Calculate"):
            size = (bal * (risk/100)) / (sl_dist/100)
            st.success(f"Recommended Position Size: **${size:.2f}**")

    elif menu == "💬 Support Chat":
        st.title("💬 Live Chat Support")
        my_chats = pd.read_sql(f"SELECT * FROM support WHERE email='{st.session_state.user_email}'", db_conn)
        for _, m in my_chats.iterrows():
            st.chat_message("user").write(m['msg'])
            if m['reply']: st.chat_message("assistant").write(m['reply'])
        
        with st.form("support_form", clear_on_submit=True):
            m = st.text_area("ඔබට ඇති ගැටලුව මෙතන ලියන්න...")
            if st.form_submit_button("Send"):
                db_conn.cursor().execute("INSERT INTO support (email, msg, time) VALUES (?,?,?)", (st.session_state.user_email, m, datetime.now().strftime("%H:%M")))
                db_conn.commit()
                st.toast("පණිවිඩය යැවුණා!")

# --- EXECUTION ---
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.is_admin:
        admin_panel()
    else:
        user_dashboard()
    
    # Logout Button (Always at the bottom of sidebar)
    st.sidebar.markdown("---")
    if st.sidebar.button("🔴 Logout from App"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.user_email = ""
        st.rerun()
