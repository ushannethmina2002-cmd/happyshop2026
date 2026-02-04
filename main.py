import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE & SUBSCRIPTION LOGIC ---
class EliteMasterEngine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_final_v6.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        # Settings
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, 
            announcement TEXT, theme_color TEXT)''')
        # Users with Expiry Date
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, expiry_date DATE)''')
        # Signals
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, reason TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'CRYPTO ELITE VIP', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'Welcome to the Premium VIP Terminal', '#f0b90b')")
        
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            # Admin gets a very long expiry date
            long_expiry = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d')
            c.execute("INSERT INTO users (username, password, role, status, expiry_date) VALUES (?,?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE', long_expiry))
        self.conn.commit()

    def get_config(self):
        return pd.read_sql("SELECT * FROM settings WHERE id=1", self.conn).iloc[0]

engine = EliteMasterEngine()

# --- 2. DYNAMIC UI & STYLING ---
config = engine.get_config()
st.set_page_config(page_title=config['app_name'], layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    .stApp {{ background: #080a0c; color: #e1e4e8; font-family: 'Plus Jakarta Sans', sans-serif; }}
    .neon-gold {{ color: {config['theme_color']}; text-shadow: 0 0 10px {config['theme_color']}55; font-weight: 800; }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
    }}
    .expiry-tag {{ font-size: 12px; background: rgba(255,0,0,0.1); color: #ff4b4b; padding: 5px 10px; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. COMPONENTS ---
def live_price_ticker():
    st.components.v1.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}, {"proName": "BINANCE:SOLUSDT", "title": "SOL"}], "colorTheme": "dark", "isTransparent": true}
    </script>""", height=50)

def render_dashboard():
    live_price_ticker()
    col1, col2 = st.columns([0.1, 0.9])
    with col1: st.image(config['logo_url'], width=60)
    with col2: st.markdown(f"<h1 class='neon-gold'>{config['app_name']}</h1>", unsafe_allow_html=True)
    
    st.info(f"📢 {config['announcement']}")
    
    # Expiry Warning
    expiry_dt = datetime.strptime(st.session_state.user['expiry'], '%Y-%m-%d')
    days_left = (expiry_dt - datetime.now()).days
    if days_left <= 5:
        st.warning(f"⚠️ Your VIP access expires in {days_left} days. Please renew to avoid interruption.")

    st.subheader("🎯 Intelligence Signals")
    signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
    for _, s in signals.iterrows():
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between;">
                <b style="font-size:18px;">{s['pair']} | {s['type']}</b>
                <span style="color:{config['theme_color']};">Confidence: {s['confidence']}</span>
            </div>
            <p style="margin-top:10px;">{s['reason']}</p>
            <small style="color:#666;">Timeframe: {s['timeframe']} | ID: #{s['id']}</small>
        </div>
        """, unsafe_allow_html=True)

# --- 4. ADMIN CONTROL PANEL ---
def render_admin():
    st.title("🛡️ Admin Command Center")
    tab1, tab2, tab3 = st.tabs(["👥 VIP Members", "📢 Signals", "🎨 App Settings"])

    with tab1:
        st.subheader("Manage VIP Access")
        with st.form("add_user_form"):
            new_u = st.text_input("Member Email")
            new_p = st.text_input("Set Key", type="password")
            days = st.number_input("Subscription Days", min_value=1, value=30)
            if st.form_submit_button("Create VIP Account"):
                exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                try:
                    h = hashlib.sha256(new_p.encode()).hexdigest()
                    engine.conn.cursor().execute("INSERT INTO users (username, password, role, status, expiry_date) VALUES (?,?,?,?,?)",
                                                (new_u, h, 'USER', 'ACTIVE', exp))
                    engine.conn.commit(); st.success(f"Added! Access expires on {exp}")
                except: st.error("User already exists.")
        
        st.divider()
        users_df = pd.read_sql("SELECT username, expiry_date, status FROM users WHERE role='USER'", engine.conn)
        st.dataframe(users_df, use_container_width=True)

    with tab2:
        # Signal Creation (Same as before)
        with st.form("sig_f"):
            pair = st.text_input("Pair")
            st_type = st.selectbox("Type", ["Trend", "Breakout", "Alert"])
            tf = st.text_input("Timeframe")
            conf = st.select_slider("Confidence", ["Low", "High"])
            desc = st.text_area("Analysis")
            if st.form_submit_button("Broadcast"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, timeframe, confidence, reason, timestamp) VALUES (?,?,?,?,?,?)",
                                            (pair, st_type, tf, conf, desc, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Signal Published!")

    with tab3:
        # App Identity Settings (Name, Logo, Color)
        with st.form("set_f"):
            n = st.text_input("App Name", value=config['app_name'])
            l = st.text_input("Logo URL", value=config['logo_url'])
            clr = st.color_picker("Theme Color", value=config['theme_color'])
            ann = st.text_area("Announcement", value=config['announcement'])
            if st.form_submit_button("Save Settings"):
                engine.conn.cursor().execute("UPDATE settings SET app_name=?, logo_url=?, announcement=?, theme_color=? WHERE id=1", (n,l,ann,clr))
                engine.conn.commit(); st.success("Settings Updated!"); st.rerun()

# --- 5. AUTHENTICATION FLOW ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    _, lb, _ = st.columns([1, 1.2, 1])
    with lb:
        st.image(config['logo_url'], width=80)
        st.title(config['app_name'])
        u_in = st.text_input("Email")
        p_in = st.text_input("Key", type="password")
        if st.button("Login to VIP Portal"):
            h_in = hashlib.sha256(p_in.encode()).hexdigest()
            res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u_in, h_in)).fetchone()
            if res:
                exp_date = datetime.strptime(res[1], '%Y-%m-%d')
                if datetime.now() > exp_date and res[0] != 'ADMIN':
                    st.error("❌ Your membership has expired. Please contact Admin.")
                else:
                    st.session_state.user = {"email": u_in, "role": res[0], "expiry": res[1]}
                    st.rerun()
            else: st.error("Invalid Credentials.")
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None; st.rerun()
    
    if st.session_state.user['role'] == 'ADMIN':
        m = st.sidebar.radio("Nav", ["Member View", "Admin Panel"])
        if m == "Admin Panel": render_admin()
        else: render_dashboard()
    else:
        render_dashboard()
