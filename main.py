import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Happy Shop | Enterprise ERP", layout="wide")

# --- 2. DATA STABILITY (KeyError Fix) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. PROFESSIONAL CSS & REAL WAYBILL DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Metrics Styling */
    .metric-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
    .m-box { padding: 15px; border-radius: 8px; text-align: center; min-width: 140px; color: white; font-weight: bold; }
    .bg-p { background: #6e7681; } .bg-c { background: #238636; } .bg-n { background: #d29922; color: black; } 
    .bg-x { background: #da3633; } .bg-f { background: #30363d; } .bg-t { background: #1f6feb; }
    .val { font-size: 26px; display: block; }

    /* HERBAL CROWN WAYBILL PRINT DESIGN (Exact Layout) */
    @media print {
        body * { visibility: hidden; }
        .print-waybill, .print-waybill * { visibility: visible; }
        .print-waybill { 
            position: absolute; left: 0; top: 0; width: 500px; 
            color: black !important; background: white !important; 
            padding: 10px; border: 1px solid black; font-family: Arial, sans-serif;
        }
        .waybill-header { display: flex; justify-content: space-between; border-bottom: 1px solid black; padding-bottom: 5px; }
        .barcode-section { text-align: center; padding: 10px 0; border-bottom: 1px solid black; }
        .barcode-img { font-size: 50px; letter-spacing: 5px; margin: 0; }
        .waybill-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 5px; font-size: 13px; text-align: left; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION (පින්තූරවල ඇති සියලුම මෙනූ) ---
with st.sidebar:
    st.title("HAPPY SHOP")
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    # Sub-menus based on your images
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Order Menu", ["New Order", "View Lead", "Order Search", "Add Lead", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Shipping", ["Ship", "Shipped List", "Print Dispatch Items"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List", "Packing"])
    elif menu == "💰 Expense": sub = st.radio("Expense Menu", ["New Expense", "View Expenses"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Stock Adjustment", "Add Waste"])
    elif menu == "🛍️ Products": sub = st.radio("Product Menu", ["Create Product", "View Products"])

# --- 5. TOP STATUS CARDS ---
def count_st(status): return len([o for o in st.session_state.orders if o.get('status') == status])
st.markdown(f"""
    <div class="metric-row">
        <div class="m-box bg-p">PENDING<span class="val">{count_st('pending')}</span></div>
        <div class="m-box bg-c">CONFIRMED<span class="val">{count_st('confirm')}</span></div>
        <div class="m-box bg-n">NO ANSWER<span class="val">{count_st('noanswer')}</span></div>
        <div class="m-box bg-x">CANCEL/HOLD<span class="val">{count_st('cancel')}</span></div>
        <div class="m-box bg-f">FAKE<span class="val">{count_st('fake')}</span></div>
        <div class="m-box bg-t">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 6. CORE LOGIC ---

# 6.1 NEW ORDER (උඹේ පින්තූරෙ තිබුණු ඔක්කොම Fields එක්ක)
if sub in ["New Order", "Add Lead"]:
    st.subheader("📝 New Order Entry")
    with st.form("full_order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            city = st.text_input("City")
            p1 = st.text_input("Contact Number 1 *")
            p2 = st.text_input("Contact Number 2")
            source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "TikTok"])
        with c2:
            prod = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Herbal Crown 1", "Kalkaya"])
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Sale Amount", value=2950.0)
            delivery = st.number_input("Delivery Charge", value=350.0)
            discount = st.number_input("Discount (-)", value=0.0)
            courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
        
        if st.form_submit_button("SAVE RECORD"):
            if name and p1:
                # KeyError නොවන්නට සියලුම Keys ඇතුළත් කිරීම
                new_id = str(len(st.session_state.orders) + 1574392)
                st.session_state.orders.append({
                    "id": new_id, "name": name, "phone": p1, "addr": addr, "city": city,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, 
                    "discount": discount, "total": (price * qty) + delivery - discount,
                    "status": "pending", "date": str(date.today()), "courier": courier
                })
                st.success("Order Saved!")
                st.rerun()

# 6.2 VIEW LEAD (ERROR FIXED)
elif sub == "View Lead":
    st.subheader("📋 Leads Management")
    if not st.session_state.orders:
        st.info("No leads available.")
    else:
        for idx, o in enumerate(st.session_state.orders):
            # SAFE DATA ACCESS (.get() පාවිච්චි කළා KeyError එක මකන්න)
            with st.expander(f"{o.get('id', 'N/A')} - {o.get('name', 'Unknown')}"):
                st.write(f"📞 {o.get('phone')} | 📍 {o.get('city')}")
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if b2.button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if b3.button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if b4.button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()

# 6.3 SHIP & PRINT (HERBAL CROWN Pvt Ltd Exact Design)
elif sub == "Ship":
    st.subheader("🚚 Print Waybills")
    to_ship = [o for o in st.session_state.orders if o.get('status') == 'confirm']
    
    if not to_ship:
        st.warning("No confirmed orders to print.")
    else:
        for idx, co in enumerate(to_ship):
            # පින්තූරයේ තිබූ ආකාරයටම බිල් එක නිර්මාණය කිරීම
            st.markdown(f"""
            <div class="print-waybill">
                <div class="waybill-header">
                    <div><b>Herbal Crown Pvt Ltd</b><br>TP: 0766066789</div>
                    <div style="text-align:right;">Date: {co.get('date')}<br>ID: {co.get('id')}</div>
                </div>
                <div class="barcode-section">
                    <p class="barcode-img">|||||||||||||||||||</p>
                    <small>RA02989179</small>
                </div>
                <div style="padding:10px 0; font-weight:bold;">{co.get('prod')} x {co.get('qty')}</div>
                <table class="waybill-table">
                    <tr><th style="width:50%;">Customer Details</th><th colspan="2">Order Summary</th></tr>
                    <tr>
                        <td rowspan="4">
                            <b>Name:</b> {co.get('name')}<br>
                            <b>Addr:</b> {co.get('addr')}<br>
                            <b>Tel:</b> {co.get('phone')}
                        </td>
                        <td>Order Total</td><td>{co.get('price'):.2f}</td>
                    </tr>
                    <tr><td>Delivery Cost</td><td>{co.get('delivery'):.2f}</td></tr>
                    <tr><td>Discount (-)</td><td>{co.get('discount'):.2f}</td></tr>
                    <tr style="background:#eee;"><td><b>Grand Total</b></td><td><b>LKR {co.get('total'):.2f}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Print & Ship {co.get('id')}", key=f"p_{idx}"):
                st.components.v1.html("<script>window.print();</script>", height=0)
                for order in st.session_state.orders:
                    if order['id'] == co['id']: order['status'] = 'shipped'
                st.rerun()

# 6.4 OTHER SECTIONS (Placeholder for future data)
else:
    st.title(f"{menu} - {sub}")
    st.info("System operational. Section under data migration.")
