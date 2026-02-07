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

# --- SRI LANKA GEO-DATA (ලංකාවේ දත්ත) ---
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

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Ultimate Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE & DB INITIALIZATION ---
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
            else: st.error("Invalid credentials")
    st.stop()

# --- 4. CSS (Enhanced UI/UX) ---
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
    @media print {
        .no-print { display: none !important; }
        .print-area { visibility: visible !important; color: black !important; background: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>👤 <b>{st.session_state.current_user}</b></p>", unsafe_allow_html=True)
    
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Admin Master Control", expanded=False):
            st.session_state.staff_perms["Add_Order"] = st.checkbox("Allow Staff: Add Leads", value=st.session_state.staff_perms["Add_Order"])
            st.session_state.staff_perms["Print"] = st.checkbox("Allow Staff: Print/Dispatch", value=st.session_state.staff_perms["Print"])
            staff_list = ["Admin", "demo1", "demo2", "demo3", "demo4", "demo5"]
            selected_ghost = st.selectbox("Ghost Switch User", staff_list, index=staff_list.index(st.session_state.current_user) if st.session_state.current_user in staff_list else 0)
            if selected_ghost != st.session_state.current_user:
                st.session_state.current_user = selected_ghost
                st.rerun()

    menu = st.radio("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": 
        sub = st.selectbox("Order Menu", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items": 
        sub = st.selectbox("Shipping Menu", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills"])
    elif menu == "📦 GRN": sub = st.selectbox("GRN Menu", ["New GRN", "GRN List"])
    elif menu == "📊 Stocks": sub = st.selectbox("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD MODULE ---
if menu == "🏠 Dashboard":
    st.title("🚀 Business Control Center")
    df_o = pd.DataFrame(st.session_state.orders)
    df_e = pd.DataFrame(st.session_state.expenses)
    
    # Logic for metrics
    def get_count(s): return len(df_o[df_o['status'] == s]) if not df_o.empty else 0
    total_rev = df_o[df_o['status'] == 'shipped']['total'].astype(float).sum() if not df_o.empty else 0
    total_exp = df_e['amount'].astype(float).sum() if not df_e.empty else 0
    net_profit = total_rev - total_exp

    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-x">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-t">TOTAL LEADS<span class="val">{len(df_o)}</span></div>
            <div class="m-card bg-profit">PROFIT<span class="val">Rs.{format_currency(net_profit)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if not df_o.empty:
            st.plotly_chart(px.pie(df_o, names='dist', title="Sales by District", hole=0.4), use_container_width=True)
    with c2:
        if not df_o.empty:
            st.plotly_chart(px.bar(df_o, x='status', color='status', title="Order Status Distribution"), use_container_width=True)

# --- 7. ORDERS MODULE (ADVANCED VIEW) ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Add_Order"]:
            st.subheader(f"📝 Happy Shop - {sub}")
            with st.form("full_order", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Customer Name *")
                    phone = st.text_input("Contact Number 1 *")
                    addr = st.text_area("Address *")
                    dist = st.selectbox("District", list(SL_DATA.keys()))
                    city = st.selectbox("City", SL_DATA[dist])
                with c2:
                    prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                    qty = st.number_input("Qty", min_value=1, value=1)
                    price = st.number_input("Sale Amount", value=2950.0)
                    delivery = st.number_input("Delivery Charge", value=350.0)
                    discount = st.number_input("Discount", value=0.0)
                    courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto", "Royal Express"])
                
                if st.form_submit_button("🚀 SAVE ENTRY"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                        "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                        "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), 
                        "courier": courier, "staff": st.session_state.current_user
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success(f"Order {oid} Saved Successfully!")
        else: st.error("Staff access restricted for this action.")

    elif sub in ["View Lead", "Order Search"]:
        st.markdown('<div class="ship-header"><h3>🔍 Leads Search & Filter</h3>', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        s_status = fc1.selectbox("Filter Status", ["Any", "pending", "confirm", "noanswer", "rejected", "fake", "cancelled"])
        s_user = fc2.selectbox("Filter User", ["Any", "Admin", "demo1", "demo2", "demo3", "demo4", "demo5"])
        s_name = fc3.text_input("Search Name/Phone")
        s_range = fc4.date_input("Date Range", [date.today() - timedelta(days=30), date.today()])
        
        if st.button("Apply Advanced Filter", type="primary"): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Status Tabs Summary
        def cnt_st(s): return len([o for o in st.session_state.orders if o.get('status') == s])
        st.markdown(f"""
            <div style="margin-bottom:20px;">
                <span class="status-tab" style="background:#4b5563;">Leads: {len(st.session_state.orders)}</span>
                <span class="status-tab" style="background:#6c757d;">Pending: {cnt_st('pending')}</span>
                <span class="status-tab" style="background:#28a745;">Confirm: {cnt_st('confirm')}</span>
                <span class="status-tab" style="background:#ffc107; color:black;">No Answer: {cnt_st('noanswer')}</span>
            </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            if s_status != "Any": df = df[df['status'] == s_status]
            if s_user != "Any": df = df[df['staff'] == s_user]
            if s_name: df = df[df['name'].str.contains(s_name, case=False) | df['phone'].astype(str).str.contains(s_name)]
            
            # Action UI
            for idx, row in df.iterrows():
                with st.expander(f"📦 {row['id']} | {row['name']} | Status: {row['status'].upper()}"):
                    col1, col2, col3, col4, col5 = st.columns(5)
                    if col1.button("✅ OK", key=f"ok_{idx}"):
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col2.button("☎ Call", key=f"cl_{idx}"):
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col3.button("🚫 Cancel", key=f"cn_{idx}"):
                        st.session_state.orders[idx]['status'] = 'cancelled'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col4.button("🗑️ Delete", key=f"dl_{idx}"):
                        st.session_state.orders.pop(idx)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
            st.dataframe(df, use_container_width=True)

# --- 8. LOGISTICS (SHIPPED ITEMS) ---
elif menu == "🚚 Shipped Items":
    if sub == "Confirm Dispatch":
        st.subheader("✅ Confirm Orders for Dispatch")
        ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
        if ready:
            for idx, o in enumerate(ready):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{o['id']}** - {o['name']} | {o['city']} | {o['prod']}")
                if c2.button("Ready to Print", key=f"pr_{idx}"):
                    o['status'] = 'ready_print'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
        else: st.info("No confirmed orders to dispatch.")

    elif sub == "Print Dispatch Items":
        st.subheader("🖨️ Printing & Shipping")
        to_ship = [o for o in st.session_state.orders if o['status'] == 'ready_print']
        if to_ship:
            for idx, o in enumerate(to_ship):
                st.markdown(f"**{o['id']}** - {o['name']} - {o['courier']}")
                if st.button(f"Mark as Shipped {o['id']}", key=f"ship_{idx}"):
                    # Stock Deduction
                    if o['prod'] in st.session_state.stocks:
                        st.session_state.stocks[o['prod']] -= int(o['qty'])
                    o['status'] = 'shipped'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                    st.success(f"Waybill Generated for {o['id']}")
                    st.rerun()

# --- 9. GRN, EXPENSES & STOCKS ---
elif menu == "📦 GRN":
    st.subheader("📦 Goods Receive Note")
    with st.form("grn_new"):
        p = st.selectbox("Select Product", list(st.session_state.stocks.keys()))
        q = st.number_input("Received Quantity", min_value=1)
        if st.form_submit_button("Add to Inventory"):
            st.session_state.stocks[p] += q
            st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
            save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
            save_data(pd.DataFrame(st.session_state.grn_history), 'grn.csv')
            st.success(f"Stock updated for {p}!")

elif menu == "💰 Expense":
    st.subheader("💰 Financial Tracking")
    with st.form("expense_entry"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["Marketing", "FB Ads", "Salary", "Rent", "Packaging", "Courier"])
        amt = c2.number_input("Amount (LKR)", min_value=0.0)
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
            save_data(pd.DataFrame(st.session_state.expenses), 'expenses.csv')
            st.success("Expense logged.")
    st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "📊 Stocks":
    st.subheader("📈 Inventory Status Dashboard")
    df_stock = pd.DataFrame(st.session_state.stocks.items(), columns=["Product Name", "Available Qty"])
    st.table(df_stock)
    
    # Low Stock Alert
    low = df_stock[df_stock['Available Qty'] < 10]
    if not low.empty:
        st.warning(f"Critical Stock: {', '.join(low['Product Name'].tolist())}")

elif menu == "🛍️ Products":
    st.subheader("🛍️ Product Master Data")
    with st.form("new_product"):
        n_p = st.text_input("New Product Name")
        if st.form_submit_button("Create Product"):
            if n_p and n_p not in st.session_state.stocks:
                st.session_state.stocks[n_p] = 0
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.rerun()

# --- FOOTER & LOGOUT ---
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout System"):
    st.session_state.authenticated = False
    st.rerun()
