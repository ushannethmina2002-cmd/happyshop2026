import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Professional ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOADERS (Districts & Cities) ---
districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]
cities = ["Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya", "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya", "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"]

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = [{"id": 1, "order_id": "821384", "customer": "Sharanga Malaka", "phone": "0702710550", "status": "pending"}]

# --- 4. ADVANCED CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .sidebar-title { 
        color: #ffa500; font-size: 28px; font-weight: 800; text-align: center; 
        padding: 20px 0; border-bottom: 1px solid #30363d; margin-bottom: 20px;
        letter-spacing: 1px;
    }
    
    /* Metrics / Status Cards */
    .status-card-container { display: flex; gap: 15px; margin-bottom: 30px; }
    .status-card {
        flex: 1; padding: 20px; border-radius: 12px; text-align: center;
        font-weight: 700; font-size: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .status-card:hover { transform: translateY(-5px); }
    .bg-pending { background: linear-gradient(135deg, #28a745, #1e7e34); color: white; }
    .bg-ok { background: linear-gradient(135deg, #fd7e14, #d96101); color: white; }
    .bg-no-answer { background: linear-gradient(135deg, #dc3545, #a71d2a); color: white; }
    
    /* Form & Input Styling */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #0d1117 !important; border: 1px solid #30363d !important;
        border-radius: 8px !important; color: white !important;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 600; 
        background-color: #ffa500; color: #000; border: none;
        padding: 10px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffc107; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTHENTICATION ---
if st.session_state.user is None:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        st.markdown("<div style='text-align:center; padding: 50px 0;'><h1 style='color:#ffa500;'>Happy Shop</h1><p>Management Portal Login</p></div>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="admin@happyshop.com")
        p = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("SIGN IN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"; st.rerun()
            else: st.error("Access Denied: Invalid Credentials")
else:
    # --- 6. SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>HAPPY SHOP</div>", unsafe_allow_html=True)
        
        menu = st.selectbox("NAVIGATE", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sub-menus based on main menu
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Order Search", "Import Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills", "Courier Feedback Summary"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])
        else:
            sub_menu = "General"

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Log Out"): st.session_state.user = None; st.rerun()

    # --- 7. TOP STATUS TILES ---
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-pending">PENDING<br><span style='font-size:24px;'>{len(st.session_state.orders)}</span></div>
            <div class="status-card bg-ok">OK (CONFIRMED)<br><span style='font-size:24px;'>0</span></div>
            <div class="status-card bg-no-answer">NO ANSWER<br><span style='font-size:24px;'>0</span></div>
        </div>
    """, unsafe_allow_html=True)

    # --- 8. PAGE CONTENT ---
    if menu == "🏠 Dashboard":
        st.title("Business Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Daily Sales", "LKR 0.00", "+0%")
        c2.metric("Total Leads", len(st.session_state.orders))
        c3.metric("Stock Value", "LKR 145,000", "-5%")

    elif menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
        st.markdown(f"## 📝 {sub_menu}")
        with st.expander("Customer & Order Entry Form", expanded=True):
            with st.form("pro_order_form"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("👤 **Customer Details**")
                    c_name = st.text_input("Full Name *")
                    c_address = st.text_area("Delivery Address *")
                    c_dist = st.selectbox("District *", sorted(districts))
                    c_city = st.selectbox("City *", sorted(cities))
                    c_p1 = st.text_input("Primary Contact *")
                    c_source = st.selectbox("Order Source", ["WhatsApp", "Facebook", "TikTok", "Website"])
                with col2:
                    st.write("📦 **Order Details**")
                    p_item = st.selectbox("Product Selection", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1 [VGLS0001]", "Kalkaya [VGLS0003]"])
                    p_qty = st.number_input("Quantity", min_value=1, value=1)
                    p_price = st.number_input("Unit Price", min_value=0.0)
                    s_charge = st.number_input("Delivery Charge", min_value=0.0)
                    p_disc = st.number_input("Discount", min_value=0.0)
                    st.info(f"Final Amount: LKR {(p_price * p_qty) + s_charge - p_disc:,.2f}")
                
                if st.form_submit_button("SUBMIT ORDER TO SYSTEM"):
                    if c_name and c_p1:
                        new_id = len(st.session_state.orders) + 1
                        st.session_state.orders.append({"id": new_id, "order_id": f"HS-{821384+new_id}", "customer": c_name, "phone": c_p1, "status": "pending"})
                        st.success(f"SUCCESS: Order {new_id} recorded.")
                        st.rerun()
                    else: st.warning("Please fill required fields.")

    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.markdown("## 📋 Leads Management Table")
        
        rows_html = ""
        for order in st.session_state.orders:
            rows_html += f"""
            <tr class="status-{order['status']}" id="row{order['id']}">
              <td><b>{order['order_id']}</b></td><td>{order['customer']}</td><td>{order['phone']}</td>
              <td><span class="badge {order['status']}" id="status{order['id']}">{order['status'].upper()}</span></td>
              <td class="actions">
                <button class="btn-confirm" onclick="setStatus({order['id']},'confirm')">✔</button>
                <button class="btn-hold" onclick="setStatus({order['id']},'hold')">⏸</button>
                <button class="btn-noanswer" onclick="setStatus({order['id']},'noanswer')">☎</button>
                <button class="btn-cancel" onclick="setStatus({order['id']},'cancel')">✖</button>
              </td>
            </tr>"""

        html_table = f"""
        <html><head><style>
            table{{ width:100%; border-collapse:collapse; background:#161b22; color:#e1e1e1; font-family: sans-serif; border-radius:10px; overflow:hidden; }}
            th, td{{ padding:15px; border-bottom:1px solid #30363d; text-align:left; }}
            th{{ background:#21262d; color:#ffa500; text-transform:uppercase; font-size:12px; }}
            .status-confirm{{ background: rgba(40, 167, 69, 0.1); }}
            .status-noanswer{{ background: rgba(220, 53, 69, 0.1); }}
            .badge{{ padding:5px 10px; border-radius:20px; font-size:10px; font-weight:bold; color:white; background:#6e7681; }}
            .confirm{{ background:#28a745; }} .noanswer{{ background:#dc3545; }} .hold{{ background:#fd7e14; }}
            .actions button{{ border:none; padding:8px 12px; border-radius:6px; cursor:pointer; margin-right:5px; transition: 0.2s; font-weight:bold; }}
            .btn-confirm{{ background:#28a745; color:white; }} .btn-hold{{ background:#fd7e14; color:white; }} .btn-noanswer{{ background:#dc3545; color:white; }} .btn-cancel{{ background:#6e7681; color:white; }}
            .actions button:hover{{ opacity: 0.8; transform: scale(1.1); }}
        </style></head>
        <body><table><thead><tr><th>Order ID</th><th>Customer Name</th><th>Phone Number</th><th>Status</th><th>Quick Actions</th></tr></thead>
        <tbody>{rows_html}</tbody></table>
        <script>
            function setStatus(id, status){{
                const row = document.getElementById("row"+id);
                const badge = document.getElementById("status"+id);
                badge.className = "badge " + status;
                badge.innerText = status.toUpperCase();
                if(status === 'confirm') row.style.background = "rgba(40, 167, 69, 0.15)";
                if(status === 'noanswer') row.style.background = "rgba(220, 53, 69, 0.15)";
            }}
        </script></body></html>"""
        components.html(html_table, height=600, scrolling=True)

    else:
        st.subheader(f"{menu} > {sub_menu}")
        st.info("Module content is being optimized for the new professional layout.")
