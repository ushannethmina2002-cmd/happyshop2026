import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE & LOGIC ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v18.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('maintenance', 'OFF'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

def get_sys(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else "OFF"

# --- 2. THE "PHOTO-MATCH" UI (CSS) ---
def apply_elite_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    
    .stApp { background: radial-gradient(circle at 20% 20%, #1e2329 0%, #0b0e11 100%); color: #ffffff; }
    
    /* Neon Cards from Photo */
    .app-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .neon-text { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); font-weight: bold; }
    
    /* Neon Button Style */
    .stButton>button {
        background: #ffffff !important;
        color: #000 !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255,255,255,0.2);
    }
    
    /* Status Badges */
    .badge { padding: 4px 12px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    .long { background: #00ff88; color: #000; }
    .short { background: #ff3b3b; color: #fff; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: #0b0e11 !important; border-right: 1px solid #2d3339; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DYNAMIC WIDGETS ---
def ticker_tape():
    components.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}
    </script>""", height=50)

# --- 4. ADMIN HUB ---
def admin_hub():
    st.markdown("<h2 class='neon-text'>ADMINI HUB</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Stats", "🎯 Signals", "⚙️ Control"])
    
    with tab1:
        st.write("### Platform Performance")
        df = pd.read_sql("SELECT * FROM signals", db_conn)
        st.dataframe(df, use_container_width=True)

    with tab2:
        with st.form("sig"):
            p = st.text_input("Name (Pair)"); s = st.selectbox("Role (Side)", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("Target"); sl = st.text_input("Stop")
            if st.form_submit_button("NEON BUTTON"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.rerun()
                
    with tab3:
        st.write("### Maintenance Mode")
        mnt = st.toggle("System Maintenance", value=(get_sys('maintenance') == "ON"))
        if st.button("Apply Maintenance"):
            val = "ON" if mnt else "OFF"
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='maintenance'", (val,))
            db_conn.commit(); st.rerun()

# --- 5. USER HUB ---
def user_hub():
    if get_sys('maintenance') == "ON":
        st.error("🛠️ SYSTEM UNDER MAINTENANCE. PLEASE WAIT.")
        st.stop()
        
    st.markdown("<h1 style='text-align:center;'>CRYPTO ELITE PRO</h1>", unsafe_allow_html=True)
    ticker_tape()
    
    menu = st.sidebar.radio("Navigation", ["🎯 Signals", "📈 Markets", "📓 Journals"])
    
    if menu == "🎯 Signals":
        st.write("### Active Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        for _, r in df.iterrows():
            b_class = "long" if r['side'] == "LONG" else "short"
            st.markdown(f"""
            <div class="app-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:1.2em;">{r['pair']}</b>
                    <span class="badge {b_class}">{r['side']}</span>
                </div>
                <div style="margin-top:15px; display:grid; grid-template-columns:1fr 1fr 1fr;">
                    <div><small style="color:#848e9c;">Entry</small><br><b>{r['entry']}</b></div>
                    <div><small style="color:#848e9c;">Target</small><br><b style="color:#00ff88;">{r['tp']}</b></div>
                    <div><small style="color:#848e9c;">Stop</small><br><b style="color:#ff3b3b;">{r['sl']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif menu == "📈 Markets":
        components.html('<div style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"tv"});</script></div>', height=500)

# --- 6. MAIN SYSTEM ---
apply_elite_ui()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.8,1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center;'>LOGIN</h1>", unsafe_allow_html=True)
        e = st.text_input("Gmail").lower()
        p = st.text_input("Password", type="password")
        if st.button("NEON BUTTON"):
            st.session_state.update({"logged_in": True, "is_admin": (e=="ushan2008@gmail.com"), "user_email": e})
            st.rerun()
else:
    if st.sidebar.button("LOGOUT"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_hub()
    else: user_hub()
