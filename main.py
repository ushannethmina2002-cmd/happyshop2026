import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import re
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
BOT_TOKEN = "8526792641:AAHEyboZTc9-lporhmcAGekEVO-Z-D-pvb8"
CHANNEL_ID = "-1003662013328"

def init_db():
    conn = sqlite3.connect('crypto_empire_v11.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, role TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, note TEXT, time TEXT)')
    
    defaults = [('app_name', 'CRYPTO EMPIRE VIP'), ('theme_color', '#f0b90b'), ('announcement', '💎 Premium Trading Access Enabled!')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. ADVANCED UI STYLING ---
def apply_ultra_ui():
    color = db_conn.cursor().execute("SELECT value FROM settings WHERE key='theme_color'").fetchone()[0]
    st.markdown(f"""
        <style>
        .stApp {{ background: linear-gradient(135deg, #0b0e11 0%, #1e2329 100%); color: #eaecef; }}
        [data-testid="stSidebar"] {{ background: rgba(30, 35, 41, 0.9) !important; backdrop-filter: blur(10px); }}
        .signal-card {{
            background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;
            transition: 0.3s ease;
        }}
        .signal-card:hover {{ border-color: {color}; transform: scale(1.01); }}
        .vip-badge {{ background: linear-gradient(90deg, #f0b90b, #ffea00); color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. ADMIN FEATURES ---
def admin_portal():
    st.sidebar.title("💎 ELITE ADMIN")
    task = st.sidebar.selectbox("System Tasks", ["Dashboard", "Signal Manager", "User Access", "App Settings"])
    
    if task == "Dashboard":
        st.title("📊 Platform Oversight")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Users", "1.2k")
        c2.metric("Win Rate", "88%")
        c3.metric("Server", "Optimal")
        st.write("### Recent Activity")
        st.table(pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn))

    elif task == "App Settings":
        st.title("⚙️ Global Configuration")
        with st.form("global_settings"):
            name = st.text_input("App Name", "CRYPTO EMPIRE VIP")
            color = st.color_picker("Brand Theme Color", "#f0b90b")
            ann = st.text_area("Live Announcement", "New Signals coming soon!")
            if st.form_submit_button("Update Platform"):
                db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (name,))
                db_conn.commit()
                st.rerun()

# --- 4. USER FEATURES ---
def user_portal():
    st.sidebar.title("🚀 NAVIGATOR")
    menu = st.sidebar.radio("Categories", ["🏠 Home", "📊 Markets", "🎓 Academy", "📓 My Journal", "💬 Support"])

    if menu == "🏠 Home":
        st.title("🎯 Premium Signals")
        # Live Gauge Widget
        components.html('<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>{"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark"}</script>', height=80)
        
        df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db_conn)
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="signal-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="vip-badge">{r['type']}</span>
                    <small>{r['time']}</small>
                </div>
                <h2 style="margin:10px 0;">{r['pair']} <span style="color:#2ebd85;">{r['side']}</span></h2>
                <p>Entry: {r['entry']} | TP: {r['tp']} | SL: {r['sl']}</p>
            </div>
            """, unsafe_allow_html=True)

    elif menu == "📊 Markets":
        st.title("📊 Market Analysis")
        tab1, tab2 = st.tabs(["Charts", "News Calendar"])
        with tab1:
            components.html('<div id="tv" style="height:450px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"tv"});</script></div>', height=450)
        with tab2:
            st.subheader("Economic Calendar")
            components.html('<iframe src="https://sslecal2.forexprostools.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&category=_all&importance=1,2,3&features=datepicker,timezone&countries=25,32,6,37,7,22,5,10,35,43,36,110,11,26,12,4,8&calType=week&timeZone=8&lang=1" width="100%" height="500"></iframe>', height=500)

    elif menu == "📓 My Journal":
        st.title("📓 Personal Trade Journal")
        note = st.text_area("Record your trade thoughts...")
        if st.button("Save Note"):
            db_conn.cursor().execute("INSERT INTO journal (email, note, time) VALUES (?,?,?)", (st.session_state.user_email, note, datetime.now().strftime("%Y-%m-%d")))
            db_conn.commit()
            st.success("Note Saved!")

# --- 5. MAIN LOGIC ---
apply_ultra_ui()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ELITE ACCESS")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    if st.button("ENTER"):
        st.session_state.update({"logged_in": True, "is_admin": (e == "ushan2008@gmail.com"), "user_email": e})
        st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_portal()
    else: user_portal()
