import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# --- 1. CONFIGURATION & DATABASE (Firebase) ---
# කරුණාකර ඔයාගේ Firebase Realtime Database URL එක මෙතනට දාන්න
FIREBASE_URL = "https://your-project-id.firebaseio.com" 

def fb_get(path):
    res = requests.get(f"{FIREBASE_URL}/{path}.json")
    return res.json()

def fb_post(path, data):
    requests.post(f"{FIREBASE_URL}/{path}.json", json=data)

def fb_update(path, data):
    requests.patch(f"{FIREBASE_URL}/{path}.json", json=data)

# --- PAGE SETUP ---
st.set_page_config(page_title="Crypto Pro Hub", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: white; }
    .signal-card {
        background: #1e2329; padding: 20px; border-radius: 10px;
        border-left: 5px solid #f3ba2f; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ADMIN PANEL FUNCTIONS ---
def admin_panel():
    st.title("👨‍💼 Admin Command Center")
    tab1, tab2, tab3 = st.tabs(["📢 Post Signal", "👥 Trader Tracker", "📊 Performance"])

    with tab1:
        st.subheader("Broadcast New Signal")
        with st.form("sig_form", clear_on_submit=True):
            pair = st.text_input("Coin Pair")
            side = st.selectbox("Side", ["LONG", "SHORT"])
            entry = st.text_input("Entry Price")
            tp = st.text_input("Take Profit")
            sl = st.text_input("Stop Loss")
            if st.form_submit_button("🚀 Send Signal"):
                sig_id = datetime.now().strftime("%Y%m%d%H%M%S")
                data = {
                    "pair": pair.upper(), "side": side, "entry": entry,
                    "tp": tp, "sl": sl, "status": "Active", "time": datetime.now().strftime("%H:%M")
                }
                fb_update(f"signals/{sig_id}", data)
                st.success("Signal is Live!")

    with tab2:
        st.subheader("Live Trader Activity")
        logs = fb_get("trade_log")
        if logs:
            log_df = pd.DataFrame.from_dict(logs, orient='index')
            st.table(log_df)
            if st.button("📧 Send Daily Reports (Simulation)"):
                st.toast("Reports prepared for emails!")
        else:
            st.info("No users in trades yet.")

# --- 3. USER DASHBOARD ---
def user_dashboard():
    # Market Data
    btc_res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
    
    st.title("🛰️ Live Intelligence Hub")
    col1, col2 = st.columns(2)
    col1.metric("BTC Price", f"${float(btc_res['lastPrice']):,.2f}", f"{btc_res['priceChangePercent']}%")
    
    st.divider()
    
    # Signals Display
    st.subheader("🔥 Premium Signals")
    signals = fb_get("signals")
    if signals:
        for sid, s in signals.items():
            if s['status'] == "Active":
                color = "#00ffcc" if s['side'] == "LONG" else "#ff4b4b"
                with st.container():
                    st.markdown(f"""
                    <div class="signal-card" style="border-left-color: {color}">
                        <h3 style="color:{color}">{s['side']} {s['pair']}</h3>
                        <p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🚀 I'm In ({s['pair']})", key=sid):
                        log = {
                            "email": st.session_state.user_email,
                            "pair": s['pair'],
                            "time": datetime.now().strftime("%H:%M"),
                            "profit": "Calculating..."
                        }
                        fb_post("trade_log", log)
                        st.success("Joined! Admin will track your profit.")
    else:
        st.info("No active signals.")

# --- 4. LOGIN SYSTEM ---
def login():
    st.title("🔐 Crypto Pro Login")
    email = st.text_input("Gmail Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
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
            st.error("Invalid Login.")

# --- MAIN LOGIC ---
if not st.session_state.get('logged_in'):
    login()
else:
    menu = ["Signals", "Tools", "Leaderboard"]
    if st.session_state.is_admin:
        menu.insert(0, "Admin")
    
    choice = st.sidebar.radio("Navigation", menu)
    
    if choice == "Admin":
        admin_panel()
    elif choice == "Signals":
        user_dashboard()
    elif choice == "Tools":
        st.title("🧮 Trading Tools")
        # Risk Calc logic here...
    elif choice == "Leaderboard":
        st.title("🏆 Top Traders")
        st.write("1. @User_A (+250%)")

