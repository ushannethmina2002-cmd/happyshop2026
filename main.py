import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. PROFESSIONAL CSS & PRINT DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    
    /* Metrics Styling */
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
    .m-card { padding: 10px; border-radius: 8px; text-align: center; min-width: 110px; color: white; font-weight: bold; font-size: 13px; }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 20px; display: block; }

    /* WAYBILL PRINT DESIGN (පින්තූරයේ පරිදිම) */
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { 
            position: absolute; left: 0; top: 0; width: 400px; 
            color: black !important; background: white !important; 
            padding: 15px; border: 1px dashed #000; font-family: 'Arial', sans-serif;
        }
        .waybill-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 5px; font-size: 12px; }
        .header-box { text-align: center; margin-bottom: 10px; }
        .barcode { font-family: 'Libre Barcode 39', cursive; font-size: 40px; text-align: center; margin: 10px 0; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped & Prints", "💰 Expense", "📊 Stocks"])
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Actions", ["New Order", "View Lead", "Search Order"])
    elif menu == "🚚 Shipped & Prints":
        sub_menu = st.radio("Actions", ["Dispatch & Print", "Shipped List"])

# --- 5. TOP METRICS ---
def get_count(s): return len([o for o in st.session_state.orders if o['status'] == s])
if menu == "🏠 Dashboard" or "Lead" in sub_menu:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRM<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. NEW ORDER ENTRY ---
if sub_menu == "New Order":
    st.subheader("📝 New Order Entry")
    with st.form("order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone Number *")
            addr = st.text_area("Address *")
        with col2:
            prod = st.selectbox("Product", ["Hair Oil", "Crown 1", "Kalkaya"])
            price = st.number_input("Price", value=2950.0)
            delivery = st.number_input("Delivery Cost", value=350.0)
            discount = st.number_input("Discount", value=0.0)
        
        if st.form_submit_button("SAVE ORDER"):
            if name and phone:
                st.session_state.orders.append({
                    "id": f"{len(st.session_state.orders)+112}",
                    "name": name, "phone": phone, "addr": addr, "prod": prod,
                    "price": price, "delivery": delivery, "discount": discount,
                    "total": price + delivery - discount, "status": "pending", "date": str(date.today())
                })
                st.rerun()

# --- 7. VIEW LEAD & ACTIONS ---
elif sub_menu == "View Lead":
    st.subheader("📋 Leads Management")
    for idx, o in enumerate(st.session_state.orders):
        with st.expander(f"{o['id']} - {o['name']} ({o['status'].upper()})"):
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
            if c2.button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
            if c3.button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
            if c4.button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()

# --- 8. DISPATCH & WAYBILL PRINT (පින්තූරයේ ඩිසයින් එක) ---
elif sub_menu == "Dispatch & Print":
    st.subheader("🚚 Dispatch & Waybill Printing")
    confirm_orders = [o for o in st.session_state.orders if o['status'] == 'confirm']
    
    if not confirm_orders:
        st.warning("No confirmed orders to print.")
    else:
        for idx, co in enumerate(confirm_orders):
            st.info(f"Order Ready: {co['id']} - {co['name']}")
            
            # පින්තූරයේ තිබූ ආකාරයටම බිල් එක නිර්මාණය කිරීම
            bill_html = f"""
            <div class="print-area">
                <div class="header-box">
                    <h2 style="margin:0;">Herbal Crown Pvt Ltd</h2>
                    <p style="font-size:10px; margin:0;">Quality Herbal Products</p>
                </div>
                <table class="waybill-table">
                    <tr><td><b>TP:</b> 0766066789</td><td><b>Date:</b> {co['date']}</td></tr>
                    <tr><td><b>ID:</b> {co['id']}</td><td><b>Status:</b> CONFIRM</td></tr>
                </table>
                <div style="text-align:center; padding:10px;">
                    <p style="font-size:25px; letter-spacing:5px; margin:0;">|||| | || ||| | ||</p>
                    <p style="font-size:10px; margin:0;">{co['id']}00567512</p>
                </div>
                <table class="waybill-table">
                    <tr><th colspan="2">Customer Details</th><th colspan="2">Order Summary</th></tr>
                    <tr>
                        <td colspan="2" style="width:50%;">
                            <b>Name:</b> {co['name']}<br>
                            <b>Addr:</b> {co['addr']}<br>
                            <b>Phone:</b> {co['phone']}
                        </td>
                        <td colspan="2">
                            <b>Delivery:</b> {co['delivery']:.2f}<br>
                            <b>Discount:</b> {co['discount']:.2f}<br>
                            <b>Grand Total: LKR {co['total']:.2f}</b>
                        </td>
                    </tr>
                </table>
                <p style="font-size:9px; text-align:center; margin-top:10px;">Waybill generated by Happy Shop ERP</p>
            </div>
            """
            st.markdown(bill_html, unsafe_allow_html=True)
            
            if st.button(f"Print & Dispatch {co['id']}", key=f"p_{idx}"):
                # Shipped වලට මාරු කිරීම
                for order in st.session_state.orders:
                    if order['id'] == co['id']: order['status'] = 'shipped'
                st.components.v1.html("<script>window.print();</script>", height=0)
                st.rerun()
