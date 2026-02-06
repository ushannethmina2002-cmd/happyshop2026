import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go
import time
import re

# --- 0. DATA PERSISTENCE ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df.to_dict('records')
    return []

# --- 1. SYSTEM INITIALIZATION ---
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv')
if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil": 100, "Crown 1": 50, "Kalkaya": 75}
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
# Feature: Owner's Remote Control for Staff Permissions
if 'staff_perms' not in st.session_state:
    st.session_state.staff_perms = {"Can_Add": True, "Can_View": True, "Can_Print": True, "Can_Finance": False}

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

# --- 2. AUTHENTICATION ---
def check_auth(u, p):
    if u == "happyshop@gmail.com" and p == "happy123":
        return True, "Owner", "Admin"
    for i in range(1, 6):
        if u == f"demo{i}@gmail.com" and p == f"demo{i}":
            return True, "Staff", f"Staff_{i}"
    return False, None, None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            auth, role, name = check_auth(u, p)
            if auth:
                st.session_state.authenticated, st.session_state.user_role, st.session_state.current_user = True, role, name
                st.rerun()
    st.stop()

# --- 3. UI CONFIG ---
st.set_page_config(page_title="Happy Shop | Pro Control", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. SIDEBAR & GHOST SWITCH ---
with st.sidebar:
    st.title("HAPPY SHOP")
    st.write(f"Logged as: **{st.session_state.current_user}**")
    
    # OWNER'S MASTER CONTROL PANEL
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Staff Permissions"):
            st.session_state.staff_perms["Can_Add"] = st.checkbox("Allow Staff to Add Orders", value=True)
            st.session_state.staff_perms["Can_Print"] = st.checkbox("Allow Staff to Print/Dispatch", value=True)
            st.session_state.staff_perms["Can_Finance"] = st.checkbox("Allow Staff to see Payroll", value=False)
        
        staff_list = ["Admin", "Staff_1", "Staff_2", "Staff_3", "Staff_4", "Staff_5"]
        st.session_state.current_user = st.selectbox("Ghost Switch View", staff_list, index=staff_list.index(st.session_state.current_user))

    menu = st.selectbox("Menu", ["🏠 Dashboard", "🧾 Orders", "📊 Inventory", "💰 Finance"])

# --- 5. DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Enterprise Dashboard")
    df = pd.DataFrame(st.session_state.orders)
    c1, c2, c3, c4 = st.columns(4)
    if not df.empty:
        c1.metric("Total Leads", len(df))
        c2.metric("Confirmed", len(df[df['status'] == 'confirm']))
        c3.metric("RTS/Return", len(df[df['status'] == 'return']))
        c4.metric("Pending", len(df[df['status'] == 'pending']))

# --- 6. ORDERS MANAGEMENT (Unified for Admin & Staff) ---
elif menu == "🧾 Orders":
    tab1, tab2 = st.tabs(["➕ Add New Order", "📑 Lead Manager"])
    
    # ADD ORDER SECTION
    with tab1:
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Can_Add"]:
            st.subheader("Create Order / Lead")
            # Smart Parser Feature
            raw = st.text_area("Smart Paste WhatsApp Info")
            if st.button("Auto-Fill"):
                phone_match = re.search(r'(\d{10})', raw)
                st.session_state.tmp_name = raw.split('\n')[0] if raw else ""
                st.session_state.tmp_phone = phone_match.group(1) if phone_match else ""
                st.success("Details Parsed!")

            with st.form("add_order_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Customer Name", value=st.session_state.get('tmp_name', ""))
                phone = col1.text_input("Phone", value=st.session_state.get('tmp_phone', ""))
                addr = col1.text_area("Address")
                dist = col2.selectbox("District", list(SL_DATA.keys()))
                city = col2.selectbox("City", SL_DATA[dist])
                prod = col2.selectbox("Product", list(st.session_state.stocks.keys()))
                price = col2.number_input("Amount", value=2500)
                if st.form_submit_button("Save Order"):
                    new_id = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": new_id, "name": name, "phone": phone, "addr": addr, "dist": dist, "city": city,
                        "prod": prod, "total": price, "status": "pending", "date": str(date.today()),
                        "staff": st.session_state.current_user, "dispatch": "No"
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success("Order Added!")
        else:
            st.warning("Staff access to Add Orders is disabled by Admin.")

    # LEAD MANAGER SECTION
    with tab2:
        st.subheader("Manage Existing Leads")
        search = st.text_input("Search Name/Phone")
        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            if search:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            
            for idx, row in df.iterrows():
                with st.expander(f"Order {row['id']} - {row['name']} ({row['status']})"):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    # Status Update
                    new_st = c1.selectbox("Change Status", ["pending", "confirm", "cancel", "return", "shipped"], key=f"s_{idx}", index=0)
                    # Dispatch & Print Features
                    if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Can_Print"]:
                        if c2.button(f"🖨️ Print Waybill", key=f"pr_{idx}"):
                            st.write(f"Generating Label for {row['id']}...")
                        if c3.button(f"🚚 Mark Dispatch", key=f"ds_{idx}"):
                            st.session_state.orders[idx]['dispatch'] = "Yes"
                            st.success("Marked as Dispatched!")
                    
                    if st.button("Confirm Update", key=f"up_{idx}"):
                        st.session_state.orders[idx]['status'] = new_st
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.rerun()

# --- 7. FINANCE ---
elif menu == "💰 Finance":
    if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Can_Finance"]:
        st.title("Financial Overview")
        # Logic for Payroll calculation...
        st.write("Payroll and Expense logic loaded...")
    else:
        st.error("Access Denied: Owner permission required for Finance.")

# --- LOGOUT ---
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()
