import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. DATABASE & CONFIG ---
def init_db():
    conn = sqlite3.connect('crypto_v28_animated.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, msg TEXT, time TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. THE ULTIMATE UI DESIGN (CSS) ---
def apply_pro_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp { 
        background: #0b0e11; /* Fallback for no animation */
        color: white; 
        font-family: 'Inter', sans-serif; 
        position: relative;
        overflow: hidden; /* Hide overflow from animations */
    }
    
    /* Animated Background for Login Page */
    .crypto-animation-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        overflow: hidden;
        background: radial-gradient(circle at 20% 20%, #1a1e23 0%, #0b0e11 100%);
    }

    .crypto-coin {
        position: absolute;
        width: 30px; /* Size of the coins */
        height: 30px;
        background-color: rgba(255, 200, 0, 0.5); /* Goldish color */
        border-radius: 50%;
        opacity: 0;
        animation: floatAndFade 15s infinite ease-in-out;
        box-shadow: 0 0 15px rgba(255, 200, 0, 0.3);
    }

    @keyframes floatAndFade {
        0% { transform: translateY(100vh) scale(0.5); opacity: 0; }
        50% { opacity: 0.8; }
        100% { transform: translateY(-50vh) scale(1.5); opacity: 0; }
    }
    
    /* Generate multiple coins with staggered animation */
    .crypto-coin:nth-child(1) { left: 10%; animation-delay: 0s; }
    .crypto-coin:nth-child(2) { left: 20%; animation-delay: 2s; width: 25px; height: 25px; }
    .crypto-coin:nth-child(3) { left: 30%; animation-delay: 4s; }
    .crypto-coin:nth-child(4) { left: 40%; animation-delay: 6s; width: 35px; height: 35px; }
    .crypto-coin:nth-child(5) { left: 50%; animation-delay: 8s; }
    .crypto-coin:nth-child(6) { left: 60%; animation-delay: 10s; width: 20px; height: 20px; }
    .crypto-coin:nth-child(7) { left: 70%; animation-delay: 12s; }
    .crypto-coin:nth-child(8) { left: 80%; animation-delay: 14s; width: 40px; height: 40px; }


    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(5px); /* Add blur for glass effect */
    }
    
    .neon-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.4); }
    .neon-red { color: #ff3b3b; text-shadow: 0 0 10px rgba(255, 59, 59, 0.4); }
    
    .stat-box { background: #161a1e; padding: 10px; border-radius: 12px; text-align: center; border: 1px solid #2d3339; }
    
    .stButton>button {
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        color: black !important; font-weight: bold !important; border-radius: 12px !important;
    }

    /* Center login card */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        z-index: 10;
        position: relative;
    }
    .login-card {
        background: rgba(0, 0, 0, 0.7); /* Darker background for login card */
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. WIDGETS ---
def draw_live_charts():
    components.html("""
    <div style="height:400px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {"interval": "1m", "width": "100%", "isTransparent": true, "height": "100%", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "locale": "en", "colorTheme": "dark"}
    </script></div>""", height=400)

# --- 4. PANELS ---
def admin_hub():
    st.markdown("<h2 class='neon-green'>👨‍💻 MASTER ADMIN</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📢 New Signal", "🚨 Send Alert"])
    
    with tab1:
        with st.form("sig"):
            p = st.text_input("Pair"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("TP"); sl = st.text_input("SL")
            if st.form_submit_button("Post Signal"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Published!")

    with tab2:
        msg = st.text_area("Global Alert Message")
        if st.button("Broadcast Now"):
            db_conn.cursor().execute("INSERT INTO alerts (msg, time) VALUES (?,?)", (msg, datetime.now().strftime("%H:%M")))
            db_conn.commit(); st.success("Sent!")

def user_hub():
    # 1. Ticker Tape
    components.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    # 2. Live Alerts
    alerts = pd.read_sql("SELECT * FROM alerts ORDER BY id DESC LIMIT 1", db_conn)
    for _, a in alerts.iterrows():
        st.warning(f"🔔 ALERT: {a['msg']}")

    # 3. Market Stats Card
    st.markdown("### 📊 Market Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card"><small>Global Volatility</small><h2 class="neon-green">LOW</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><small>Success Rate</small><h2 style="color:#f0b90b;">94%</h2></div>', unsafe_allow_html=True)

    # 4. Active Signals
    st.markdown("### 🎯 VIP Trading Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn)
    if df.empty: st.info("Waiting for market setup...")
    for _, r in df.iterrows():
        color = "#00ff88" if r['side'] == "LONG" else "#ff3b3b"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{r['pair']}</b> <span style="color:{color}; font-weight:bold;">{r['side']}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; margin-top:10px; text-align:center;">
                <div class="stat-box"><small>Entry</small><br><b>{r['entry']}</b></div>
                <div class="stat-box"><small>Target</small><br><b class="neon-green">{r['tp']}</b></div>
                <div class="stat-box"><small>Stop</small><br><b class="neon-red">{r['sl']}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Live Technical Gauge
    st.markdown("### ⚡ Live Technical Analysis")
    draw_live_charts()

# --- 5. LOGIC ---
apply_pro_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Crypto Animation Background
    st.markdown('<div class="crypto-animation-bg">' + 
                ''.join([f'<div class="crypto-coin" style="left: {random.randint(0, 100)}%; animation-delay: {random.randint(0, 15)}s; width: {random.randint(20, 40)}px; height: {random.randint(20, 40)}px;"></div>' for _ in range(10)]) +
                '</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white;'>ELITE LOGIN</h1>", unsafe_allow_html=True)
    u = st.text_input("Username/Email").lower()
    p = st.text_input("Password", type="password")
    if st.button("SIGN IN"):
        st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # close login-card
    st.markdown('</div>', unsafe_allow_html=True) # close login-container
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_hub()
    else: user_hub()
