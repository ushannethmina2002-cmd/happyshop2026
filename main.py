import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | 1000% Pro ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Persistence) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = date.today()

# Daily Reset Logic
if st.session_state.last_reset_date != date.today():
    st.session_state.orders = []
    st.session_state.last_reset_date = date.today()

# --- 3. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 4. PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
    .m-card {
        padding: 10px; border-radius: 8px; text-align: center; min-width: 110px;
        color: white; font-weight: bold; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 22px; display: block; }
    
    /* Print Styles */
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; border: 2px dashed #000; padding: 20px; color: black; background: white; }
    }
    .print-only { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped & Dispatch", "📊 Stocks"])
    sub_menu = "View Lead"
    
    if menu == "🧾 Orders":
        sub_menu = st.radio("Actions", ["New Order", "View Lead", "Order Tracking"])
    elif menu == "🚚 Shipped & Dispatch":
        sub_menu = st.radio("Actions", ["Ship Items", "Dispatch List"])

# --- 6. ORDER TRACKING (NOTIFICATION SYSTEM) ---
if sub_menu == "Order Tracking":
    st.subheader("🔍 Search & Track Order")
    search_q = st.text_input("Enter Phone Number or Order ID")
    if search_q:
        found = [o for o in st.session_state.orders if search_q in o['phone'] or search_q in o['order_id']]
        if found:
            res = found[0]
            status_colors = {"pending": "gray", "confirm": "green", "noanswer": "orange", "cancel": "red", "shipped": "blue"}
            st.toast(f"Order Found: {res['status'].upper()}", icon="ℹ️")
            st.markdown(f"""
                <div style="padding:20px; border-radius:10px; background:rgba(255,165,0,0.1); border:1px solid orange;">
                    <h3>Status: <span style="color:{status_colors.get(res['status'], 'white')}">{res['status'].upper()}</span></h3>
                    <p><b>Customer:</b> {res['customer']} | <b>Phone:</b> {res['phone']}</p>
                    <p><b>Order ID:</b> {res['order_id']} | <b>Amount:</b> LKR {res['total']}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("No Order Found!")

# --- 7. METRIC CARDS ---
if menu == "🏠 Dashboard" or sub_menu == "View Lead":
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

# --- 8. PAGE CONTENT ---
if menu == "🏠 Dashboard":
    st.title("Business Summary")
    st.info(f"Today: {date.today()}")

elif sub_menu == "New Order":
    st.subheader("📝 Add New Order")
    with st.form("new_order_f"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name")
        phone = c1.text_input("Phone")
        addr = c1.text_area("Address")
        prod = c2.selectbox("Product", ["Hair Oil", "Crown 1", "Kalkaya"])
        amt = c2.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save Order"):
            new_id = len(st.session_state.orders) + 1
            st.session_state.orders.append({
                "id": new_id, "order_id": f"HS-{1000+new_id}", 
                "customer": name, "phone": phone, "status": "pending", "total": amt, "product": prod, "address": addr
            })
            st.success("Saved!")
            st.rerun()

elif sub_menu == "View Lead":
    st.subheader("📋 Orders Management")
    for idx, order in enumerate(st.session_state.orders):
        with st.expander(f"{order['order_id']} - {order['customer']} ({order['status'].upper()})"):
            c1, c2, c3 = st.columns([2,1,1])
            c1.write(f"📞 {order['phone']} | 📍 {order['address']}")
            if c2.button("Confirm ✔", key=f"conf_{idx}"):
                st.session_state.orders[idx]['status'] = "confirm"; st.rerun()
            if c3.button("Shipped 🚚", key=f"ship_{idx}"):
                st.session_state.orders[idx]['status'] = "shipped"; st.rerun()

elif sub_menu == "Ship Items":
    st.subheader("🚚 Ready to Ship & Waybill Print")
    ready_orders = [o for o in st.session_state.orders if o['status'] == 'confirm']
    if not ready_orders:
        st.write("No confirmed orders to ship.")
    else:
        for idx, ro in enumerate(ready_orders):
            col_a, col_b = st.columns([3, 1])
            col_a.info(f"Order: {ro['order_id']} | {ro['customer']} | LKR {ro['total']}")
            if col_b.button(f"Print & Dispatch", key=f"prnt_{idx}"):
                # Dispatch කරද්දී status එක shipped වෙයි
                for o in st.session_state.orders:
                    if o['order_id'] == ro['order_id']:
                        o['status'] = 'shipped'
                
                # WAYBILL PRINT PREVIEW (Pop-up style)
                st.markdown(f"""
                <div style="background:white; color:black; padding:20px; border:2px solid black; margin-top:10px;">
                    <h2 style="text-align:center;">HAPPY SHOP - WAYBILL</h2>
                    <hr>
                    <p><b>Order ID:</b> {ro['order_id']}</p>
                    <p><b>To:</b> {ro['customer']}</p>
                    <p><b>Address:</b> {ro['address']}</p>
                    <p><b>Phone:</b> {ro['phone']}</p>
                    <p><b>Product:</b> {ro['product']}</p>
                    <p><b>COD Amount: LKR {ro['total']}</b></p>
                    <hr>
                    <p style="text-align:center; font-size:10px;">Thank you for shopping with Happy Shop!</p>
                </div>
                <script>window.print();</script>
                """, unsafe_allow_html=True)
                st.success(f"Dispatched {ro['order_id']} Successfully!")

elif sub_menu == "Dispatch List":
    st.subheader("📦 Dispatched Orders (History)")
    dispatched = [o for o in st.session_state.orders if o['status'] == 'shipped']
    if dispatched:
        st.table(pd.DataFrame(dispatched)[['order_id', 'customer', 'phone', 'total']])
    else:
        st.write("No items dispatched yet.")
