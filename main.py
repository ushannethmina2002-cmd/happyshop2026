import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Storage) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = {}

# --- 3. PROFESSIONAL CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metric Cards */
    .metric-container { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 15px; border-radius: 12px; text-align: center; min-width: 140px;
        color: white; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .bg-pending { background: #1a1d23; border: 1px solid #6c757d; }
    .bg-confirm { background: #1b4d2e; } 
    .bg-noanswer { background: #856404; } 
    .bg-cancel { background: #721c24; }
    .bg-total { background: #004085; }
    .val { font-size: 28px; display: block; margin-top: 5px; }

    /* Waybill Print Styling */
    @media print {
        .no-print { display: none !important; }
        .print-area { display: block !important; width: 100%; color: black !important; background: white !important; padding: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HELPER FUNCTIONS ---
def get_count(status):
    if status == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status])

def calculate_total_sales():
    # පින්තූරවල තිබුණු KeyError එක විසඳීමට float() සහ check එකක් එක් කළා
    try:
        return sum(float(o.get('total_amt', 0)) for o in st.session_state.orders if o['status'] == 'confirm' or o['status'] == 'shipped')
    except:
        return 0.0

# --- 5. SIDEBAR NAVIGATION (පින්තූරවල තිබුණු සියලුම Menu Items ඇතුළත්) ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    
    menu = st.selectbox("MAIN NAVIGATION", 
        ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🛍️ Products"])

    # පින්තූරවල තිබුණු Sub-menus
    sub_menu = ""
    if menu == "📦 GRN":
        sub_menu = st.sidebar.radio("GRN Actions", ["New GRN", "GRN List", "Reorder List", "New PO", "PO List", "Packing", "Packing List"])
    elif menu == "💰 Expense":
        sub_menu = st.sidebar.radio("Expense Actions", ["New Expense", "View Expenses", "Create Expense Type", "View Expense Type", "POS Expenses"])
    elif menu == "🧾 Orders":
        sub_menu = st.sidebar.radio("Order Actions", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items":
        sub_menu = st.sidebar.radio("Shipping Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills"])
    elif menu == "🔄 Return":
        sub_menu = st.sidebar.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])
    elif menu == "📊 Stocks":
        sub_menu = st.sidebar.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
    elif menu == "🛍️ Products":
        sub_menu = st.sidebar.radio("Product Actions", ["Create Product", "View Products", "Raw Items"])

# --- 6. TOP METRIC TILES ---
if menu == "🏠 Dashboard" or "View Lead" in sub_menu or "New Order" in sub_menu:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">OK (CONFIRMED)<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-total">TOTAL SALES<span class="val">LKR {calculate_total_sales():,.2f}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. MAIN CONTENT LOGIC ---

# 7.1 NEW ORDER / ADD LEAD (සම්පූර්ණ Fields සහිතව)
if menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
    st.subheader("📝 Customer & Order Entry Form")
    with st.form("full_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Customer Name *")
            c_address = st.text_area("Address *")
            c_city = st.selectbox("Select City", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            c_dist = st.selectbox("Select District", ["Colombo", "Gampaha", "Kalutara", "Other"])
            c_phone1 = st.text_input("Contact Number One *")
            c_phone2 = st.text_input("Contact Number Two")
            c_email = st.text_input("Email")
            c_source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Instagram", "TikTok"])
        
        with col2:
            p_item = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1 [VGLS0001]", "Kalkaya [VGLS0003]"])
            p_qty = st.number_input("Qty", min_value=1, value=1)
            p_price = st.number_input("Sale Amount (LKR)", min_value=0.0, value=2950.0)
            p_discount = st.number_input("Product Discount", min_value=0.0)
            p_courier = st.selectbox("Courier Company", ["Any", "Koombiyo", "Domex", "Pronto"])
            p_weight = st.number_input("Pkg Weight (kgs)", min_value=0.0, value=0.5)
            p_shipping = st.number_input("Delivery Charge", min_value=0.0)
            p_note = st.text_area("Order Note")
        
        total_to_collect = (p_price * p_qty) + p_shipping - p_discount
        st.markdown(f"### Total Amount to Collect: **LKR {total_to_collect:,.2f}**")
        
        if st.form_submit_button("🚀 SAVE & CONFIRM ORDER"):
            if c_name and c_phone1:
                order_id = f"HS-{len(st.session_state.orders) + 821370}"
                st.session_state.orders.append({
                    "order_id": order_id, "customer": c_name, "phone": c_phone1, "address": c_address,
                    "item": p_item, "qty": p_qty, "total_amt": total_to_collect, "status": "pending",
                    "date": str(date.today()), "courier": p_courier
                })
                st.success(f"Order {order_id} Saved Successfully!")
                st.rerun()

# 7.2 ORDER SEARCH & TRACKING (Notification System)
elif menu == "🧾 Orders" and sub_menu == "Order Search":
    st.subheader("🔍 Search & Track Order")
    search_term = st.text_input("Enter Phone Number or Order ID to Track")
    if search_term:
        results = [o for o in st.session_state.orders if search_term in o['phone'] or search_term in o['order_id']]
        if results:
            for res in results:
                st.info(f"📍 Order ID: {res['order_id']} | Status: {res['status'].upper()}")
                st.json(res)
        else:
            st.warning("No Order Found for this Number.")

# 7.3 VIEW LEAD / MANAGEMENT
elif menu == "🧾 Orders" and sub_menu == "View Lead":
    st.subheader("📋 Leads Management Table")
    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)
        st.dataframe(df[['order_id', 'customer', 'phone', 'item', 'total_amt', 'status']])
        
        # Action Buttons
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"Action for {o['order_id']} - {o['customer']}"):
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("Confirm ✅", key=f"conf_{idx}"):
                    st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if c2.button("No Answer ☎️", key=f"no_{idx}"):
                    st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if c3.button("Cancel ❌", key=f"can_{idx}"):
                    st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if c4.button("Ship 🚚", key=f"ship_{idx}"):
                    st.session_state.orders[idx]['status'] = 'shipped'; st.rerun()

# 7.4 PRINT WAYBILL / DISPATCH
elif menu == "🚚 Shipped Items" and sub_menu == "Ship":
    st.subheader("🚚 Dispatch & Waybill Printing")
    confirm_orders = [o for o in st.session_state.orders if o['status'] == 'confirm']
    if not confirm_orders:
        st.write("No confirmed orders to ship.")
    else:
        for idx, co in enumerate(confirm_orders):
            st.markdown(f"**Order:** {co['order_id']} | **Customer:** {co['customer']}")
            if st.button(f"Generate Waybill for {co['order_id']}", key=f"print_{idx}"):
                st.markdown(f"""
                <div style="background:white; color:black; padding:20px; border:2px solid black; font-family:Arial;">
                    <h2 style="text-align:center;">HAPPY SHOP WAYBILL</h2>
                    <p><b>TO:</b> {co['customer']}<br><b>ADDR:</b> {co['address']}<br><b>TEL:</b> {co['phone']}</p>
                    <hr>
                    <p><b>ITEM:</b> {co['item']} (Qty: {co['qty']})</p>
                    <p style="font-size:20px;"><b>COD AMOUNT: LKR {co['total_amt']:.2f}</b></p>
                </div>
                """, unsafe_allow_html=True)
                st.button("Click to Print (Ctrl+P)")

# --- 8. OTHER SECTIONS (Placeholder based on photos) ---
else:
    st.title(f"{menu} > {sub_menu}")
    st.info("මෙම අංශය දැනට සැකසෙමින් පවතී. (Orders > Import Lead අංශය මෙන්)")

