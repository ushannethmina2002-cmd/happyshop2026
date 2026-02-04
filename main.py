import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE SETUP (ඇප් එක ඇතුළෙම ඩේටාබේස් එක සෑදීම) ---
def init_db():
    conn = sqlite3.connect('signals_data.db', check_same_thread=False)
    c = conn.cursor()
    # සිග්නල් ගබඩා කරන ටේබල් එක
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, 
                  status TEXT, time TEXT)''')
    # යූසර්ලා 'I'm In' එබූ විට වාර්තා වන ටේබල් එක
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_email TEXT, pair TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. CSS FOR STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .signal-card {
        background-color: #1e212b;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #f0b90b;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Crypto Pro Secure Login")
    email = st.text_input("Gmail Address").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login Now"):
        if email == "ushan2008@gmail.com" and password == "2008":
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
            st.error("විස්තර වැරදියි. නැවත උත්සාහ කරන්න.")

# --- 4. ADMIN PANEL ---
def admin_panel():
    st.title("👨‍💼 Admin Control (Internal DB)")
    t1, t2 = st.tabs(["📢 Post Signal", "📊 View Active Trades"])
    
    with t1:
        with st.form("add_sig", clear_on_submit=True):
            pair = st.text_input("Pair (BTC/USDT)")
            side = st.selectbox("Side", ["LONG", "SHORT"])
            en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            if st.form_submit_button("Publish Signal"):
                c = db_conn.cursor()
                c.execute("INSERT INTO signals (pair, side, entry, tp, sl, status, time) VALUES (?,?,?,?,?,?,?)",
                          (pair.upper(), side, en, tp, sl, "Active", datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.success(f"{pair} Signal එක සේව් වුණා!")

    with t2:
        st.subheader("Traders Activity")
        logs = pd.read_sql("SELECT * FROM user_logs", db_conn)
        st.dataframe(logs, use_container_width=True)
        if st.button("Clear Logs"):
            db_conn.cursor().execute("DELETE FROM user_logs")
            db_conn.commit()
            st.rerun()

# --- 5. USER DASHBOARD ---
def user_dashboard():
    st.title("🚀 Live Trading Signals")
    # ඩේටාබේස් එකෙන් සිග්නල් කියවීම
    df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
    
    if not df.empty:
        for i, row in df.iterrows():
            card_color = "#00ffcc" if row['side'] == "LONG" else "#ff4b4b"
            st.markdown(f"""
            <div class="signal-card" style="border-left-color: {card_color};">
                <h3 style="color:{card_color};">{row['side']} {row['pair']}</h3>
                <p><b>Entry:</b> {row['entry']} | <b>TP:</b> {row['tp']} | <b>SL:</b> {row['sl']}</p>
                <small>Time: {row['time']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ I'm In ({row['pair']})", key=f"btn_{row['id']}"):
                c = db_conn.cursor()
                c.execute("INSERT INTO user_logs (user_email, pair, time) VALUES (?,?,?)",
                          (st.session_state.user_email, row['pair'], datetime.now().strftime("%H:%M:%S")))
                db_conn.commit()
                st.toast("Admin දැනුවත් කළා!")
    else:
        st.info("දැනට සක්‍රීය සිග්නල් කිසිවක් නැත.")

# --- NAVIGATION ---
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Crypto Pro")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.is_admin:
        mode = st.sidebar.radio("Navigation", ["Admin", "Dashboard"])
        if mode == "Admin": admin_panel()
        else: user_dashboard()
    else:
        user_dashboard()
