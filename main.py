import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('signals_pro_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_activity (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, pair TEXT, action_time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    # Default Settings
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('app_name', 'Crypto Pro Hub')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_pw', '2008')")
    conn.commit()
    return conn

db_conn = init_db()

def get_setting(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else ""

# --- 2. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title(f"🔐 {get_setting('app_name')} Login")
    email = st.text_input("Gmail Address").lower()
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and pw == get_setting('admin_pw'):
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, True, email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, False, email
            st.rerun()

# --- 3. ADMIN PAGES ---

def admin_dashboard():
    st.title("📊 Overview Dashboard")
    c1, c2, c3 = st.columns(3)
    total_s = pd.read_sql("SELECT COUNT(*) FROM signals", db_conn).values[0][0]
    active_s = pd.read_sql("SELECT COUNT(*) FROM signals WHERE status='Active'", db_conn).values[0][0]
    users_v = pd.read_sql("SELECT COUNT(*) FROM user_activity", db_conn).values[0][0]
    
    c1.metric("මුළු සිග්නල්", total_s)
    c2.metric("දැනට Active", active_s)
    c3.metric("Trade එකතු වූ වාර", users_v)
    
    st.subheader("පසුගිය යූසර් ක්‍රියාකාරකම්")
    st.table(pd.read_sql("SELECT email, pair, action_time FROM user_activity ORDER BY id DESC LIMIT 5", db_conn))

def admin_settings():
    st.title("⚙️ App Control Settings")
    new_name = st.text_input("App Name එක වෙනස් කරන්න", get_setting('app_name'))
    new_pw = st.text_input("Admin Password එක වෙනස් කරන්න", get_setting('admin_pw'))
    if st.button("Save Settings"):
        db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (new_name,))
        db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='admin_pw'", (new_pw,))
        db_conn.commit()
        st.success("Settings saved! පේජ් එක Refresh කරන්න.")

# --- 4. MAIN NAVIGATION ---
if not st.session_state.logged_in:
    login()
else:
    app_title = get_setting('app_name')
    st.sidebar.title(app_title)
    
    if st.session_state.is_admin:
        menu = st.sidebar.radio("Admin Menu", ["🏠 Dashboard", "📢 Signal Manager", "👥 User Activity", "⚙️ Settings"])
        
        if menu == "🏠 Dashboard": admin_dashboard()
        elif menu == "📢 Signal Manager":
            st.title("📢 Signal Management")
            with st.form("new_s", clear_on_submit=True):
                p = st.text_input("Pair")
                s = st.selectbox("Side", ["LONG", "SHORT"])
                en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
                if st.form_submit_button("Post Signal"):
                    db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, time) VALUES (?,?,?,?,?,?,?)",
                                             (p.upper(), s, en, tp, sl, "Active", datetime.now().strftime("%H:%M")))
                    db_conn.commit()
                    st.success("පල කළා!")
            df = pd.read_sql("SELECT * FROM signals", db_conn)
            edited = st.data_editor(df, num_rows="dynamic")
            if st.button("Save Changes"):
                edited.to_sql('signals', db_conn, if_exists='replace', index=False)
                st.rerun()
        elif menu == "👥 User Activity":
            st.title("👥 User Activity Logs")
            st.dataframe(pd.read_sql("SELECT * FROM user_activity ORDER BY id DESC", db_conn), use_container_width=True)
        elif menu == "⚙️ Settings": admin_settings()
    else:
        st.title(f"🚀 {app_title} Live Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        for i, row in df.iterrows():
            st.info(f"📊 {row['side']} {row['pair']} | Entry: {row['entry']} | TP: {row['tp']}")
            if st.button(f"✅ I'm In ({row['pair']})", key=f"u_{row['id']}"):
                db_conn.cursor().execute("INSERT INTO user_activity (email, pair, action_time) VALUES (?,?,?)",
                                         (st.session_state.user_email, row['pair'], datetime.now().strftime("%H:%M:%S")))
                db_conn.commit()
                st.toast("Admin දැනුවත් කළා!")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
