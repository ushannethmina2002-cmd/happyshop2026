import streamlit as st
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Pro ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE & RESET LOGIC ---
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = date.today()

# දවස අලුත් වෙද්දී Data Reset කිරීමේ Logic එක
if st.session_state.last_reset_date != date.today():
    st.session_state.orders = [] # දවස අලුත් නම් ලිස්ට් එක හිස් කරයි
    st.session_state.last_reset_date = date.today()

if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total":
        return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 4. CSS FOR PROFESSIONAL UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metric Cards Styling */
    .metric-container { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; justify-content: center; }
    .m-card {
        padding: 10px 15px; border-radius: 8px; text-align: center; min-width: 120px;
        color: white; font-weight: bold; font-size: 14px; box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .bg-pending { background: #28a745; }
    .bg-confirm { background: #fd7e14; }
    .bg-noanswer { background: #dc3545; }
    .bg-cancel { background: #6f42c1; }
    .bg-fake { background: #343a40; }
    .bg-total { background: #007bff; }
    .val { font-size: 20px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTHENTICATION ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#ffa500;'>Happy Shop</h1>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"; st.rerun()
            else: st.error("Invalid Login")
else:
    # --- 6. SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#ffa500;'>HAPPY SHOP</h2>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "📊 Stocks"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Actions", ["New Order", "View Lead", "Add Lead", "Order History"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Actions", ["View Stocks", "Stock Adjustment"])
        
        if st.button("Logout"): st.session_state.user = None; st.rerun()

    # --- 7. DYNAMIC METRIC CARDS (Dashboard & View Lead Only) ---
    if menu == "🏠 Dashboard" or (menu == "🧾 Orders" and sub_menu == "View Lead"):
        st.markdown(f"""
            <div class="metric-container">
                <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
                <div class="m-card bg-confirm">OK (CONFIRMED)<span class="val">{get_count('confirm')}</span></div>
                <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
                <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
                <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
                <div class="m-card bg-total">TOTAL LEADS<span class="val">{get_count('total')}</span></div>
            </div>
        """, unsafe_allow_html=True)

    # --- 8. PAGE CONTENT ---
    if menu == "🏠 Dashboard":
        st.title("Business Summary")
        st.write(f"Today's Date: {date.today()}")
        # Dashboard එකේ පෙන්නන්න ඕන දේවල් මෙතනට

    elif menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
        st.subheader("Add New Lead / Order")
        with st.form("pro_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer Name *")
            phone = c1.text_input("Phone Number *")
            addr = c1.text_area("Address")
            dist = c2.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            city = c2.text_input("City")
            amt = c2.number_input("Total Amount", min_value=0.0)
            if st.form_submit_button("SAVE LEAD"):
                if name and phone:
                    new_id = len(st.session_state.orders) + 1
                    st.session_state.orders.append({
                        "id": new_id, "order_id": f"HS-{1000+new_id}", 
                        "customer": name, "phone": phone, "status": "pending", "date": str(date.today())
                    })
                    st.success("Lead Saved Successfully!")
                    st.rerun()

    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.subheader("Interactive Leads Table")
        
        # HTML Table Generator
        rows_html = ""
        for order in st.session_state.orders:
            rows_html += f"""
            <tr class="status-{order['status']}" id="row{order['id']}">
              <td>{order['order_id']}</td><td>{order['customer']}</td><td>{order['phone']}</td>
              <td><span class="badge {order['status']}" id="status{order['id']}">{order['status'].upper()}</span></td>
              <td class="actions">
                <button class="btn-confirm" onclick="updateStatus({order['id']}, 'confirm')">✔</button>
                <button class="btn-noanswer" onclick="updateStatus({order['id']}, 'noanswer')">☎</button>
                <button class="btn-cancel" onclick="updateStatus({order['id']}, 'cancel')">✖</button>
                <button class="btn-fake" onclick="updateStatus({order['id']}, 'fake')">⚠</button>
              </td>
            </tr>"""

        # Web Component for Table & JS
        # සටහන: මෙහි JavaScript එකේ updateStatus එබූ විට counts refresh වීමට Streamlit එකට query param එකක් යවනවා.
        html_code = f"""
        <html><head><style>
            table {{ width:100%; border-collapse:collapse; background:#161b22; color:white; font-family:sans-serif; }}
            th, td {{ padding:12px; border:1px solid #30363d; text-align:left; }}
            th {{ background:#21262d; color:#ffa500; font-size:12px; }}
            .badge {{ padding:4px 8px; border-radius:12px; font-size:10px; background:#444; }}
            .confirm {{ background:#fd7e14; }} .noanswer {{ background:#dc3545; }} .cancel {{ background:#6f42c1; }} .fake {{ background:#343a40; }}
            .actions button {{ border:none; padding:6px 10px; border-radius:4px; cursor:pointer; color:white; font-weight:bold; margin-right:3px; }}
            .btn-confirm {{ background:#fd7e14; }} .btn-noanswer {{ background:#dc3545; }} .btn-cancel {{ background:#6f42c1; }} .btn-fake {{ background:#343a40; }}
        </style></head>
        <body>
            <table><thead><tr><th>Order ID</th><th>Customer</th><th>Phone</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>{rows_html}</tbody></table>
            <script>
                function updateStatus(id, newStatus) {{
                    // මෙය ක්ලික් කළ විට UI එකේ පාට මාරු වේ
                    document.getElementById("status"+id).className = "badge " + newStatus;
                    document.getElementById("status"+id).innerText = newStatus.toUpperCase();
                    
                    // මෙය Python පැත්තට දත්ත යැවීමට භාවිතා කළ හැක (මෙහිදී සරලව refresh කිරීමට window.parent භාවිතා කරයි)
                    // සම්පූර්ණ දත්ත Update වීමට නම් python එකේ 'st_callback' අවශ්‍ය වේ.
                    // දැනට අපි කරන්නේ ක්ලික් කළ පසු session එකේ update එක python side එකෙන් handle කිරීමයි.
                    window.parent.postMessage({{type: 'streamlit:set_status', id: id, status: newStatus}}, '*');
                }}
            </script>
        </body></html>"""
        
        components.html(html_code, height=400, scrolling=True)
        
        # Python side status update logic
        # සටහන: උඹට Table එකේ Status එක එබූ සැනින් Python වල update වෙන්න ඕනෙ නම් 
        # මෙතන query parameter එකක් පාවිච්චි කරන්න පුළුවන්. දැනට මම මේක සරලව තියලා තියෙන්නේ.

    else:
        st.info(f"{menu} > {sub_menu} අංශය දැනට සකස් වෙමින් පවතී.")
