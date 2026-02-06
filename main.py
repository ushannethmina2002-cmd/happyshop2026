import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA STORAGE (SESSION STATE) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metric Cards */
    .metric-container { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 12px; border-radius: 10px; text-align: center; min-width: 120px;
        color: white; font-weight: bold; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .bg-pending { background: #6c757d; } 
    .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } 
    .bg-cancel { background: #dc3545; }
    .bg-fake { background: #343a40; }
    .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; margin-top: 5px; }

    /* Waybill Print Styles */
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; color: black !important; background: white !important; padding: 20px; border: 2px solid black; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HELPER FUNCTIONS ---
def get_count(status):
    if status == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status])

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Order Tracking", "Order History", "Blacklist"])
    elif menu == "🚚 Shipped Items":
        sub_menu = st.radio("Shipping Actions", ["Dispatch", "Shipped List", "Print Waybills"])
    elif menu == "📊 Stocks":
        sub_menu = st.radio("Stock Actions", ["View Stocks", "Adjustment", "Waste"])

# --- 6. TOP METRIC TILES ---
if menu == "🏠 Dashboard" or "Lead" in sub_menu or "Order" in sub_menu:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL<span class="val">{get_count('total')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. MAIN CONTENT ---

# 7.1 DASHBOARD
if menu == "🏠 Dashboard":
    st.title("Business Overview")
    st.write(f"Today's Date: {date.today()}")
    st.info("System fully operational. All data synced.")

# 7.2 NEW ORDER / ADD LEAD (සම්පූර්ණ පෝරමය)
elif sub_menu in ["New Order", "Add Lead"]:
    st.subheader("📝 Order Entry Form")
    with st.form("full_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            address = st.text_area("Delivery Address *")
            district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            city = st.text_input("City")
            phone1 = st.text_input("Phone Number 1 *")
            phone2 = st.text_input("Phone Number 2")
            email = st.text_input("Email Address")
        with c2:
            prod = st.selectbox("Product", ["Kesharaja Hair Oil", "Crown 1", "Kalkaya"])
            qty = st.number_input("Quantity", min_value=1, value=1)
            price = st.number_input("Product Price", value=2950.0)
            delivery = st.number_input("Delivery Charge", value=350.0)
            discount = st.number_input("Discount", value=0.0)
            courier = st.selectbox("Courier Company", ["Any", "Koombiyo", "Domex", "Pronto"])
            source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "TikTok"])
            note = st.text_area("Note")
            
        if st.form_submit_button("SAVE ORDER"):
            if name and phone1:
                st.session_state.orders.append({
                    "id": f"HS-{len(st.session_state.orders)+821380}",
                    "name": name, "phone": phone1, "addr": address, "prod": prod, "qty": qty,
                    "total": (price * qty) + delivery - discount, "status": "pending", 
                    "date": str(date.today()), "courier": courier
                })
                st.success("Lead Added Successfully!")
                st.rerun()

# 7.3 VIEW LEAD (Interactive Table with Fake Button)
elif sub_menu == "View Lead":
    st.subheader("📋 Leads Management")
    if not st.session_state.orders:
        st.write("No leads available.")
    else:
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"Order {o['id']} - {o['name']} ({o['status'].upper()})"):
                st.write(f"📞 {o['phone']} | 📍 {o['addr']} | 💰 LKR {o['total']}")
                cols = st.columns(5)
                if cols[0].button("Confirm ✔", key=f"c_{idx}"):
                    st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n_{idx}"):
                    st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ✖", key=f"x_{idx}"):
                    st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠", key=f"f_{idx}"):
                    st.session_state.orders[idx]['status'] = 'fake'; st.rerun()
                if cols[4].button("Ship 🚚", key=f"s_{idx}"):
                    st.session_state.orders[idx]['status'] = 'shipped'; st.rerun()

# 7.4 ORDER TRACKING (SEARCH)
elif sub_menu == "Order Tracking":
    st.subheader("🔍 Tracking")
    q = st.text_input("Enter Phone Number")
    if q:
        matches = [o for o in st.session_state.orders if q in o['phone']]
        if matches:
            for m in matches:
                st.info(f"Order {m['id']} is {m['status'].upper()}")
                st.toast(f"Status: {m['status'].upper()}")
        else: st.error("No data found.")

# 7.5 DISPATCH & PRINT (Waybill)
elif sub_menu in ["Dispatch", "Print Waybills"]:
    st.subheader("🚚 Dispatch & Waybills")
    confirmed = [o for o in st.session_state.orders if o['status'] == 'confirm']
    if not confirmed:
        st.write("No confirmed orders to ship.")
    else:
        for idx, co in enumerate(confirmed):
            st.info(f"Print Ready: {co['id']} - {co['name']}")
            if st.button(f"Print & Dispatch {co['id']}", key=f"p_{idx}"):
                # Print Layout
                st.markdown(f"""
                <div class="print-area">
                    <h2 style="text-align:center;">HAPPY SHOP WAYBILL</h2>
                    <hr>
                    <p><b>TO:</b> {co['name']}<br><b>ADDR:</b> {co['addr']}<br><b>TEL:</b> {co['phone']}</p>
                    <p><b>ITEM:</b> {co['prod']} (x{co['qty']})</p>
                    <h3 style="text-align:right;">COD AMOUNT: LKR {co['total']:.2f}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Shipped වලට මාරු කිරීම
                for order in st.session_state.orders:
                    if order['id'] == co['id']: order['status'] = 'shipped'
                
                st.components.v1.html("<script>window.print();</script>", height=0)
                st.success("Dispatched!")
                st.rerun()

# 7.6 Placeholder Sections
else:
    st.title(f"{menu} > {sub_menu}")
    st.info("System module ready. No data recorded in this section yet.")
