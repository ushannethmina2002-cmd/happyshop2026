import streamlit as st
import pandas as pd
from datetime import datetime

# පිටුවේ පෙනුම සැකසීම
st.set_page_config(page_title="Crypto Signals Pro", layout="centered")

# දත්ත තාවකාලිකව තබා ගැනීමට (Database එකක් නැති නිසා)
if 'signals' not in st.session_state:
    st.session_state.signals = []

# --- 1. LOGIN පද්ධතිය ---
def login_page():
    st.title("🚀 Crypto Signals Login")
    email = st.text_input("Email (Admin: ushan2008@gmail.com)")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and password == "2008":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.rerun()
        elif email != "" and password != "":
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.rerun()
        else:
            st.error("කරුණාකර නිවැරදි විස්තර ඇතුළත් කරන්න")

# --- 2. ADMIN PANEL (සිග්නල් පෝස්ට් කිරීමට) ---
def admin_panel():
    st.header("⚡ Admin Control Panel")
    with st.form("post_signal"):
        pair = st.text_input("Coin Pair (උදා: BTC/USDT)")
        trade_type = st.selectbox("Type", ["LONG", "SHORT"])
        entry = st.text_input("Entry Zone")
        tp = st.text_input("Take Profit Target")
        sl = st.text_input("Stop Loss")
        
        if st.form_submit_button("🚀 Broadcast Signal"):
            new_sig = {
                "pair": pair.upper(),
                "type": trade_type,
                "entry": entry,
                "tp": tp,
                "sl": sl,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.signals.insert(0, new_sig)
            st.success(f"{pair} Signal එක පල කරා!")

# --- 3. USER SIGNALS (සිග්නල් පෙන්වන තැන) ---
def user_dashboard():
    st.title("📈 Active Crypto Signals")
    if not st.session_state.signals:
        st.info("දැනට සක්‍රීය සිග්නල් නැත. Admin පණිවිඩයක් එවන තෙක් රැඳී සිටින්න.")
    else:
        for s in st.session_state.signals:
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid orange; margin-bottom: 10px;">
                <h3 style="color: orange; margin:0;">{s['pair']} - {s['type']}</h3>
                <p style="margin:5px 0;"><b>Entry:</b> {s['entry']} | <b>TP:</b> {s['tp']} | <b>SL:</b> {s['sl']}</p>
                <small style="color: gray;">🕒 Posted: {s['time']}</small>
            </div>
            """, unsafe_allow_html=True)

# --- 4. RISK CALCULATOR ---
def risk_calculator():
    st.header("🧮 Position Size Calculator")
    balance = st.number_input("Wallet Balance ($)", min_value=0.0, step=10.0)
    risk_p = st.slider("Risk (%)", 1, 10, 2)
    if balance > 0:
        risk_val = balance * (risk_p / 100)
        st.info(f"ඔබ මේ ට්‍රේඩ් එකට වැය කළ යුතු උපරිම මුදල: **${risk_val:.2f}**")

# --- MAIN LOGIC ---
if 'logged_in' not in st.session_state:
    login_page()
else:
    # Sidebar Menu
    menu = ["Signals", "Risk Calculator"]
    if st.session_state.is_admin:
        menu.insert(0, "Admin Panel")
    
    choice = st.sidebar.radio("Navigation", menu)
    
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        
    if choice == "Admin Panel":
        admin_panel()
    elif choice == "Signals":
        user_dashboard()
    elif choice == "Risk Calculator":
        risk_calculator()
