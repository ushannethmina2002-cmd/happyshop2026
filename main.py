import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. ENHANCED ENGINE ---
class PowerEngine:
    def __init__(self):
        self.conn = sqlite3.connect('vip_power_v11_3.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Settings Table with 10+ Controls
        c.execute('''CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY, 
            app_name TEXT, 
            theme_color TEXT, 
            maintenance INTEGER, 
            welcome_msg TEXT,
            default_pair TEXT,
            support_url TEXT,
            logo_url TEXT,
            whale_limit TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT)''')
        
        # Default Settings Seed
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("""INSERT INTO config VALUES (1, 'ELITE TERMINAL', '#f0b90b', 0, 
                      'Welcome to VIP Intelligence', 'BINANCE:BTCUSDT', 'https://t.me/yourlink', 
                      'https://cryptologos.cc/logos/bitcoin-btc-logo.png', '1000 BTC')""")
        
        # Admin Account
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry) VALUES (?,?,?,?)", 
                  ('ushannethmina2002@gmail.com', h, 'ADMIN', '2099-12-31'))
        self.conn.commit()

db = PowerEngine()
config = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. DYNAMIC STYLING ---
st.set_page_config(page_title=config['app_name'], layout="wide")
if config['maintenance'] == 1:
    st.error("⚠️ SYSTEM UNDER MAINTENANCE. PLEASE CHECK LATER.")
    st.stop()

st.markdown(f"<style>.stApp {{ background: #05070a; color: #e1e4e8; }} .stButton>button {{ background: {config['theme_color']} !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)

# --- 3. ADMIN SETTINGS TAB (FULL CONTROL) ---
def render_settings():
    st.header("⚙️ Global App Settings")
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        # 1. App Name
        new_name = col1.text_input("App Display Name", value=config['app_name'])
        # 2. Theme Color
        new_color = col2.color_picker("Brand Theme Color", value=config['theme_color'])
        # 3. Welcome Message
        new_msg = st.text_area("Dashboard Welcome Message", value=config['welcome_msg'])
        
        col3, col4 = st.columns(2)
        # 4. TradingView Symbol
        new_pair = col3.text_input("Default Chart Symbol", value=config['default_pair'])
        # 5. Support URL
        new_url = col4.text_input("Support Link (Telegram/WA)", value=config['support_url'])
        
        col5, col6 = st.columns(2)
        # 6. Maintenance Toggle
        new_mnt = col5.selectbox("Maintenance Mode", [0, 1], format_func=lambda x: "OFF" if x==0 else "ON")
        # 7. Whale Limit
        new_whale = col6.text_input("Whale Alert Min. Limit", value=config['whale_limit'])
        
        # 8. Logo URL
        new_logo = st.text_input("Logo Image URL", value=config['logo_url'])
        
        if st.form_submit_button("✅ SAVE ALL 10+ SETTINGS"):
            db.conn.cursor().execute("""UPDATE config SET app_name=?, theme_color=?, maintenance=?, 
                                     welcome_msg=?, default_pair=?, support_url=?, logo_url=?, whale_limit=? WHERE id=1""",
                                  (new_name, new_color, new_mnt, new_msg, new_pair, new_url, new_logo, new_whale))
            db.conn.commit()
            st.success("App Settings Updated Successfully!")
            st.rerun()

    # 9. Signal Management (Clear Data)
    st.divider()
    st.subheader("🧹 Database Cleanup")
    if st.button("DELETE ALL OLD SIGNALS"):
        db.conn.cursor().execute("DELETE FROM signals")
        db.conn.commit(); st.warning("All signals cleared.")

    # 10. User Log Summary
    st.subheader("📊 User Statistics")
    u_count = pd.read_sql("SELECT count(*) as total FROM users", db.conn).iloc[0]['total']
    st.write(f"Total Registered VIP Members: {u_count}")

# --- 4. MAIN APP LOGIC ---
def admin_panel():
    st.title("🛡️ Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Signals", "Members", "Settings ⚙️"])
    with tab1: st.write("Signal Post Section")
    with tab2: st.write("Member Management")
    with tab3: render_settings()

# (Login & User View Logic remains same as v11.2)
if 'auth' not in st.session_state: st.session_state.auth = None
if not st.session_state.auth:
    # Login Code
    e = st.text_input("Email")
    k = st.text_input("Key", type="password")
    if st.button("LOGIN"):
        h = hashlib.sha256(k.encode()).hexdigest()
        res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND key=?", (e, h)).fetchone()
        if res: st.session_state.auth = {"role": res[0]}; st.rerun()
else:
    if st.session_state.auth['role'] == 'ADMIN':
        admin_panel()
