import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go
import time
import re

# --- 0. DATA PERSISTENCE & SYSTEM STABILIZER ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df.to_dict('records')
    return []

def format_currency(num):
    if num >= 1_000_000_000: return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000: return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000: return f"{num / 1_000:.1f}K"
    return f"{num:,.2f}"

# --- SRI LANKA GEO-DATA ---
SL_DATA = {
    "Colombo": ["Colombo 1-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Malabe", "Battaramulla"],
    "Gampaha": ["Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Veyangoda"],
    "Kalutara": ["Kalutara", "Panadura", "Horana", "Beruwala", "Matugama"],
    "Kandy": ["Kandy", "Peradeniya", "Katugastota", "Gampola", "Nawalapitiya"],
    "Matale": ["Matale", "Dambulla", "Sigiriya"],
    "Nuwara Eliya": ["Nuwara Eliya", "Hatton", "Talawakele"],
    "Galle": ["Galle", "Hikkaduwa", "Ambalangoda", "Karapitiya"],
    "Matara": ["Matara", "Akuressa", "Weligama"],
    "Hambantota": ["Hambantota", "Tangalle", "Beliatta"],
    "Jaffna": ["Jaffna", "Chavakachcheri"],
    "Mannar": ["Mannar"], "Vavuniya": ["Vavuniya"], "Mullaitivu": ["Mullaitivu"], "Kilinochchi": ["Kilinochchi"],
    "Batticaloa": ["Batticaloa"], "Ampara": ["Ampara", "Kalmunai"], "Trincomalee": ["Trincomalee"],
    "Kurunegala": ["Kurunegala", "Kuliyapitiya", "Narammala", "Pannala"],
    "Puttalam": ["Puttalam", "Chilaw", "Marawila"],
    "Anuradhapura": ["Anuradhapura", "Eppawala", "Kekirawa"], "Polonnaruwa": ["Polonnaruwa"],
    "Badulla": ["Badulla", "Bandarawela", "Hali-Ela"], "Moneragala": ["Moneragala", "Wellawaya"],
    "Ratnapura": ["Ratnapura", "Embilipitiya", "Balangoda"], "Kegalle": ["Kegalle", "Mawanella", "Warakapola"]
}

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Happy Shop | Ultimate Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE & DB (SYNC WITH ORIGINAL) ---
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv')
if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil": 100, "Crown 1": 50, "Kalkaya": 75}
if 'expenses' not in st.session_state: st.session_state.expenses = load_data('expenses.csv')
if 'audit_logs' not in st.session_state: st.session_state.audit_logs = load_data('audit.csv')
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 3. AUTH SYSTEM (SECURE EMAIL LOGIN) ---
def check_auth(u, p):
    if u == "happyshop@gmail.com" and p == "happy123":
        return True, "Owner", "Admin"
    for i in range(1, 6):
        if u == f"demo{i}@gmail.com" and p == f"demo{i}":
            return True, "Staff", f"Staff_{i}"
    return False, None, None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username (Email)")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            auth, role, name = check_auth(user, pw)
            if auth:
                st.session_state.authenticated, st.session_state.user_role, st.session_state.current_user = True, role, name
                st.rerun()
            else: st.error("Invalid Login Details")
    st.stop()

# --- 4. CSS (VIBRANT THEME) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .m-card { padding: 15px; border-radius: 12px; text-align: center; color: white; font-weight: bold; border: 1px solid #30363d; margin-bottom: 10px; }
    .bg-p { background: linear-gradient(135deg, #6c757d, #495057); } 
    .bg-c { background: linear-gradient(135deg, #28a745, #1e7e34); } 
    .bg-n { background: linear-gradient(135deg, #ffc107, #e0a800); color: black; } 
    .bg-x { background: linear-gradient(135deg, #dc3545, #bd2130); } 
    .bg-t { background: linear-gradient(135deg, #007bff, #0062cc); }
    .wa-btn { background-color: #25D366; color: white; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 14px; display: inline-block; }
    .ghost-tag { background: #6f42c1; color: white; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GHOST SWITCH (ADMIN ONLY) ---
if st.session_state.user_role == "Owner":
    with st.sidebar:
        st.markdown("### 🛠️ Ghost Switcher")
        staff_list = ["Admin"] + [f"Staff_{i}" for i in range(1, 6)]
        switch_to = st.selectbox("Switch View To:", staff_list)
        if st.button("Confirm Switch"):
            st.session_state.current_user = switch_to
            st.toast(f"Active User: {switch_to}")

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.current_user}**")
    st.markdown("---")
    menu = st.selectbox("Navigation", ["🏠 Dashboard", "🧾 Orders", "📊 Inventory", "💰 Finance & Payroll", "📈 Strategy & AI"])
    
    sub = ""
    if menu == "🧾 Orders":
        sub = st.radio("Order Actions", ["New Order", "View Leads", "Bulk Courier Sync"])
    elif menu == "💰 Finance & Payroll":
        sub = st.radio("Financials", ["Expense Tracker", "Staff Payroll"])

# --- 7. DASHBOARD & FORECAST ---
if menu == "🏠 Dashboard":
    st.title(f"🚀 Business Control Center - {st.session_state.current_user}")
    
    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="m-card bg-p">PENDING<br><span style="font-size:24px">{get_count("pending")}</span></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="m-card bg-c">CONFIRMED<br><span style="font-size:24px">{get_count("confirm")}</span></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="m-card bg-n">NO ANSWER<br><span style="font-size:24px">{get_count("noanswer")}</span></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="m-card bg-x">CANCELLED<br><span style="font-size:24px">{get_count("cancel")}</span></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="m-card bg-t">TOTAL LEADS<br><span style="font-size:24px">{len(st.session_state.orders)}</span></div>', unsafe_allow_html=True)

    # Inventory Forecast Logic
    st.subheader("🤖 Smart Inventory Forecast")
    df_orders = pd.DataFrame(st.session_state.orders)
    if not df_orders.empty:
        # Calculate daily sales velocity
        df_confirmed = df_orders[df_orders['status'] == 'confirm']
        if not df_confirmed.empty:
            velocity = len(df_confirmed) / 30 # monthly average velocity
            cols = st.columns(len(st.session_state.stocks))
            for i, (item, qty) in enumerate(st.session_state.stocks.items()):
                days = int(qty / velocity) if velocity > 0 else 999
                color = "🔴" if days < 5 else "🟢"
                cols[i].metric(item, f"{qty} units", f"{days} days left {color}")

# --- 8. ORDERS (COMPLETE LOGIC) ---
elif menu == "🧾 Orders":
    if sub == "New Order":
        st.subheader("✨ New Order Entry")
        
        # Smart Parser Box
        with st.expander("📋 Smart Paste (Extract from WhatsApp)"):
            raw_text = st.text_area("Paste Customer WhatsApp message here...")
            if st.button("Parse Data"):
                phone_match = re.search(r'(\d{10})', raw_text)
                st.session_state.p_name = raw_text.split('\n')[0] if raw_text else ""
                st.session_state.p_phone = phone_match.group(1) if phone_match else ""
                st.session_state.p_addr = " ".join(raw_text.split('\n')[1:]) if len(raw_text.split('\n')) > 1 else ""
                st.success("Form Auto-filled!")

        with st.form("new_order_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Name", value=st.session_state.get('p_name', ""))
            phone = col1.text_input("Phone", value=st.session_state.get('p_phone', ""))
            address = col1.text_area("Full Address", value=st.session_state.get('p_addr', ""))
            
            dist = col2.selectbox("District", list(SL_DATA.keys()))
            city = col2.selectbox("City", SL_DATA[dist])
            prod = col2.selectbox("Product", list(st.session_state.stocks.keys()))
            courier = col2.selectbox("Courier", ["Royal Express", "Koombiyo", "Domex", "Pronto"])
            price = col2.number_input("Price (LKR)", value=2500)
            
            if st.form_submit_button("🚀 Save & Confirm Order"):
                oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                new_ord = {
                    "id": oid, "name": name, "phone": phone, "addr": address, "dist": dist, "city": city,
                    "prod": prod, "total": price, "status": "pending", "date": str(date.today()),
                    "courier": courier, "staff": st.session_state.current_user, "notes": "", "cancel_reason": ""
                }
                st.session_state.orders.append(new_ord)
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                st.balloons()
                st.success(f"Order {oid} saved successfully!")

    elif sub == "View Leads":
        st.subheader("📋 Lead Manager")
        search = st.text_input("🔍 Search Leads (Name / Phone / ID)")
        df = pd.DataFrame(st.session_state.orders)
        
        if not df.empty:
            if search:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            
            for idx, row in df.iterrows():
                # Risk Analysis
                risk = "🟢 SAFE"
                if any(o['phone'] == row['phone'] and o['status'] == 'return' for o in st.session_state.orders):
                    risk = "🔴 HIGH RETURN RISK"

                with st.expander(f"📦 {row['id']} | {row['name']} | {row['status'].upper()} | {risk}"):
                    # WhatsApp Link
                    wa_url = f"https://wa.me/94{row['phone'][1:]}?text=Hi {row['name']}, Happy Shop here."
                    st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">💬 WhatsApp Customer</a>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    new_st = c1.selectbox("Update Status", ["pending", "confirm", "noanswer", "hold", "cancel", "shipped"], key=f"st_{idx}")
                    
                    # Logic for cancel reasons
                    reason = ""
                    if new_st == "cancel":
                        reason = c1.selectbox("Reason", ["Price", "Late", "Fake", "Change Mind"], key=f"re_{idx}")
                    
                    new_notes = c2.text_area("Internal Notes", row.get('notes', ""), key=f"nt_{idx}")
                    
                    if st.button("Save Updates", key=f"btn_{idx}"):
                        st.session_state.orders[idx]['status'] = new_st
                        st.session_state.orders[idx]['notes'] = new_notes
                        if new_st == "cancel": st.session_state.orders[idx]['cancel_reason'] = reason
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.rerun()

# --- 9. FINANCE & PAYROLL (FEATURE 39) ---
elif menu == "💰 Finance & Payroll":
    if sub == "Staff Payroll":
        st.title("💸 Staff Commission & Salary")
        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            summary = df[df['status'] == 'confirm'].groupby('staff').size().reset_index(name='Total_Confirms')
            summary['Base_Salary'] = 30000
            summary['Commission'] = summary['Total_Confirms'] * 50
            summary['Final_Payable'] = summary['Base_Salary'] + summary['Commission']
            st.table(summary)

# --- 10. INVENTORY ---
elif menu == "📊 Inventory":
    st.title("📦 Current Stock Status")
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Item Name", "Quantity Available"]))

# --- LOGOUT ---
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.caption(f"Enterprise v5.5 | {date.today()}")
