import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- 1. පිටුවේ සැකසුම් (PAGE CONFIGURATION) ---
st.set_page_config(
    page_title="HappyShop ERP System", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS & UI STYLING ---
st.markdown("""
    <style>
    /* Hide Streamlit elements - Added to remove Footer and Logo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* Global Styles */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #001f3f !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Custom UI Components */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
        margin: 10px 0px;
        color: white;
    }
    .section-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e67e22;
        margin-bottom: 20px;
        color: white;
    }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 15px; border-radius: 10px; text-align: center; min-width: 130px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-f { background: #343a40; } .bg-t { background: #007bff; } .bg-profit { background: #9b59b6; }
    .val { font-size: 26px; display: block; }
    .status-tab { padding: 5px 12px; border-radius: 5px; font-weight: bold; font-size: 11px; margin-right: 5px; color: white; display: inline-block;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA PERSISTENCE & CONNECTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

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

# SRI LANKA GEO-DATA
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

# --- 4. SESSION STATE INITIALIZATION ---
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv')
if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil": 100, "Crown 1": 50, "Kalkaya": 75}
if 'expenses' not in st.session_state: st.session_state.expenses = load_data('expenses.csv')
if 'grn_history' not in st.session_state: st.session_state.grn_history = load_data('grn.csv')
if 'user' not in st.session_state: st.session_state.user = None
if 'staff_perms' not in st.session_state:
    st.session_state.staff_perms = {"Add_Order": True, "Print": True, "Finance": False}

# --- 5. LOGIN SYSTEM ---
def login():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        email = st.text_input("Email", placeholder="example@gmail.com")
        password = st.text_input("Password", type="password")
        
        if st.button("Log In", use_container_width=True):
            if email == "happyshop@gmail.com" and password == "VLG0005":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif email == "demo1@gmail.com" and password == "demo1":
                st.session_state.user = {"name": "Staff 01", "role": "STAFF"}
                st.rerun()
            elif email == "demo2@gmail.com" and password == "demo2":
                st.session_state.user = {"name": "Staff 02", "role": "STAFF"}
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# --- 6. MAIN APPLICATION LOGIC ---
if st.session_state.user is None:
    login()
else:
    # SIDEBAR NAVIGATION
    with st.sidebar:
        st.markdown(f"### 🛒 HappyShop\nUser: {st.session_state.user['name']}")
        st.markdown("---")
        
        menu = st.radio("MAIN NAVIGATION", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🛍️ Products"])
        
        sub_choice = ""
        if menu == "🧾 Orders":
            st.markdown("<div class='menu-header'>Orders</div>", unsafe_allow_html=True)
            sub_choice = st.radio("Order Menu", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"], label_visibility="collapsed")
        elif menu == "🚚 Shipped Items":
            st.markdown("<div class='menu-header'>Logistics</div>", unsafe_allow_html=True)
            sub_choice = st.radio("Shipping Menu", ["Confirm Dispatch", "Print Dispatch Items", "Shipped List", "Shipped Summary"], label_visibility="collapsed")
        
        if st.sidebar.button("🔓 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.title("🚀 Business Control Center")
        df_o = pd.DataFrame(st.session_state.orders)
        df_e = pd.DataFrame(st.session_state.expenses)
        
        def get_count(s): return len(df_o[df_o['status'] == s]) if not df_o.empty else 0
        total_rev = df_o[df_o['status'] == 'shipped']['total'].astype(float).sum() if not df_o.empty else 0
        total_exp = df_e['amount'].astype(float).sum() if not df_e.empty else 0
        net_profit = total_rev - total_exp

        st.markdown(f"""
            <div class="metric-container">
                <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
                <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
                <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
                <div class="m-card bg-x">CANCEL<span class="val">{get_count('cancelled')}</span></div>
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

    # ORDERS MODULE
    elif menu == "🧾 Orders":
        if sub_choice in ["New Order", "Add Lead"]:
            st.markdown(f"## 📝 New Order / Waybill Entry")
            with st.form("full_order", clear_on_submit=True):
                c1, c2 = st.columns([1.5, 1], gap="large")
                with c1:
                    st.markdown("<div class='section-box'><b>Customer Details</b></div>", unsafe_allow_html=True)
                    name = st.text_input("Customer Name *")
                    phone = st.text_input("Contact Number 1 *")
                    addr = st.text_area("Address *")
                    dist = st.selectbox("District", list(SL_DATA.keys()))
                    city = st.selectbox("Select City", SL_DATA[dist])
                    source = st.selectbox("Order Source", ["FB Lead", "WhatsApp", "Web"])
                with c2:
                    st.markdown("<div class='section-box'><b>Product & Pricing</b></div>", unsafe_allow_html=True)
                    prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                    qty = st.number_input("Qty", min_value=1, value=1)
                    price = st.number_input("Sale Amount", value=2950.0)
                    delivery = st.number_input("Delivery Charge", value=350.0)
                    discount = st.number_input("Discount", value=0.0)
                    courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto", "Royal Express"])
                
                if st.form_submit_button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                    if name and phone and addr:
                        oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                        st.session_state.orders.append({
                            "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                            "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                            "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), 
                            "courier": courier, "staff": st.session_state.user['name'], "source": source
                        })
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.success(f"Order {oid} saved successfully by {st.session_state.user['name']}!")
                    else:
                        st.error("Please fill all required (*) fields.")

        elif sub_choice in ["View Lead", "Order Search", "Pending Orders"]:
            st.header("🔍 Leads Management")
            df = pd.DataFrame(st.session_state.orders)
            if not df.empty:
                # Filter UI
                fc1, fc2 = st.columns(2)
                s_name = fc1.text_input("Search Name/Phone")
                if s_name: df = df[df['name'].str.contains(s_name, case=False) | df['phone'].astype(str).str.contains(s_name)]
                
                for idx, row in df.iterrows():
                    with st.expander(f"📦 {row['id']} | {row['name']} | Status: {row['status'].upper()}"):
                        col1, col2, col3, col4 = st.columns(4)
                        if col1.button("✅ Confirm", key=f"ok_{idx}"):
                            st.session_state.orders[idx]['status'] = 'confirm'
                            save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                        if col2.button("☎ No Answer", key=f"cl_{idx}"):
                            st.session_state.orders[idx]['status'] = 'noanswer'
                            save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                        if col3.button("🚫 Cancel", key=f"cn_{idx}"):
                            st.session_state.orders[idx]['status'] = 'cancelled'
                            save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                        if col4.button("🗑️ Delete", key=f"dl_{idx}"):
                            st.session_state.orders.pop(idx)
                            save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                st.dataframe(df, use_container_width=True)

        elif sub_choice == "Blacklist Manager":
            st.header("🚫 Blacklist Manager")
            st.info("Blacklisted customers will appear here.")

    # LOGISTICS MODULE
    elif menu == "🚚 Shipped Items":
        if sub_choice == "Confirm Dispatch":
            st.subheader("✅ Confirm Orders for Dispatch")
            ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
            if ready:
                for idx, o in enumerate(ready):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{o['id']}** - {o['name']} | {o['city']} | {o['prod']}")
                    if c2.button("Ready to Print", key=f"pr_{idx}"):
                        for order in st.session_state.orders:
                            if order['id'] == o['id']: order['status'] = 'ready_print'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
            else: st.info("No confirmed orders to dispatch.")

        elif sub_choice == "Print Dispatch Items":
            st.subheader("🖨️ Printing & Shipping")
            to_ship = [o for o in st.session_state.orders if o['status'] == 'ready_print']
            if to_ship:
                for idx, o in enumerate(to_ship):
                    st.markdown(f"**{o['id']}** - {o['name']} - {o['courier']}")
                    if st.button(f"Mark as Shipped {o['id']}", key=f"ship_{idx}"):
                        if o['prod'] in st.session_state.stocks:
                            st.session_state.stocks[o['prod']] -= int(o['qty'])
                        for order in st.session_state.orders:
                            if order['id'] == o['id']: order['status'] = 'shipped'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                        st.success(f"Shipped {o['id']}")
                        st.rerun()

    # GRN MODULE
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

    # EXPENSE MODULE
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
        if st.session_state.expenses:
            st.table(pd.DataFrame(st.session_state.expenses))

    # STOCKS MODULE
    elif menu == "📊 Stocks":
        st.subheader("📈 Inventory Status Dashboard")
        df_stock = pd.DataFrame(st.session_state.stocks.items(), columns=["Product Name", "Available Qty"])
        st.table(df_stock)
        low = df_stock[df_stock['Available Qty'] < 10]
        if not low.empty:
            st.warning(f"Critical Stock: {', '.join(low['Product Name'].tolist())}")

    # PRODUCTS MODULE
    elif menu == "🛍️ Products":
        st.subheader("🛍️ Product Master Data")
        with st.form("new_product"):
            n_p = st.text_input("New Product Name")
            if st.form_submit_button("Create Product"):
                if n_p and n_p not in st.session_state.stocks:
                    st.session_state.stocks[n_p] = 0
                    save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                    st.rerun()
