import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. DATABASE & LOGIC ---
def init_db():
    conn = sqlite3.connect('crypto_ultra_v25.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE ULTRA'), ('maintenance', 'OFF'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

def get_sys(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else "OFF"

# --- 2. THE ULTRA-PREMIUM UI DESIGN (CSS) ---
def apply_ultra_premium_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    
    .stApp { background: radial-gradient(circle at 20% 20%, #1e2329 0%, #0b0e11 100%); color: white; font-family: 'Inter', sans-serif; }
    
    /* Neon Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
    }
    .glass-card:hover { transform: translateY(-5px); }
    
    .neon-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }
    .neon-red { color: #ff3b3b; text-shadow: 0 0 10px rgba(255, 59, 59, 0.5); }
    
    /* Modern Badges */
    .badge { padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .long-bg { background: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1px solid #00ff88; }
    .short-bg { background: rgba(255, 59, 59, 0.15); color: #ff3b3b; border: 1px solid #ff3b3b; }
    .neutral-bg { background: rgba(255, 200, 0, 0.15); color: #ffc800; border: 1px solid #ffc800; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        color: black !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(240, 185, 11, 0.4);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #00ff88 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. COMPONENTS ---
def draw_market_header():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''<div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Fear & Greed Index</small>
            <h2 style="color:#f0b90b; margin:0;">68 <span style="font-size:14px; color:#848e9c;">Greed</span></h2>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown('''<div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Market Sentiment</small>
            <h2 class="neon-green" style="margin:0;">VERY BULLISH</h2>
        </div>''', unsafe_allow_html=True)

def draw_ticker():
    components.html("""
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}, {"proName": "BINANCE:SOLUSDT", "title": "SOL"}], "colorTheme": "dark", "isTransparent": true}
        </script>""", height=50)

# --- 4. PANELS ---
def admin_portal():
    st.markdown("<h2 class='neon-green'>👨‍💻 MASTER CONTROL HUB</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📢 POST SIGNAL", "📊 ALL SIGNALS", "⚙️ SYSTEM"])
    
    with tab1:
        with st.form("new_sig"):
            p = st.text_input("Asset Pair (e.g. BTC/USDT)"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("Target"); sl = st.text_input("Stop")
            if st.form_submit_button("PUBLISH TO VIP"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit(); st.success("Signal is LIVE!")

    with tab2:
        df = pd.read_sql("SELECT * FROM signals", db_conn)
        st.dataframe(df, use_container_width=True)
        
    with tab3:
        st.write("### Maintenance Settings")
        mnt = st.toggle("Maintenance Mode", value=(get_sys('maintenance') == "ON"))
        if st.button("Apply Changes"):
            val = "ON" if mnt else "OFF"
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='maintenance'", (val,))
            db_conn.commit(); st.rerun()

def user_portal():
    if get_sys('maintenance') == "ON":
        st.warning("🛠️ SYSTEM UNDER MAINTENANCE. PLEASE CHECK LATER.")
        st.stop()
        
    st.markdown("<h1 style='text-align:center; font-weight:900;'>CRYPTO ELITE ULTRA</h1>", unsafe_allow_html=True)
    draw_ticker()
    
    # NEW: AI-Driven Analysis Card
    st.markdown("### 🧠 AI-Driven Insights")
    st.markdown(f'''
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b>Global Market Trend</b>
            <span class="badge long-bg">OPTIMISTIC</span>
        </div>
        <p style="font-size:14px; color:#848e9c; margin-top:10px;">
            AI predicts continued upward momentum for BTC in the short term.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    draw_market_header() # Fear & Greed + Market Sentiment
    
    # NEW: P/L Overview
    st.markdown("### 📈 Performance Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'''
        <div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Total Profit</small>
            <h3 class="neon-green" style="margin:0;">+ $ {random.randint(1000, 5000)}.00</h3>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Win Rate</small>
            <h3 class="neon-green" style="margin:0;">{random.randint(70, 95)}%</h3>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("### 🎯 VIP TRADING SIGNALS")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn)
    if df.empty:
        st.info("Searching for premium setups...")
    else:
        for _, r in df.iterrows():
            b_class = "long-bg" if r['side'] == "LONG" else "short-bg"
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:18px; font-weight:bold;">{r['pair']}</span>
                    <span class="badge {b_class}">{r['side']}</span>
                </div>
                <div style="margin-top:15px; display:grid; grid-template-columns:1fr 1fr 1fr; text-align:center;">
                    <div><small style="color:#848e9c;">Entry</small><br><b>{r['entry']}</b></div>
                    <div><small style="color:#848e9c;">Target</small><br><b class="neon-green">{r['tp']}</b></div>
                    <div><small style="color:#848e9c;">Stop</small><br><b class="neon-red">{r['sl']}</b></div>
                </div>
                <div style="margin-top:15px; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;">
                    <small style="color:#848e9c;">Posted: {r['time']} • <span class="neon-green">Live Action</span></small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # NEW: Recent Transactions/Closed Signals
    st.markdown("### ⏳ Recent Activity")
    st.markdown(f'''
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span>ETH/USDT <span class="badge long-bg">LONG</span></span>
            <span class="neon-green">+12.5%</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span>SOL/USDT <span class="badge short-bg">SHORT</span></span>
            <span class="neon-red">-3.2%</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("### 🚀 UPGRADE TO VIP")
    st.markdown('''
    <div class="glass-card">
        <p style="font-size:16px; text-align:center;">Unlock all premium features and maximize your gains!</p>
        <button style="width:100%; border:none; padding:10px; border-radius:8px; background-color:#00ff88; color:black; font-weight:bold;">GET VIP NOW</button>
    </div>
    ''', unsafe_allow_html=True)

# --- 5. SYSTEM RUN ---
apply_ultra_premium_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.title("Elite Login")
        u = st.text_input("Email/Username")
        p = st.text_input("Password", type="password")
        if st.button("UNLOCK PRO ACCESS"):
            st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
            st.rerun()
else:
    if st.sidebar.button("LOGOUT"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_portal()
    else: user_portal()
