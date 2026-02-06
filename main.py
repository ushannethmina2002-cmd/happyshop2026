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
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'staff_perms' not in st.session_state:
    st.session_state.staff_perms = {"Add_Order": True, "Print": True, "Finance": False}

# --- 3. LOGIN SYSTEM ---
def check_login(u, p):
    if u == "happyshop@gmail.com" and p == "happy123":
        return True, "Owner", "Admin"
    for i in range(1, 6):
        if u == f"demo{i}@gmail.com" and p == f"demo{i}":
            return True, "Staff", f"demo{i}"
    return False, None, None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_input = st.text_input("Email/Username")
        pass_input = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            auth, role, name = check_login(user_input, pass_input)
            if auth:
                st.session_state.authenticated = True
                st.session_state.user_role = role
                st.session_state.current_user = name
                st.rerun()
            else:
                st.error("Invalid Email or Password")
    st.stop()

# --- 4. CSS (Enhanced with Picture Style) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 15px; border-radius: 10px; text-align: center; min-width: 140px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-t { background: #007bff; } .bg-profit { background: #9b59b6; }
    .val { font-size: 28px; display: block; }
    .status-bar { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .status-item { padding: 3px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR & GHOST SWITCH ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#ffa500; font-size: 24px;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    st.markdown(f"👤 **{st.session_state.current_user}**")
    
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Admin Master Controls", expanded=False):
            st.session_state.staff_perms["Add_Order"] = st.checkbox("Staff: Add Leads", value=st.session_state.staff_perms["Add_Order"])
            st.session_state.staff_perms["Print"] = st.checkbox("Staff: Print/Dispatch", value=st.session_state.staff_perms["Print"])
            st.session_state.staff_perms["Finance"] = st.checkbox("Staff: Finance View", value=st.session_state.staff_perms["Finance"])
            staff_options = ["Admin", "demo1", "demo2", "demo3", "demo4", "demo5"]
            selected_user = st.selectbox("Ghost Switch User", staff_options, index=staff_options.index(st.session_state.current_user) if st.session_state.current_user in staff_options else 0)
            if selected_user != st.session_state.current_user:
                st.session_state.current_user = selected_user
                st.rerun()

    st.markdown("---")
    menu = st.radio("MAIN NAVIGATION", ["🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", "✈️ Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"])
    
    if menu == "🛒 Orders":
        sub = st.selectbox("ORDER OPTIONS", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])

# --- 6. DASHBOARD (Analytics & Profit Added Back) ---
if menu == "🏠 Dashboard":
    st.title("🚀 Business Control Center")
    
    # පින්තූරයේ තිබූ Analysis දත්ත ගණනය කිරීම
    df_orders = pd.DataFrame(st.session_state.orders)
    df_exp = pd.DataFrame(st.session_state.expenses)
    
    total_revenue = df_orders[df_orders['status'] == 'confirm']['total'].sum() if not df_orders.empty else 0
    total_expenses = df_exp['amount'].sum() if not df_exp.empty else 0
    net_profit = total_revenue - total_expenses

    def get_count(s): return len(df_orders[df_orders['status'] == s]) if not df_orders.empty else 0
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-t">TOTAL LEADS<span class="val">{len(df_orders)}</span></div>
            <div class="m-card bg-x">RETURNS<span class="val">{get_count('return')}</span></div>
            <div class="m-card bg-profit">PROFIT<span class="val">Rs.{format_currency(net_profit)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    # ඩෑෂ්බෝඩ් ප්‍රස්ථාර
    if not df_orders.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_status = px.pie(df_orders, names='status', title='Order Status Distribution', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
        with c2:
            fig_daily = px.area(df_orders, x='date', title='Order Growth Over Time')
            st.plotly_chart(fig_daily, use_container_width=True)

# --- 7. ORDERS MODULE (Detailed Search Filters Added) ---
elif menu == "🛒 Orders":
    if sub in ["View Lead", "Order Search", "Pending Orders"]:
        st.subheader("🔍 Leads Search & Filter")
        
        # පින්තූරයේ තිබූ Search Filters (Status, User, Product, Date Range)
        c1, c2, c3, c4 = st.columns(4)
        f_status = c1.selectbox("Status", ["Any", "Pending", "Ok", "No Answer", "Rejected", "Cancelled", "On Hold"])
        f_user = c2.selectbox("User", ["Any", "Admin", "demo1", "demo2", "demo3", "demo4", "demo5"])
        f_name = c3.text_input("Customer Name", placeholder="Search name...")
        f_product = c4.selectbox("Product", ["Any"] + list(st.session_state.stocks.keys()))
        
        d1, d2 = st.columns(2)
        start_date = d1.date_input("Start Date", date.today() - timedelta(days=7))
        end_date = d2.date_input("End Date", date.today())

        # පින්තූරයේ තිබූ පාට පාට Status Legend එක
        st.markdown("""
            <div class="status-bar">
                <div class="status-item" style="background:#007bff">Pending | 0</div>
                <div class="status-item" style="background:#28a745">Ok | 0</div>
                <div class="status-item" style="background:#ffc107; color:black">No Answer | 0</div>
                <div class="status-item" style="background:#dc3545">Rejected | 0</div>
                <div class="status-item" style="background:#6c757d">Cancelled | 0</div>
                <div class="status-item" style="background:#e74c3c">On Hold | 0</div>
            </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.orders)
        # Filter Logic (Applying user filters)
        if not df.empty:
            if f_status != "Any": df = df[df['status'] == f_status.lower()]
            if f_user != "Any": df = df[df['staff'] == f_user]
            if f_name: df = df[df['name'].str.contains(f_name, case=False)]
            
            # Action Buttons Column (Shopping Cart, Call, Cancel, Edit etc.)
            st.markdown("### Leads List:")
            for idx, row in df.iterrows():
                with st.expander(f"📌 {row['id']} | {row['name']} | {row['city']} | Status: {row['status']}"):
                    # පින්තූරයේ තිබූ Action Icons ටික (Buttons ලෙස)
                    b1, b2, b3, b4, b5 = st.columns(5)
                    if b1.button("🛒 Confirm", key=f"conf_{idx}"):
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.rerun()
                    if b2.button("📞 No Answer", key=f"call_{idx}"):
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.rerun()
                    if b3.button("🚫 Cancel", key=f"canc_{idx}"):
                        st.session_state.orders[idx]['status'] = 'cancel'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.rerun()
                    if b4.button("✍️ Edit", key=f"edit_{idx}"): st.info("Edit feature opening...")
                    if b5.button("🖨️ Print", key=f"prnt_{idx}"): st.success("Printing Waybill...")

            st.table(df[['date', 'id', 'name', 'phone', 'city', 'pro_code', 'staff', 'status']])

    elif sub in ["New Order", "Add Lead"]:
        # මුල් Code එකේ තිබූ New Order Form එක (එක අකුරක්වත් අයින් නොකර)
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Add_Order"]:
            st.subheader("➕ Create New Entry")
            with st.form("entry_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Customer Name")
                phone = c1.text_input("Contact Number")
                addr = c1.text_area("Address")
                dist = c2.selectbox("District", list(SL_DATA.keys()))
                city = c2.selectbox("City", SL_DATA[dist])
                pro_code = c2.text_input("Product Code (Pro Code)")
                price = c2.number_input("Order Value", value=0)
                if st.form_submit_button("Save Entry"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone, "addr": addr, "dist": dist, "city": city,
                        "pro_code": pro_code, "total": price, "status": "pending", "date": str(date.today()),
                        "staff": st.session_state.current_user, "dispatch": "No"
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success("Saved!")
        else:
            st.error("බලතල සීමා කර ඇත.")

# --- 8. REMAINING MODULES (Keep Intact) ---
elif menu == "📦 GRN": st.title("Good Receive Note")
elif menu == "💸 Expense": st.title("Expense Tracking")
elif menu == "📊 Stocks":
    st.title("Stock Inventory")
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]))
elif menu == "✈️ Shipped Items": st.title("Dispatched Orders")
elif menu == "🔄 Return": st.title("Returns Management")
elif menu == "🏷️ Products": st.title("Product Master")

# --- FOOTER & LOGOUT ---
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()
