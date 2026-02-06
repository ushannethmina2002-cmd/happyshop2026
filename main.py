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
        return pd.read_csv(filename).to_dict('records')
    return []

def format_currency(num):
    if num >= 1_000_000_000: return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000: return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000: return f"{num / 1_000:.1f}K"
    return f"{num:,.2f}"

# --- SRI LANKA GEO-DATA (RE-ADDED FULLY) ---
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
st.set_page_config(page_title="Happy Shop | Ultimate Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE & DB ---
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv')
if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil": 100, "Crown 1": 50, "Kalkaya": 75}
if 'expenses' not in st.session_state: st.session_state.expenses = load_data('expenses.csv')
if 'grn_history' not in st.session_state: st.session_state.grn_history = load_data('grn.csv')
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'staff_perms' not in st.session_state:
    st.session_state.staff_perms = {"Add_Order": True, "Print": True, "Finance": False}

# --- 3. LOGIN SYSTEM ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pw == "happy123":
                st.session_state.authenticated, st.session_state.user_role, st.session_state.current_user = True, "Owner", "Admin"
                st.rerun()
            elif user.startswith("staff") and pw == "staff123":
                st.session_state.authenticated, st.session_state.user_role, st.session_state.current_user = True, "Staff", user
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()

# --- 4. CSS (ENHANCED) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 15px; border-radius: 10px; text-align: center; min-width: 140px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-t { background: #007bff; }
    .val { font-size: 28px; display: block; }
    .status-bar { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-item { padding: 5px 15px; border-radius: 4px; font-weight: bold; font-size: 13px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR (COMPREHENSIVE MENU) ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#ffa500;'>HAPPY SHOP</h2>", unsafe_allow_html=True)
    st.markdown(f"👤 **{st.session_state.current_user}**")
    
    # OWNER CONTROLS FOR STAFF PERMISSIONS
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Admin Controls"):
            st.session_state.staff_perms["Add_Order"] = st.checkbox("Allow Staff to Add Leads", value=st.session_state.staff_perms["Add_Order"])
            st.session_state.staff_perms["Print"] = st.checkbox("Allow Staff Print/Dispatch", value=st.session_state.staff_perms["Print"])
            st.session_state.staff_perms["Finance"] = st.checkbox("Allow Staff Finance View", value=st.session_state.staff_perms["Finance"])
            staff_list = ["Admin", "staff1", "staff2", "staff3"]
            st.session_state.current_user = st.selectbox("Ghost Switch", staff_list, index=staff_list.index(st.session_state.current_user))

    # FULL MENU ITEMS FROM SCREENSHOTS
    menu = st.radio("MAIN NAVIGATION", ["🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", "✈️ Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"])
    
    if menu == "🛒 Orders":
        sub = st.selectbox("ORDER OPTIONS", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])

# --- 6. DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("🚀 Business Control Center")
    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-t">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
            <div class="m-card bg-x">RETURNS<span class="val">{get_count('return')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. ORDERS MODULE (THE HEART) ---
elif menu == "🛒 Orders":
    if sub in ["New Order", "Add Lead"]:
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Add_Order"]:
            st.subheader("➕ Create New Lead / Order")
            # SMART PARSER
            raw_text = st.text_area("Paste WhatsApp Text to Parse")
            if st.button("Auto-Fill"):
                phone_m = re.search(r'(\d{10})', raw_text)
                st.session_state.tmp_name = raw_text.split('\n')[0] if raw_text else ""
                st.session_state.tmp_phone = phone_m.group(1) if phone_m else ""
            
            with st.form("full_order_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Customer Name", value=st.session_state.get('tmp_name', ""))
                phone = c1.text_input("Contact #1", value=st.session_state.get('tmp_phone', ""))
                addr = c1.text_area("Address")
                dist = c2.selectbox("District", list(SL_DATA.keys()))
                city = c2.selectbox("City", SL_DATA[dist])
                pro_code = c2.text_input("Pro Code", value="VGLS0005")
                price = c2.number_input("Value", value=2500)
                if st.form_submit_button("🚀 SAVE LEAD"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone, "addr": addr, "dist": dist, "city": city,
                        "pro_code": pro_code, "total": price, "status": "pending", "date": str(date.today()),
                        "staff": st.session_state.current_user, "dispatch": "No"
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success("Lead Added!")
        else: st.error("Access Denied by Admin")

    elif sub in ["View Lead", "Order Search", "Pending Orders"]:
        st.subheader("🔍 Leads Search & Manager")
        # STATUS BAR FROM SCREENSHOT
        st.markdown("""
            <div class="status-bar">
                <div class="status-item" style="background:#007bff">Pending | 0</div>
                <div class="status-item" style="background:#28a745">Ok | 0</div>
                <div class="status-item" style="background:#ffc107; color:black">No Answer | 0</div>
                <div class="status-item" style="background:#dc3545">Cancelled | 0</div>
            </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            for idx, row in df.iterrows():
                with st.expander(f"Order: {row['id']} | {row['name']} | {row['status']}"):
                    col1, col2, col3, col4 = st.columns(4)
                    # ACTION BUTTONS AS REQUESTED
                    if col1.button("🛒 Confirm", key=f"c_{idx}"):
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    if col2.button("🚫 Cancel", key=f"x_{idx}"):
                        st.session_state.orders[idx]['status'] = 'cancel'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    if col3.button("📞 No Answer", key=f"n_{idx}"):
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    
                    # PRINT & DISPATCH CONTROL
                    if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Print"]:
                        if col4.button("🖨️ Dispatch", key=f"p_{idx}"):
                            st.session_state.orders[idx]['dispatch'] = "Yes"
                            st.success("Marked for Dispatch!")
            
            st.dataframe(df[['date', 'id', 'name', 'phone', 'dist', 'city', 'pro_code', 'staff', 'status']])

# --- 8. OTHER MODULES ---
elif menu == "📦 GRN": st.title("Good Receive Note")
elif menu == "💸 Expense":
    if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Finance"]:
        st.title("Expense Management")
    else: st.error("Finance Access Locked")
elif menu == "📊 Stocks": st.title("Inventory Tracking")
elif menu == "🏷️ Products": st.title("Product Master")
elif menu == "✈️ Shipped Items": st.title("Shipped Items Tracker")
elif menu == "🔄 Return": st.title("Returns Management")

# --- LOGOUT ---
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()
