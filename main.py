import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Stability) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'stocks' not in st.session_state:
    # Default stocks for products
    st.session_state.stocks = {
        "Kesharaja Hair Oil [VGLS0005]": 50,
        "Crown 1": 30,
        "Kalkaya": 25
    }
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. LOGIN SYSTEM ---
def login():
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pw == "happy123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- 4. PROFESSIONAL CSS & PRINTING DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 12px; border-radius: 10px; text-align: center; min-width: 120px; color: white; font-weight: bold; font-size: 14px; }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; margin-top: 5px; }

    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 500px; color: black !important; background: white !important; padding: 15px; border: 2px solid black; font-family: 'Inter', sans-serif; }
        .waybill-header { display: flex; justify-content: space-between; border-bottom: 2px solid black; padding-bottom: 5px; }
        .barcode-section { display: flex; border-bottom: 2px solid black; }
        .barcode-box { flex: 3; text-align: center; border-right: 2px solid black; padding: 10px; font-size: 30px; letter-spacing: 5px; }
        .qty-box { flex: 1; text-align: center; padding: 10px; font-weight: bold; font-size: 20px; }
        .waybill-table { width: 100%; border-collapse: collapse; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 6px; font-size: 12px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. HELPERS ---
def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Order Menu", ["New Order", "View Lead", "Order Tracking", "Add Lead"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Shipping Menu", ["Dispatch & Bulk Print", "Shipped List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment"])

# --- 7. DASHBOARD (Financials & Export) ---
if menu == "🏠 Dashboard":
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
    
    

    st.subheader("📊 Financial Summary & Reports")
    shipped_orders = [o for o in st.session_state.orders if o['status'] == 'shipped']
    rev = sum([o['total'] for o in shipped_orders])
    deliv = sum([o['delivery'] for o in shipped_orders])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue (Shipped)", f"LKR {rev:,.2f}")
    c2.metric("Delivery Collected", f"LKR {deliv:,.2f}")
    
    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)
        csv = df.to_csv(index=False).encode('utf-8')
        c3.download_button("📥 Export to Excel (CSV)", data=csv, file_name=f"orders_{date.today()}.csv", mime="text/csv")

    # Low Stock Alert
    st.subheader("⚠️ Inventory Alerts")
    for item, qty in st.session_state.stocks.items():
        if qty < 10:
            st.error(f"Low Stock: {item} - Only {qty} remaining!")

# --- 8. ORDERS ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        st.subheader("📝 New Order Entry")
        with st.form("full_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                address = st.text_area("Address *")
                phone1 = st.text_input("Contact Number 1 *")
                city = st.text_input("City")
                district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            with c2:
                prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Sale Amount", value=2950.0)
                delivery = st.number_input("Delivery Charge", value=350.0)
                discount = st.number_input("Discount", value=0.0)
                courier = st.selectbox("Courier", ["Koombiyo", "Domex", "Pronto"])

            if st.form_submit_button("🚀 SAVE ORDER"):
                if name and phone1:
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone1, "addr": address, "city": city,
                        "dist": district, "prod": prod, "qty": qty, "price": price, 
                        "delivery": delivery, "discount": discount, "total": (price * qty) + delivery - discount,
                        "status": "pending", "date": str(date.today()), "courier": courier
                    })
                    st.success(f"Order {oid} Saved!")
                    st.rerun()

    elif sub == "View Lead":
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"{o['id']} - {o['name']} ({o['status'].upper()})"):
                cols = st.columns(5)
                if cols[0].button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()

# --- 9. DISPATCH & BULK PRINT (Herbal Crown Pvt Ltd) ---
elif sub == "Dispatch & Bulk Print":
    st.subheader("🚚 Bulk Printing & Dispatch")
    ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
    
    if not ready:
        st.info("No confirmed orders to print.")
    else:
        if st.button("🖨️ PRINT ALL CONFIRMED ORDERS"):
            st.components.v1.html("<script>window.print();</script>", height=0)
            for o in st.session_state.orders:
                if o['status'] == 'confirm':
                    # Inventory auto-deduct
                    st.session_state.stocks[o['prod']] -= o['qty']
                    o['status'] = 'shipped'
            st.rerun()

        for idx, ro in enumerate(ready):
            st.markdown(f"""
            <div class="print-area" style="margin-bottom: 50px;">
                <div class="waybill-header">
                    <div><b>Herbal Crown Pvt Ltd</b><br>TP: 0766066789</div>
                    <div style="text-align:right;">Date: {ro['date']}<br>ID: {ro['id']}</div>
                </div>
                <div class="barcode-section">
                    <div class="barcode-box">||||||||||||||||||||</div>
                    <div class="qty-box">QTY: {ro['qty']}</div>
                </div>
                <table class="waybill-table">
                    <tr><th style="width:60%;">Customer Details</th><th>Payment</th></tr>
                    <tr>
                        <td><b>{ro['name']}</b><br>{ro['addr']}<br>Tel: {ro['phone']}</td>
                        <td>Total: LKR {ro['total']:.2f}<br>Courier: {ro['courier']}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

# --- 10. STOCKS ---
elif menu == "📊 Stocks":
    st.subheader("📦 Inventory Management")
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Product", "Quantity"]))
    
    if sub == "Adjustment":
        with st.form("stock_form"):
            p = st.selectbox("Product", list(st.session_state.stocks.keys()))
            q = st.number_input("Add/Remove Qty", value=0)
            if st.form_submit_button("Update Stock"):
                st.session_state.stocks[p] += q
                st.success("Stock Updated!")
                st.rerun()
