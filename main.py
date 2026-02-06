import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Happy Shop | Ultimate ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Stability) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. UI & PRINT STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metrics Layout */
    .metric-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
    .m-box { padding: 15px; border-radius: 10px; text-align: center; min-width: 130px; color: white; font-weight: bold; }
    .bg-p { background: #6e7681; } .bg-c { background: #238636; } .bg-n { background: #d29922; color: black; } 
    .bg-x { background: #da3633; } .bg-f { background: #30363d; } .bg-t { background: #1f6feb; }
    .val { font-size: 26px; display: block; }

    /* HERBAL CROWN WAYBILL DESIGN */
    @media print {
        body * { visibility: hidden; }
        .print-container, .print-container * { visibility: visible; }
        .print-container { 
            position: absolute; left: 0; top: 0; width: 500px; 
            color: black !important; background: white !important; 
            padding: 20px; border: 1.5px solid black; font-family: 'Courier New', Courier, monospace;
        }
        .bill-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .bill-table td, .bill-table th { border: 1px solid black; padding: 5px; font-size: 14px; text-align: left; }
        .barcode-area { text-align: center; padding: 15px 0; border-bottom: 1px solid black; }
        .barcode-text { font-size: 45px; letter-spacing: 5px; margin: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION (සියලුම පින්තූරවල තිබූ මෙනූ) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=50)
    st.markdown("<h2 style='color:#ffa500;'>HAPPY SHOP</h2>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    # Sub-menus Based on Uploaded Images
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Actions", ["New Order", "View Lead", "Order Search", "Add Lead", "Blacklist"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Actions", ["Ship & Print", "Shipped List", "Delivery Summary"])
    elif menu == "📦 GRN": sub = st.radio("Actions", ["New GRN", "GRN List", "Packing"])
    elif menu == "💰 Expense": sub = st.radio("Actions", ["New Expense", "View Expenses"])
    elif menu == "📊 Stocks": sub = st.radio("Actions", ["View Stocks", "Stock Adjustment", "Add Waste"])
    elif menu == "🛍️ Products": sub = st.radio("Actions", ["Create Product", "View Products"])

# --- 5. TOP SUMMARY CARDS ---
def get_count(status): return len([o for o in st.session_state.orders if o.get('status') == status])

if menu in ["🏠 Dashboard", "🧾 Orders"]:
    st.markdown(f"""
        <div class="metric-row">
            <div class="m-box bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-box bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-box bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-box bg-x">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-box bg-f">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-box bg-t">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. CORE FUNCTIONALITY ---

# 6.1 NEW ORDER (උඹේ පින්තූරෙ තිබුණු ඔක්කොම Fields එක්ක)
if sub in ["New Order", "Add Lead"]:
    st.subheader("📝 Customer & Order Entry Form")
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            city = st.selectbox("City", ["Colombo", "Kandy", "Galle", "Gampaha", "Other"])
            phone1 = st.text_input("Contact Number 1 *")
            phone2 = st.text_input("Contact Number 2")
            source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "TikTok"])
        with c2:
            prod = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Herbal Crown 1", "Kalkaya"])
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Sale Amount", value=2950.0)
            weight = st.number_input("Pkg Weight(kgs)", value=0.5)
            delivery = st.number_input("Delivery Charge", value=350.0)
            discount = st.number_input("Discount (-)", value=0.0)
            courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
        
        if st.form_submit_button("💾 SAVE ORDER"):
            if name and phone1:
                order_id = f"{len(st.session_state.orders) + 1574392}"
                st.session_state.orders.append({
                    "id": order_id, "name": name, "phone": phone1, "addr": addr, "city": city,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, 
                    "discount": discount, "total": (price * qty) + delivery - discount,
                    "status": "pending", "date": str(date.today()), "courier": courier
                })
                st.success("Lead Added Successfully!")
                st.rerun()

# 6.2 VIEW LEAD (Fake Button එක සහ Error එක Fix කරලා)
elif sub == "View Lead":
    st.subheader("📋 Leads Management Table")
    if not st.session_state.orders:
        st.info("No orders found.")
    else:
        for idx, o in enumerate(st.session_state.orders):
            # KeyError වැළැක්වීමට safe get පාවිච්චි කළා
            with st.expander(f"Order: {o.get('id', 'N/A')} - {o.get('name', 'Customer')}"):
                st.write(f"📞 {o.get('phone')} | 💰 LKR {o.get('total')}")
                cols = st.columns(5)
                if cols[0].button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()
                if cols[4].button("Ship 🚚", key=f"s_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()

# 6.3 SHIP & PRINT (පින්තූරයේ පරිදිම Herbal Crown Waybill)
elif sub == "Ship & Print":
    st.subheader("🚚 Dispatch & Waybill Printing")
    to_ship = [o for o in st.session_state.orders if o['status'] == 'confirm']
    
    for idx, o in enumerate(to_ship):
        # පින්තූරය c54e37... හි ඇති ආකාරයටම ඩිසයින් එක
        st.markdown(f"""
        <div class="print-container">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;">Herbal Crown Pvt Ltd</h2>
                <div style="text-align:right; font-size:13px;">
                    Date: {o['date']}<br>ID: {o['id']}
                </div>
            </div>
            <p style="margin:0; font-size:13px;">TP: 0766066789</p>
            <div class="barcode-area">
                <p class="barcode-text">|||||||||||||||||||||</p>
                <p style="margin:0; font-size:12px;">RA02989179</p>
            </div>
            <div style="padding:10px 0; font-weight:bold; border-bottom:1px solid black;">
                {o['prod']} x {o['qty']}
            </div>
            <table class="bill-table">
                <tr><th style="width:55%;">Customer Details</th><th colspan="2">Order Summary</th></tr>
                <tr>
                    <td rowspan="4">
                        <b>Name:</b> {o['name']}<br>
                        <b>Addr:</b> {o['addr']}<br>
                        <b>City:</b> {o['city']}<br>
                        <b>Contacts:</b> {o['phone']}
                    </td>
                    <td>Order Total</td><td>{o['price']:.2f}</td>
                </tr>
                <tr><td>Delivery Cost</td><td>{o['delivery']:.2f}</td></tr>
                <tr><td>Discount (-)</td><td>{o['discount']:.2f}</td></tr>
                <tr><td>Paid (-)</td><td>0.00</td></tr>
                <tr style="background:#f0f0f0;">
                    <th colspan="1">Grand Total</th>
                    <th colspan="2" style="text-align:right;">LKR {o['total']:.2f}</th>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Print & Ship {o['id']}", key=f"prnt_{idx}"):
            st.components.v1.html("<script>window.print();</script>", height=0)
            # Shipped වලට මාරු කිරීම
            for order in st.session_state.orders:
                if order['id'] == o['id']: order['status'] = 'shipped'
            st.rerun()

# --- 7. OTHER SECTIONS ---
else:
    st.title(f"{menu} > {sub}")
    st.info("මෙම අංශය සඳහා දත්ත ඇතුළත් කරමින් පවතී. (GRN / Stocks / Expense)")
