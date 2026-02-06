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
# SESSION STATE INIT
# --------------------------------------------------
if "orders" not in st.session_state:
    st.session_state.orders = {}

if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "Kesharaja Hair Oil [VGLS0005]": 100,
        "Crown 1": 50,
        "Kalkaya": 75
    }

if "print_order" not in st.session_state:
    st.session_state.print_order = None

# --------------------------------------------------
# CSS (UI & PRINT DESIGN)
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background:#0d1117; color:#c9d1d9; }
[data-testid=stSidebar] { background:#161b22; }

/* Dashboard Metrics */
.metric-container {
    display:flex; gap:10px; flex-wrap:wrap;
    padding: 10px 0;
}
.m-card {
    padding:12px; border-radius:10px;
    min-width:120px; text-align:center;
    font-weight:bold; color:white;
}
.bg-pending{background:#6c757d;}
.bg-confirm{background:#28a745;}
.bg-noanswer{background:#ffc107;color:black;}
.bg-cancel{background:#dc3545;}
.bg-fake{background:#343a40;}
.bg-shipped{background:#0dcaf0;}
.bg-total{background:#007bff;}
.val{font-size:24px; display:block;}

/* LOGO STYLING */
.sidebar-logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 80px;
    border-radius: 50%;
    border: 3px solid #ffa500;
}

/* WAYBILL PRINT DESIGN */
@media print {
    body * { visibility:hidden; }
    .print-area, .print-area * { visibility:visible; }
    .print-area {
        position:absolute; left:0; top:0; width:550px;
        background:white !important; color:black !important;
        padding:20px; border:2px solid black;
        font-family: 'Arial', sans-serif;
    }
    .print-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid black; padding-bottom: 10px; }
    .print-logo { width: 120px; }
    .barcode-placeholder { font-size: 40px; font-family: 'Libre Barcode 39', cursive; text-align: center; margin: 10px 0; letter-spacing: 5px; }
    .bill-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .bill-table td, .bill-table th { border: 1px solid black; padding: 8px; text-align: left; font-size: 13px; }
    .total-row { background: #f2f2f2 !important; font-weight: bold; font-size: 16px; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def count_status(s):
    return len([o for o in st.session_state.orders.values() if o["order"]["status"] == s])

def new_order_id():
    return "HS-" + uuid.uuid4().hex[:8].upper()

# --------------------------------------------------
# SIDEBAR (LOGO ADDED)
# --------------------------------------------------
with st.sidebar:
    # HAPPY SHOP LOGO
    st.markdown("""
        <img src="https://i.ibb.co/L9P8VvG/happy-shop-logo.png" class="sidebar-logo">
        <h2 style='color:#ffa500;text-align:center;margin-top:10px;'>HAPPY SHOP</h2>
    """, unsafe_allow_html=True)
    
    menu = st.selectbox("MAIN MENU", [
        "🏠 Dashboard",
        "🧾 Orders",
        "🚚 Dispatch",
        "📦 Stocks",
        "🔍 Tracking"
    ])

    sub = ""
    if menu == "🧾 Orders":
        sub = st.radio("Orders", ["New Order", "View Leads"])
    if menu == "🚚 Dispatch":
        sub = "Dispatch"

# --------------------------------------------------
# METRICS
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
# NEW ORDER
# --------------------------------------------------
if sub == "New Order":
    st.subheader("📝 New Order Entry")
    with st.form("order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone *")
            address = st.text_area("Address *")
            city = st.text_input("City")
        with c2:
            product = st.selectbox("Product", list(st.session_state.stocks.keys()))
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Price", value=2950.0)
            delivery = st.number_input("Delivery", value=350.0)
            discount = st.number_input("Discount", value=0.0)
        submit = st.form_submit_button("SAVE ORDER")

    if submit:
        if not name or not phone:
            st.error("Name & Phone required")
        else:
            oid = new_order_id()
            st.session_state.orders[oid] = {
                "customer": {"name": name, "phone": phone, "address": address, "city": city},
                "order": {"product": product, "qty": qty, "price": price, "delivery": delivery, "discount": discount, 
                          "total": price * qty + delivery - discount, "status": "pending"},
                "date": str(date.today())
            }
            st.success(f"Order {oid} created")
            st.rerun()

# --------------------------------------------------
# VIEW LEADS (WITH FAKE BUTTON)
# --------------------------------------------------
elif sub == "View Leads":
    st.subheader("📋 Leads Management")
    for oid, o in st.session_state.orders.items():
        with st.expander(f"{oid} | {o['customer']['name']} ({o['order']['status']})"):
            st.write(f"📞 {o['customer']['phone']} | 📍 {o['customer']['address']}, {o['customer']['city']}")
            c = st.columns(4)
            if c[0].button("Confirm ✅", key=f"c{oid}"):
                st.session_state.orders[oid]["order"]["status"] = "confirm"
                st.rerun()
            if c[1].button("No Answer ☎", key=f"n{oid}"):
                st.session_state.orders[oid]["order"]["status"] = "noanswer"
                st.rerun()
            if c[2].button("Cancel ❌", key=f"x{oid}"):
                st.session_state.orders[oid]["order"]["status"] = "cancel"
                st.rerun()
            if c[3].button("Fake ⚠️", key=f"f{oid}"):
                st.session_state.orders[oid]["order"]["status"] = "fake"
                st.rerun()

# --------------------------------------------------
# DISPATCH & HERBAL CROWN WAYBILL
# --------------------------------------------------
elif menu == "🚚 Dispatch":
    st.subheader("🚚 Ready to Dispatch")
    confirmed_orders = {k: v for k, v in st.session_state.orders.items() if v["order"]["status"] == "confirm"}
    
    if not confirmed_orders:
        st.info("No confirmed orders to display.")
    
    for oid, o in confirmed_orders.items():
        # HERBAL CROWN PROFESSIONAL BILL DESIGN
        st.markdown(f"""
        <div class="print-area">
            <div class="print-header">
                <div>
                    <img src="https://i.ibb.co/vYf3C7S/herbal-crown-logo.png" class="print-logo">
                    <h2 style="margin:0;">Herbal Crown Pvt Ltd</h2>
                </div>
                <div style="text-align:right;">
                    <b>ID:</b> {oid}<br>
                    <b>Date:</b> {o['date']}
                </div>
            </div>
            
            <div class="barcode-placeholder">|||| ||| || |||| |||</div>
            
            <table class="bill-table">
                <tr>
                    <th style="width:50%">Customer Details</th>
                    <th>Payment Summary</th>
                </tr>
                <tr>
                    <td>
                        <b>{o['customer']['name']}</b><br>
                        {o['customer']['address']}<br>
                        {o['customer']['city']}<br>
                        <b>TP: {o['customer']['phone']}</b>
                    </td>
                    <td>
                        Order Total: {o['order']['price'] * o['order']['qty']:.2f}<br>
                        Delivery: {o['order']['delivery']:.2f}<br>
                        Discount: -{o['order']['discount']:.2f}
                    </td>
                </tr>
                <tr class="total-row">
                    <td>Items: {o['order']['product']} (x{o['order']['qty']})</td>
                    <td>Grand Total: LKR {o['order']['total']:.2f}</td>
                </tr>
            </table>
            <p style="text-align:center; font-size:10px; margin-top:15px;">Thank you for shopping with Happy Shop!</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🖨 Print & Ship {oid}", key=f"p{oid}"):
            st.session_state.print_order = oid
            st.rerun()

# --------------------------------------------------
# AUTOMATIC PRINT & STOCK UPDATE
# --------------------------------------------------
if st.session_state.print_order:
    oid = st.session_state.print_order
    # Status Update
    st.session_state.orders[oid]["order"]["status"] = "shipped"
    # Stock Update
    prod_name = st.session_state.orders[oid]["order"]["product"]
    st.session_state.stocks[prod_name] -= st.session_state.orders[oid]["order"]["qty"]

    st.components.v1.html(f"""
    <script>
      window.print();
      setTimeout(() => {{ window.location.reload(); }}, 1000);
    </script>
    """, height=0)
    st.session_state.print_order = None

# (Stocks & Tracking modules remain same or slightly updated)
elif menu == "📦 Stocks":
    st.subheader("📦 Stock Inventory")
    st.table(st.session_state.stocks)

elif menu == "🔍 Tracking":
    st.subheader("🔍 Order Tracking")
    q = st.text_input("Enter Phone Number")
    if q:
        results = [f"{oid} -> {o['order']['status'].upper()}" for oid, o in st.session_state.orders.items() if q in o["customer"]["phone"]]
        if results:
            for r in results: st.success(r)
        else: st.error("No records found.")
