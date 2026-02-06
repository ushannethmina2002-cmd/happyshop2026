import streamlit as st
from datetime import date, datetime
import uuid

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Happy Shop | Enterprise ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE INIT (Data Stability)
# --------------------------------------------------
if "orders" not in st.session_state:
    st.session_state.orders = {}

if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "Kesharaja Hair Oil [VGLS0005]": 100,
        "Crown 1": 50,
        "Kalkaya": 75
    }

# --------------------------------------------------
# PROFESSIONAL CSS (UI & PRINT DESIGN)
# --------------------------------------------------
st.markdown("""
<style>
/* Dashboard Theme */
.stApp { background:#0d1117; color:#c9d1d9; }
[data-testid=stSidebar] { background:#161b22; }

/* Metrics Styling */
.metric-container { display:flex; gap:10px; flex-wrap:wrap; margin-bottom: 20px; }
.m-card { padding:12px; border-radius:10px; min-width:120px; text-align:center; font-weight:bold; color:white; }
.bg-pending{background:#6c757d;} .bg-confirm{background:#28a745;} 
.bg-noanswer{background:#ffc107;color:black;} .bg-cancel{background:#dc3545;}
.bg-fake{background:#343a40;} .bg-shipped{background:#0dcaf0;} .bg-total{background:#007bff;}
.val{font-size:24px; display:block;}

/* SIDEBAR LOGO */
.sb-logo { display: block; margin: 0 auto 10px auto; width: 100px; border-radius: 50%; border: 3px solid #ffa500; }

/* HERBAL CROWN WAYBILL DESIGN (Fixed for Printing) */
@media print {
    body * { visibility:hidden; }
    .print-area, .print-area * { visibility:visible; }
    .print-area {
        position:absolute; left:0; top:0; width:550px;
        background:white !important; color:black !important;
        padding:15px; border:2px solid black; font-family: 'Arial', sans-serif;
    }
    .bill-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid black; padding-bottom: 5px; }
    .barcode-section { display: flex; border-bottom: 2px solid black; }
    .barcode-box { flex: 3; text-align: center; border-right: 2px solid black; padding: 10px; font-size: 35px; letter-spacing: 5px; }
    .qty-box { flex: 1; text-align: center; padding: 10px; font-size: 20px; font-weight: bold; }
    .bill-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
    .bill-table td, .bill-table th { border: 1px solid black; padding: 6px; font-size: 13px; text-align: left; }
    .total-row { background: #f2f2f2 !important; font-weight: bold; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def count_status(s):
    return len([o for o in st.session_state.orders.values() if o["order"]["status"] == s])

# --------------------------------------------------
# SIDEBAR (Happy Shop Logo Added)
# --------------------------------------------------
with st.sidebar:
    st.markdown("""
        <img src="https://i.ibb.co/L9P8VvG/happy-shop-logo.png" class="sb-logo">
        <h2 style='color:#ffa500;text-align:center;'>HAPPY SHOP</h2>
    """, unsafe_allow_html=True)
    
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Dispatch", "📦 Stocks", "🔍 Tracking"])
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Actions", ["New Order", "View Leads"])

# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------
st.markdown(f"""
<div class="metric-container">
 <div class="m-card bg-pending">Pending<span class="val">{count_status("pending")}</span></div>
 <div class="m-card bg-confirm">Confirmed<span class="val">{count_status("confirm")}</span></div>
 <div class="m-card bg-noanswer">No Answer<span class="val">{count_status("noanswer")}</span></div>
 <div class="m-card bg-cancel">Cancel<span class="val">{count_status("cancel")}</span></div>
 <div class="m-card bg-fake">Fake<span class="val">{count_status("fake")}</span></div>
 <div class="m-card bg-shipped">Shipped<span class="val">{count_status("shipped")}</span></div>
 <div class="m-card bg-total">Total<span class="val">{len(st.session_state.orders)}</span></div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# NEW ORDER (Full Fields)
# --------------------------------------------------
if sub == "New Order":
    st.subheader("📝 New Order Entry")
    with st.form("main_order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone *")
            address = st.text_area("Address *")
            city = st.text_input("City")
            district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
        with c2:
            product = st.selectbox("Product", list(st.session_state.stocks.keys()))
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Price", value=2950.0)
            weight = st.number_input("Weight (kg)", value=0.5)
            courier = st.selectbox("Courier", ["Koombiyo", "Domex", "Pronto"])
            delivery = st.number_input("Delivery", value=350.0)
            discount = st.number_input("Discount", value=0.0)
        
        if st.form_submit_button("SAVE ORDER"):
            if name and phone:
                oid = "HS-" + uuid.uuid4().hex[:6].upper()
                st.session_state.orders[oid] = {
                    "customer": {"name": name, "phone": phone, "address": address, "city": city, "dist": district},
                    "order": {"product": product, "qty": qty, "price": price, "delivery": delivery, 
                              "discount": discount, "total": (price * qty) + delivery - discount, "status": "pending", "courier": courier},
                    "date": str(date.today())
                }
                st.success(f"Order {oid} Saved!")
                st.rerun()

# --------------------------------------------------
# VIEW LEADS (Fake Button Added)
# --------------------------------------------------
elif sub == "View Leads":
    st.subheader("📋 Leads Management")
    for oid, o in st.session_state.orders.items():
        with st.expander(f"{oid} | {o['customer']['name']} ({o['order']['status']})"):
            st.write(f"📞 {o['customer']['phone']} | 📍 {o['customer']['address']}")
            cols = st.columns(4)
            if cols[0].button("Confirm ✅", key=f"c{oid}"): o["order"]["status"] = "confirm"; st.rerun()
            if cols[1].button("No Answer ☎", key=f"n{oid}"): o["order"]["status"] = "noanswer"; st.rerun()
            if cols[2].button("Cancel ❌", key=f"x{oid}"): o["order"]["status"] = "cancel"; st.rerun()
            if cols[3].button("Fake ⚠️", key=f"f{oid}"): o["order"]["status"] = "fake"; st.rerun()

# --------------------------------------------------
# DISPATCH & HERBAL CROWN BILL
# --------------------------------------------------
elif menu == "🚚 Dispatch":
    st.subheader("🚚 Ready to Print & Dispatch")
    confirmed = {k: v for k, v in st.session_state.orders.items() if v["order"]["status"] == "confirm"}
    
    for oid, o in confirmed.items():
        st.markdown(f"""
        <div class="print-area">
            <div class="bill-header">
                <div><b style="font-size:18px;">Herbal Crown Pvt Ltd</b><br>TP: 0766066789</div>
                <div style="text-align:right;">Date: {o['date']}<br>ID: {oid}</div>
            </div>
            <div class="barcode-section">
                <div class="barcode-box">|||| |||| |||| ||||</div>
                <div class="qty-box">QTY: {o['order']['qty']}</div>
            </div>
            <div style="padding:10px 0; font-weight:bold; border-bottom:1px solid black;">
                {o['order']['product']} (x{o['order']['qty']})
            </div>
            <table class="bill-table">
                <tr><th style="width:50%;">Customer Details</th><th colspan="2">Order Summary</th></tr>
                <tr>
                    <td rowspan="4"><b>{o['customer']['name']}</b><br>{o['customer']['address']}<br>{o['customer']['city']}<br>Tel: {o['customer']['phone']}</td>
                    <td>Price</td><td>{o['order']['price']:.2f}</td>
                </tr>
                <tr><td>Delivery</td><td>{o['order']['delivery']:.2f}</td></tr>
                <tr><td>Discount</td><td>{o['order']['discount']:.2f}</td></tr>
                <tr class="total-row"><td>Grand Total</td><td>LKR {o['order']['total']:.2f}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🖨 Print {oid}", key=f"btn{oid}"):
            # Update Stock & Status
            st.session_state.stocks[o['order']['product']] -= o['order']['qty']
            o["order"]["status"] = "shipped"
            st.components.v1.html("<script>window.print(); setTimeout(() => { window.location.reload(); }, 1000);</script>", height=0)

elif menu == "📦 Stocks":
    st.table(st.session_state.stocks)
