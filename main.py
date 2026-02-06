import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go

# --- 0. DATA PERSISTENCE (දත්ත ස්ථීරව තබා ගැනීම) ---
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
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

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
    if (u == "admin" and p == "happy123") or (u == "happyshop@gmail.com" and p == "happy123"):
        return True, "Owner", "Admin"
    for i in range(1, 6):
        if u == f"demo{i}@gmail.com" and p == f"demo{i}":
            return True, "Staff", f"demo{i}"
    return False, None, None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_input = st.text_input("Username / Email")
        pass_input = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            auth, role, name = check_login(user_input, pass_input)
            if auth:
                st.session_state.authenticated = True
                st.session_state.user_role = role
                st.session_state.current_user = name
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- 4. CSS (Enhanced Styling) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 15px; border-radius: 10px; text-align: center; min-width: 130px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-f { background: #343a40; } .bg-t { background: #007bff; } .bg-profit { background: #9b59b6; }
    .val { font-size: 26px; display: block; }
    .ship-header { background-color: #1f2937; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #374151; }
    .status-tab { padding: 5px 12px; border-radius: 5px; font-weight: bold; font-size: 11px; margin-right: 5px; color: white; display: inline-block;}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>👤 <b>{st.session_state.current_user}</b> ({st.session_state.user_role})</p>", unsafe_allow_html=True)
    
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Admin Controls", expanded=False):
            st.session_state.staff_perms["Add_Order"] = st.checkbox("Staff: Add Leads", value=st.session_state.staff_perms["Add_Order"])
            st.session_state.staff_perms["Print"] = st.checkbox("Staff: Print/Dispatch", value=st.session_state.staff_perms["Print"])
            staff_options = ["Admin", "demo1", "demo2", "demo3", "demo4", "demo5"]
            ghost_user = st.selectbox("Switch View As:", staff_options, index=staff_options.index(st.session_state.current_user) if st.session_state.current_user in staff_options else 0)
            if ghost_user != st.session_state.current_user:
                st.session_state.current_user = ghost_user
                st.rerun()

    menu = st.radio("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": 
        sub = st.selectbox("Order Menu", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items": 
        sub = st.selectbox("Shipping Menu", ["Ship", "Shipped List", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills"])
    elif menu == "📊 Stocks": sub = st.selectbox("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("🚀 Business Control Center")
    df_o = pd.DataFrame(st.session_state.orders)
    df_e = pd.DataFrame(st.session_state.expenses)
    
    # Metrics Calculation
    def get_cnt(s): return len(df_o[df_o['status'] == s]) if not df_o.empty else 0
    total_rev = df_o[df_o['status'] == 'shipped']['total'].sum() if not df_o.empty else 0
    total_exp = df_e['amount'].sum() if not df_e.empty else 0
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_cnt('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_cnt('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_cnt('noanswer')}</span></div>
            <div class="m-card bg-x">CANCEL<span class="val">{get_cnt('cancel')}</span></div>
            <div class="m-card bg-t">TOTAL LEADS<span class="val">{len(df_o)}</span></div>
            <div class="m-card bg-profit">PROFIT<span class="val">Rs.{format_currency(total_rev - total_exp)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    if not df_o.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(df_o, names='dist', title="Sales by District", hole=0.4), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df_o, x='status', color='status', title="Order Status Distribution"), use_container_width=True)

# --- 7. ORDERS MODULE ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Add_Order"]:
            st.subheader(f"📝 Happy Shop - {sub}")
            with st.form("full_order", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Customer Name *")
                    phone = st.text_input("Contact Number *")
                    addr = st.text_area("Address *")
                    dist = st.selectbox("District", list(SL_DATA.keys()))
                    city = st.selectbox("City", SL_DATA[dist])
                with c2:
                    prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                    qty = st.number_input("Qty", min_value=1, value=1)
                    price = st.number_input("Sale Amount", value=2950.0)
                    delivery = st.number_input("Delivery Charge", value=350.0)
                    courier = st.selectbox("Courier", ["Koombiyo", "Domex", "Pronto"])
                
                if st.form_submit_button("🚀 SAVE ENTRY"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                        "pro_code": prod, "qty": qty, "total": (price * qty) + delivery, 
                        "status": "pending", "date": str(date.today()), "staff": st.session_state.current_user, "courier": courier
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success(f"Order {oid} Saved!")
        else:
            st.error("Permission Denied.")

    elif sub in ["View Lead", "Order Search", "Pending Orders"]:
        st.markdown('<div class="ship-header"><h3>🔍 Search & Filter Leads</h3>', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        s_status = fc1.selectbox("Status", ["Any", "pending", "confirm", "noanswer", "rejected", "fake", "cancel"])
        s_user = fc2.selectbox("User", ["Any", "Admin", "demo1", "demo2", "demo3", "demo4", "demo5"])
        s_name = fc3.text_input("Search Name/Phone")
        s_prod = fc4.selectbox("Product", ["Any"] + list(st.session_state.stocks.keys()))
        
        if st.button("Apply Filters"): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Status Tabs
        def cnt(st_val): return len([o for o in st.session_state.orders if o.get('status') == st_val])
        st.markdown(f"""
            <div style="margin-bottom:20px;">
                <span class="status-tab" style="background:#6c757d;">Pending: {cnt('pending')}</span>
                <span class="status-tab" style="background:#28a745;">Ok: {cnt('confirm')}</span>
                <span class="status-tab" style="background:#ffc107; color:black;">No Answer: {cnt('noanswer')}</span>
                <span class="status-tab" style="background:#dc3545;">Rejected: {cnt('rejected')}</span>
            </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            if s_status != "Any": df = df[df['status'] == s_status]
            if s_user != "Any": df = df[df['staff'] == s_user]
            if s_name: df = df[df['name'].str.contains(s_name, case=False) | df['phone'].astype(str).str.contains(s_name)]
            
            for idx, row in df.iterrows():
                with st.expander(f"📌 {row['id']} - {row['name']} ({row['status'].upper()})"):
                    ac1, ac2, ac3, ac4, ac5 = st.columns(5)
                    if ac1.button("✅ Confirm", key=f"c_{idx}"):
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if ac2.button("☎ No Answer", key=f"n_{idx}"):
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if ac3.button("❌ Reject", key=f"r_{idx}"):
                        st.session_state.orders[idx]['status'] = 'rejected'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if ac4.button("🗑️ Delete", key=f"d_{idx}"):
                        st.session_state.orders.pop(idx)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
            st.dataframe(df, use_container_width=True)

# --- 8. SHIPPED ITEMS & LOGISTICS ---
elif menu == "🚚 Shipped Items":
    if sub == "Confirm Dispatch":
        st.subheader("✅ Ready to Dispatch")
        ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
        if ready:
            for idx, o in enumerate(ready):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{o['id']}** | {o['name']} | {o['city']} | {o['pro_code']}")
                if c2.button("Mark Ready", key=f"rd_{idx}"):
                    o['status'] = 'ready_print'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
        else: st.info("No orders to dispatch.")

    elif sub == "Print Dispatch Items":
        to_print = [o for o in st.session_state.orders if o['status'] == 'ready_print']
        for idx, o in enumerate(to_print):
            if st.button(f"Print & Ship {o['id']}", key=f"sh_{idx}"):
                # Deduct Stock
                if o['pro_code'] in st.session_state.stocks:
                    st.session_state.stocks[o['pro_code']] -= int(o['qty'])
                o['status'] = 'shipped'
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.success(f"{o['id']} Shipped!")
                st.rerun()

# --- 9. GRN, EXPENSES & STOCKS ---
elif menu == "📦 GRN":
    st.subheader("📦 Goods Receive Note")
    with st.form("grn"):
        p = st.selectbox("Product", list(st.session_state.stocks.keys()))
        q = st.number_input("Received Qty", min_value=1)
        if st.form_submit_button("Update Stock"):
            st.session_state.stocks[p] += q
            st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
            save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
            save_data(pd.DataFrame(st.session_state.grn_history), 'grn.csv')
            st.success("Inventory Updated!")

elif menu == "💰 Expense":
    st.subheader("💰 Expense Tracking")
    with st.form("exp"):
        cat = st.selectbox("Category", ["Marketing", "Salary", "Rent", "Courier"])
        amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
            save_data(pd.DataFrame(st.session_state.expenses), 'expenses.csv')
            st.success("Expense Saved!")
    st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "📊 Stocks":
    st.subheader("📈 Inventory Level")
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Product Name", "Available Qty"]))

elif menu == "🛍️ Products":
    st.subheader("🛍️ Product Management")
    with st.form("new_p"):
        np = st.text_input("Product Name")
        if st.form_submit_button("Add Product"):
            if np and np not in st.session_state.stocks:
                st.session_state.stocks[np] = 0
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.rerun()

# --- FOOTER ---
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()
