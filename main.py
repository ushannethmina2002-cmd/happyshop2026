import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v21.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. ULTRA-PREMIUM CSS (MATCHING YOUR PHOTOS) ---
def apply_ultra_premium_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp { background: #0b0e11; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Premium Glass Card Style */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Neon Text & Badges */
    .neon-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
    .neon-red { color: #ff3b3b; text-shadow: 0 0 10px rgba(255, 59, 59, 0.3); }
    
    .status-badge {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .buy-bg { background: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1px solid #00ff88; }
    .sell-bg { background: rgba(255, 59, 59, 0.15); color: #ff3b3b; border: 1px solid #ff3b3b; }

    /* Bottom Nav Bar Simulation */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #161a1e;
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid #2d3339;
        z-index: 100;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        color: #000 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        height: 48px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PHOTO-SPECIFIC WIDGETS ---
def draw_market_header():
    # පින්තූරයේ තියෙන Market Overview කොටස
    st.markdown("### 📊 Market Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''<div class="glass-card">
            <small style="color:#848e9c;">Fear & Greed Index</small>
            <h2 style="color:#f0b90b; margin:0;">54 <span style="font-size:15px; color:#848e9c;">Neutral</span></h2>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown('''<div class="glass-card">
            <small style="color:#848e9c;">Market Sentiment</small>
            <h2 class="neon-green" style="margin:0;">BULLISH</h2>
        </div>''', unsafe_allow_html=True)

# --- 4. NAVIGATION LOGIC ---
def user_interface():
    st.markdown("<h2 style='text-align:center; font-weight:800;'>CRYPTO ELITE PRO</h2>", unsafe_allow_html=True)
    
    # පින්තූරයේ තියෙන Live Ticker Tape
    components.html("""
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}, {"proName": "BINANCE:SOLUSDT", "title": "SOL"}], "colorTheme": "dark", "isTransparent": true}
        </script>""", height=50)

    # 1. Dashboard Header
    draw_market_header()
    
    # 2. Signals Section (හරියටම පින්තූරයේ විදිහට)
    st.markdown("### 🎯 VIP Trading Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 10", db_conn)
    
    if df.empty:
        st.info("Analyzing markets for next signal...")
    else:
        for _, r in df.iterrows():
            badge_class = "buy-bg" if r['side'] == "LONG" else "sell-bg"
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:18px; font-weight:700;">{r['pair']}</span>
                    <span class="status-badge {badge_class}">{r['side']}</span>
                </div>
                <div style="margin-top:15px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:5px; text-align:center;">
                    <div><small style="color:#848e9c;">Entry</small><br><b>{r['entry']}</b></div>
                    <div><small style="color:#848e9c;">Target</small><br><b class="neon-green">{r['tp']}</b></div>
                    <div><small style="color:#848e9c;">Stop Loss</small><br><b class="neon-red">{r['sl']}</b></div>
                </div>
                <div style="margin-top:15px; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;">
                    <small style="color:#848e9c;">Posted: {r['time']} • <span class="neon-green">Live Action</span></small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Market Coins List
    st.markdown("### 📈 Top Assets")
    st.markdown("""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span><b>BTC</b> Bitcoin</span> <span class="neon-green">$96,432.10</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span><b>ETH</b> Ethereum</span> <span class="neon-green">$2,845.50</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span><b>SOL</b> Solana</span> <span class="neon-red">$142.12</span>
        </div>
    </div>
    <br><br><br>
    """, unsafe_allow_html=True)

# --- 5. MAIN APP ---
apply_ultra_premium_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login පේජ් එකත් පින්තූරවල තියෙන විදිහට හැදුවා
    _, col, _ = st.columns([1,3,1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center;'>ELITE</h1>", unsafe_allow_html=True)
        u = st.text_input("GMAIL")
        p = st.text_input("PASSWORD", type="password")
        if st.button("UNLOCK ACCESS"):
            st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    
    if st.session_state.is_admin:
        st.title("👨‍💻 Admin Hub")
        with st.form("new_sig"):
            pair = st.text_input("Pair (BTC/USDT)"); side = st.selectbox("Side", ["LONG", "SHORT"])
            ent = st.text_input("Entry"); tp = st.text_input("TP"); sl = st.text_input("SL")
            if st.form_submit_button("PUBLISH SIGNAL"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (pair,side,ent,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Live Now!")
    else:
        user_interface()
