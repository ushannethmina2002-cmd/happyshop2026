import streamlit as st
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Ultimate ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOADERS & SESSION STATE ---
districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]
cities = ["Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya", "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya", "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"]

if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = date.today()

# Daily Reset Logic: දවස මාරු වූ විට දත්ත සීරෝ (0) කරයි
if st.session_state.last_reset_date != date.today():
    st.session_state.orders = []
    st.session_state.last_reset_date = date.today()

# --- 3. STATUS UPDATE LOGIC (QUERY PARAMS) ---
# Table එකේ බටන් එබූ විට counts real-time update වීමට මෙය භාවිතා වේ
query_params = st.query_params
if "update_id" in query_params and "new_status" in query_params:
    u_id = int(query_params["update_id"])
    u_status = query_params["new_status"]
    for order in st.session_state.orders:
        if order['id'] == u_id:
            order['status'] = u_status
    st.query_params.clear()
    st.rerun()

# --- 4. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 5. PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metrics / Buttons Styling */
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
    .m-card {
        padding: 10px 12px; border-radius: 8px; text-align: center; min-width: 110px;
        color: white; font-weight: bold; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .bg-pending { background: #6c757d; } /* අළු පාට */
    .bg-confirm { background: #28a745; } /* කොළ පාට */
    .bg-noanswer { background: #ffc107; color: black; } /* කහ පාට */
    .bg-cancel { background: #dc3545; } /* රතු පාට */
    .bg-fake { background: #343a40; } 
    .bg-total { background: #007bff; }
    .val { font-size: 20px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "📊 Stocks"])
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Add Lead", "Order History", "Search Waybills"])
    
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

# --- 7. TOP METRIC CARDS (Visible on Dashboard & View Lead) ---
if menu == "🏠 Dashboard" or (menu == "🧾 Orders" and sub_menu == "View Lead"):
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL LEADS<span class="val">{get_count('total')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 8. PAGE CONTENT ---
if menu == "🏠 Dashboard":
    st.title("Business Summary")
    st.info(f"System Operational. Today's Date: {date.today()}")

elif menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
    st.subheader(f"📝 {sub_menu}")
    with st.form("pro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            dist = st.selectbox("Select District *", sorted(districts))
            city = st.selectbox("Select City *", sorted(cities))
            phone1 = st.text_input("Contact Number One *")
            phone2 = st.text_input("Contact Number Two")
        with col2:
            p_item = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1 [VGLS0001]", "Kalkaya [VGLS0003]"])
            p_qty = st.number_input("Qty", min_value=1, value=1)
            p_amt = st.number_input("Sale Amount", min_value=0.0)
            s_charge = st.number_input("Delivery Charge", min_value=0.0)
            p_disc = st.number_input("Discount", min_value=0.0)
            source = st.selectbox("Source", ["Facebook", "WhatsApp", "TikTok", "Google"])
        
        if st.form_submit_button("🚀 SAVE ORDER / LEAD"):
            if name and phone1:
                new_id = len(st.session_state.orders) + 1
                st.session_state.orders.append({
                    "id": new_id, "order_id": f"HS-{821384+new_id}", 
                    "customer": name, "phone": phone1, "status": "pending",
                    "amount": (p_amt * p_qty) + s_charge - p_disc
                })
                st.success("Lead Saved Successfully!")
                st.rerun()

elif menu == "🧾 Orders" and sub_menu == "View Lead":
    st.subheader("📋 Leads Management Table")
    
    rows_html = ""
    for order in st.session_state.orders:
        row_bg = "background: rgba(255,255,255,0.02);"
        if order['status'] == 'confirm': row_bg = "background: rgba(40,167,69,0.1);"
        elif order['status'] == 'noanswer': row_bg = "background: rgba(255,193,7,0.1);"
        elif order['status'] == 'cancel': row_bg = "background: rgba(220,53,69,0.1);"

        rows_html += f"""
        <tr style="{row_bg}">
            <td>{order['order_id']}</td><td>{order['customer']}</td><td>{order['phone']}</td>
            <td><span class="badge {order['status']}">{order['status'].upper()}</span></td>
            <td>
                <a href="?update_id={order['id']}&new_status=confirm" target="_self"><button class="btn-s btn-confirm">✔</button></a>
                <a href="?update_id={order['id']}&new_status=noanswer" target="_self"><button class="btn-s btn-noanswer">☎</button></a>
                <a href="?update_id={order['id']}&new_status=cancel" target="_self"><button class="btn-s btn-cancel">✖</button></a>
                <a href="?update_id={order['id']}&new_status=fake" target="_self"><button class="btn-s btn-fake">⚠</button></a>
            </td>
        </tr>"""

    html_table = f"""
    <html><head><style>
        table {{ width:100%; border-collapse:collapse; color:#e1e1e1; font-family:sans-serif; background:#161b22; }}
        th, td {{ padding:10px; border:1px solid #30363d; text-align:left; font-size:13px; }}
        th {{ background:#21262d; color:#ffa500; text-transform:uppercase; }}
        .badge {{ padding:4px 8px; border-radius:4px; font-size:10px; font-weight:bold; }}
        .pending {{ background:#6c757d; }} .confirm {{ background:#28a745; }} .noanswer {{ background:#ffc107; color:black; }} .cancel {{ background:#dc3545; }} .fake {{ background:#343a40; }}
        .btn-s {{ border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold; color:white; margin-right:4px; text-decoration:none; }}
        .btn-confirm {{ background:#28a745; }} .btn-noanswer {{ background:#ffc107; color:black; }} .btn-cancel {{ background:#dc3545; }} .btn-fake {{ background:#343a40; }}
    </style></head>
    <body><table><thead><tr><th>ID</th><th>Customer</th><th>Phone</th><th>Status</th><th>Action</th></tr></thead>
    <tbody>{rows_html}</tbody></table></body></html>
    """
    components.html(html_table, height=500, scrolling=True)
