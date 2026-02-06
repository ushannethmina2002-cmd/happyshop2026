import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Stability) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = {}

# --- 3. PROFESSIONAL CSS & PRINTING DESIGN ---
st.markdown("""
    <style>
    /* Dark Theme UI */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metrics Layout */
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 12px; border-radius: 10px; text-align: center; min-width: 120px; color: white; font-weight: bold; font-size: 14px; }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; margin-top: 5px; }

    /* HERBAL CROWN Pvt Ltd WAYBILL DESIGN (Fixed for Printing) */
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { 
            position: absolute; left: 0; top: 0; width: 500px; 
            color: black !important; background: white !important; 
            padding: 15px; border: 2px solid black; font-family: 'Inter', sans-serif;
        }
        .waybill-header { display: flex; justify-content: space-between; border-bottom: 2px solid black; padding-bottom: 5px; }
        .barcode-section { display: flex; border-bottom: 2px solid black; }
        .barcode-box { flex: 3; text-align: center; border-right: 2px solid black; padding: 10px; }
        .qty-box { flex: 1; text-align: center; padding: 10px; }
        .item-row { padding: 10px; font-weight: bold; border-bottom: 2px solid black; }
        .waybill-table { width: 100%; border-collapse: collapse; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 6px; font-size: 12px; text-align: left; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION (All Menu Items from Photos) ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Order Menu", ["New Order", "View Lead", "Order Tracking", "Add Lead", "Blacklist"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Shipping Menu", ["Dispatch & Print", "Shipped List", "Delivery Summary"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List", "Packing List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment", "Waste"])

# --- 5. TOP SUMMARY CARDS ---
def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
if menu in ["🏠 Dashboard", "🧾 Orders"]:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. CORE LOGIC ---

# 6.1 NEW ORDER / ADD LEAD (Full Fields as per Images)
if sub in ["New Order", "Add Lead"]:
    st.subheader("📝 Customer & Order Entry Form")
    with st.form("full_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *")
            phone1 = st.text_input("Contact Number 1 *")
            phone2 = st.text_input("Contact Number 2")
            city = st.text_input("City")
            district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
        with c2:
            prod = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1", "Kalkaya"])
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Sale Amount", value=2950.0)
            delivery = st.number_input("Delivery Charge", value=350.0)
            discount = st.number_input("Discount", value=0.0)
            weight = st.number_input("Pkg Weight (kg)", value=0.5)
            courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
            source = st.selectbox("Source", ["Facebook", "WhatsApp", "TikTok"])

        if st.form_submit_button("🚀 SAVE ORDER"):
            if name and phone1:
                order_id = f"HS-{len(st.session_state.orders) + 821380}"
                st.session_state.orders.append({
                    "id": order_id, "name": name, "phone": phone1, "addr": address, "city": city,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, 
                    "discount": discount, "total": (price * qty) + delivery - discount,
                    "status": "pending", "date": str(date.today()), "courier": courier
                })
                st.success(f"Order {order_id} Saved!")
                st.rerun()

# 6.2 VIEW LEAD (Interactive Buttons)
elif sub == "View Lead":
    st.subheader("📋 Leads Management")
    if not st.session_state.orders: st.info("No leads available.")
    else:
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"{o.get('id')} - {o.get('name')} ({o.get('status').upper()})"):
                st.write(f"📞 {o.get('phone')} | 📍 {o.get('addr')}")
                cols = st.columns(5)
                if cols[0].button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()
                if cols[4].button("Dispatch 🚚", key=f"d_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()

# 6.3 DISPATCH & PRINT (Herbal Crown Pvt Ltd Design)
elif sub == "Dispatch & Print":
    st.subheader("🚚 Ready for Dispatch")
    ready = [o for o in st.session_state.orders if o.get('status') == 'confirm']
    if not ready: st.warning("No confirmed orders to print.")
    else:
        for idx, ro in enumerate(ready):
            # පින්තූරයේ තිබූ ආකාරයටම බිල් එක නිර්මාණය කිරීම
            st.markdown(f"""
            <div class="print-area">
                <div class="waybill-header">
                    <div><b>Herbal Crown Pvt Ltd</b><br>TP: 0766066789</div>
                    <div style="text-align:right;">Date: {ro['date']}<br>ID: {ro['id']}</div>
                </div>
                <div class="barcode-section">
                    <div class="barcode-box">
                        <div style="font-size:35px; letter-spacing:5px;">||||||||||||||||||||</div>
                        <small>RA0298917900</small>
                    </div>
                    <div class="qty-box">
                        <small>Total Qty</small><br><b style="font-size:25px;">{ro['qty']}</b>
                    </div>
                </div>
                <div class="item-row">{ro['prod']} x {ro['qty']}</div>
                <table class="waybill-table">
                    <tr style="background:#eee;"><th>Customer Details</th><th colspan="2">Order Summary</th></tr>
                    <tr>
                        <td rowspan="4" style="width:55%;">
                            <b>Name:</b> {ro['name']}<br>
                            <b>Address:</b> {ro['addr']}, {ro['city']}<br>
                            <b>Tel:</b> {ro['phone']}
                        </td>
                        <td>Price</td><td>{ro['price']:.2f}</td>
                    </tr>
                    <tr><td>Delivery</td><td>{ro['delivery']:.2f}</td></tr>
                    <tr><td>Discount</td><td>{ro['discount']:.2f}</td></tr>
                    <tr style="background:#f9f9f9;"><td><b>Total</b></td><td><b>LKR {ro['total']:.2f}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Print & Ship {ro['id']}", key=f"p_{idx}"):
                for order in st.session_state.orders:
                    if order['id'] == ro['id']: order['status'] = 'shipped'
                st.components.v1.html("<script>window.print();</script>", height=0)
                st.rerun()

# 6.4 ORDER TRACKING (With Notification)
elif sub == "Order Tracking":
    st.subheader("🔍 Tracking")
    q = st.text_input("Enter Phone Number")
    if q:
        found = [o for o in st.session_state.orders if q in o['phone']]
        if found:
            for f in found:
                st.toast(f"Status: {f['status'].upper()}", icon="ℹ️")
                st.info(f"Order {f['id']} - Current Status: {f['status'].upper()}")
        else: st.error("No record found.")
