import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop Official ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOADERS (Districts & Cities) ---
districts = [
    "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", 
    "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", 
    "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", 
    "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"
]

# Sample Cities (You can expand this list)
cities = [
    "Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya",
    "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya",
    "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"
]

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"id": 1, "order_id": "821384", "customer": "Sharanga Malaka", "phone": "0702710550", "status": "pending"}
    ]

# --- 4. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    .sidebar-title { color: #e67e22; font-size: 26px; font-weight: bold; text-align: center; }
    .status-card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-card { padding: 12px 20px; border-radius: 8px; font-weight: bold; color: black; min-width: 140px; text-align: center;}
    .bg-green { background-color: #2ecc71; }
    .bg-orange { background-color: #f39c12; }
    .bg-red { background-color: #e74c3c; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTHENTICATION ---
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><h2 style='text-align:center;'>Happy Shop Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"; st.rerun()
            else: st.error("Invalid Credentials!")
else:
    # --- 6. SIDEBAR (Updated as per your photo) ---
    with st.sidebar:
        st.markdown(f"<div class='sidebar-title'>Happy Shop</div>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills", "Courier Feedback Summary"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])

        st.markdown("---")
        if st.button("🚪 Logout"): st.session_state.user = None; st.rerun()

    # --- TOP STATUS BAR ---
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-green">Pending | {len(st.session_state.orders)}</div>
            <div class="status-card bg-orange">Ok | 0</div>
            <div class="status-card bg-red">No Answer | 0</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 7. ORDER FORM LOGIC (As per Photo 2 & 11) ---
    if menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
        st.subheader(f"Orders > {sub_menu}")
        
        with st.form("order_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Customer Information**")
                c_name = st.text_input("Customer Name *")
                c_address = st.text_area("Address *")
                c_district = st.selectbox("Select District *", sorted(districts))
                c_city = st.selectbox("Select City *", sorted(cities)) # Searchable dropdown
                c_phone1 = st.text_input("Contact Number One *")
                c_phone2 = st.text_input("Contact Number Two")
                c_email = st.text_input("Email")
                c_date = st.date_input("Order Date", datetime.now())
                c_source = st.selectbox("Select Order Source", ["Facebook", "WhatsApp", "TikTok", "Google", "Instagram"])
                c_method = st.selectbox("Payment Method", ["COD", "Bank Transfer", "Card Payment"])

            with col2:
                st.markdown("**Product & Shipping**")
                p_item = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1 [VGLS0001]", "Kalkaya [VGLS0003]"])
                p_qty = st.number_input("Qty", min_value=1, value=1)
                p_amount = st.number_input("Sale Amount", min_value=0.0, format="%.2f")
                p_note = st.text_area("Product Note")
                p_discount = st.number_input("Product Discount", min_value=0.0)
                
                st.divider()
                s_courier = st.selectbox("Courier Company", ["Any", "Koombiyo", "Domex", "Pronto", "Fardar"])
                s_ref = st.text_input("Reference No")
                s_weight = st.number_input("Pkg Weight (kgs)", min_value=0.0, value=0.0)
                s_charge = st.number_input("Delivery Charge", min_value=0.0, value=0.0)
                
                total_amt = (p_amount * p_qty) + s_charge - p_discount
                st.markdown(f"### Total Amount: LKR {total_amt:,.2f}")

            submit = st.form_submit_button("🚀 SAVE ORDER / LEAD")
            
            if submit:
                if c_name and c_phone1 and c_address:
                    new_id = len(st.session_state.orders) + 1
                    st.session_state.orders.append({
                        "id": new_id, "order_id": f"HS-{821384+new_id}", 
                        "customer": c_name, "phone": c_phone1, "status": "pending",
                        "district": c_district, "city": c_city, "amount": total_amt
                    })
                    st.success(f"Order for {c_name} saved successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields (*)!")

    # --- 8. VIEW LEAD (Interactive HTML Table) ---
    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.subheader("Orders / Leads List")
        
        rows_html = ""
        for order in st.session_state.orders:
            rows_html += f"""
            <tr class="status-{order['status']}" id="row{order['id']}">
              <td>{order['order_id']}</td><td>{order['customer']}</td><td>{order['phone']}</td>
              <td><span class="badge {order['status']}" id="status{order['id']}">{order['status'].upper()}</span></td>
              <td class="actions">
                <button class="btn-confirm" onclick="setStatus({order['id']},'confirm')">✔</button>
                <button class="btn-hold" onclick="setStatus({order['id']},'hold')">⏸</button>
                <button class="btn-noanswer" onclick="setStatus({order['id']},'noanswer')">☎✖</button>
                <button class="btn-cancel" onclick="setStatus({order['id']},'cancel')">✖</button>
                <button class="btn-fake" onclick="setStatus({order['id']},'fake')">⚠</button>
              </td>
            </tr>"""

        html_code = f"""
        <html><head><style>
            table{{ width:100%; border-collapse:collapse; font-family: sans-serif; background:#fff; }}
            th, td{{ padding:10px; border:1px solid #ddd; text-align:left; font-size:13px; color:#333; }}
            th{{ background:#222; color:#fff; }}
            .status-confirm{{ background:#d4edda; }} .status-hold{{ background:#fff3cd; }}
            .status-noanswer{{ background:#f8d7da; }} .status-cancel{{ background:#f5c6cb; }}
            .actions button{{ border:none; padding:5px 10px; cursor:pointer; border-radius:4px; margin:2px; color:#fff; font-weight:bold; }}
            .btn-confirm{{ background:#28a745; }} .btn-hold{{ background:#ffc107; color:#000; }}
            .btn-noanswer{{ background:#dc3545; }} .btn-cancel{{ background:#bd2130; }} .btn-fake{{ background:#6c757d; }}
            .badge{{ padding:4px 8px; border-radius:4px; font-size:11px; color:#fff; background:#6c757d; }}
        </style></head>
        <body><table><thead><tr><th>ID</th><th>Customer</th><th>Phone</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>{rows_html}</tbody></table>
        <script>
            function setStatus(id, status){{
                document.getElementById("row"+id).className = "status-" + status;
                const b = document.getElementById("status"+id);
                b.innerText = status.toUpperCase();
                b.style.background = (status==='confirm')?'#28a745':(status==='noanswer')?'#dc3545':'#ffc107';
            }}
        </script></body></html>"""
        components.html(html_code, height=500, scrolling=True)

    else:
        st.subheader(f"{menu} > {sub_menu}")
        st.write("Ready for Data Entry...")
