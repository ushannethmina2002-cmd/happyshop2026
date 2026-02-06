import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS FOR PROFESSIONAL UI (Dark Mode & Status Colors) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Header Status Cards */
    .status-card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-card {
        padding: 12px 25px; border-radius: 8px; font-weight: bold; color: black; 
        display: flex; align-items: center; justify-content: center; min-width: 140px;
    }
    .bg-pending { background-color: #2ecc71; }   /* Green */
    .bg-ok { background-color: #f39c12; }        /* Orange */
    .bg-no-answer { background-color: #e74c3c; }  /* Red */
    .bg-hold { background-color: #9b59b6; }      /* Purple */
    .bg-cancel { background-color: #95a5a6; }    /* Gray */
    
    .form-container { background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT (Fixes KeyErrors) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    # Initial Sample Order
    st.session_state.orders = [
        {"ID": "HS-1001", "Date": "2026-02-06", "Customer": "Sharanga Malaka", "Phone": "0702710550", 
         "Address": "69/3 Ragama Road, Kadawatha", "Status": "Pending", "Amount": 2950.0, "Product": "Hair Oil"}
    ]
if 'stocks' not in st.session_state:
    st.session_state.stocks = [
        {"Product": "Hair Oil", "Code": "VGLS0005", "Price": 2950.0, "Available": 272, "Packed": 0},
        {"Product": "Crown 1", "Code": "VGLS0001", "Price": 2400.0, "Available": 50, "Packed": 0},
        {"Product": "Kalkaya", "Code": "VGLS0003", "Price": 2800.0, "Available": 624, "Packed": 0}
    ]

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><div class='form-container'><h2 style='text-align:center;'>Happy Shop ERP</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Invalid Credentials!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#e67e22;'>Sandun</h2>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Order Search", "Import Lead", "Order History", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Search Waybills"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. TOP STATUS BAR (Dynamic Count for Header) ---
    def get_count(status): return len([o for o in st.session_state.orders if o['Status'] == status])
    
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-pending">Pending | {get_count('Pending')}</div>
            <div class="status-card bg-ok">Ok | {get_count('Ok')}</div>
            <div class="status-card bg-no-answer">No Answer | {get_count('No Answer')}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 7. CONTENT SECTIONS ---

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.subheader("Welcome to Dashboard")
        m1, m2, m3 = st.columns(3)
        # Using safely to avoid KeyError
        total_rev = sum(float(o.get('Amount', 0)) for o in st.session_state.orders)
        m1.metric("Total Revenue", f"LKR {total_rev:,.2f}")
        m2.metric("Total Orders", len(st.session_state.orders))
        m3.metric("Stock Value", "Calculating...")
        
        st.markdown("### Recent Leads Activity")
        st.dataframe(pd.DataFrame(st.session_state.orders).tail(10), use_container_width=True)

    # NEW ORDER ENTRY
    elif menu == "🧾 Orders" and sub_menu == "New Order":
        st.subheader("Create New Order")
        with st.form("new_order_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                addr = st.text_area("Address *")
                ph1 = st.text_input("Contact Number One *")
                dist = st.selectbox("Select District", ["Colombo", "Kandy", "Gampaha", "Kadawatha", "Other"])
            with c2:
                prod = st.selectbox("Product", [s['Product'] for s in st.session_state.stocks])
                qty = st.number_input("Qty", min_value=1, value=1)
                amt = st.number_input("Sale Amount", min_value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
            
            if st.form_submit_button("SAVE ORDER"):
                if name and ph1:
                    new_entry = {
                        "ID": f"HS-{1000 + len(st.session_state.orders) + 1}",
                        "Date": str(datetime.now().date()), "Customer": name, "Phone": ph1,
                        "Address": addr, "Status": "Pending", "Amount": amt, "Product": prod
                    }
                    st.session_state.orders.append(new_entry)
                    st.success("Order Added Successfully!")
                    st.rerun()
                else: st.error("Required fields are missing!")

    # VIEW LEAD (With Status Update & Action as per your photo)
    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.subheader("View & Manage Leads")
        
        # Displaying the Leads Table
        df_view = pd.DataFrame(st.session_state.orders)
        st.dataframe(df_view, use_container_width=True)
        
        st.markdown("---")
        # Action Section (To update Status like Confirmation/No Answer/Cancel)
        st.markdown("#### ⚡ Lead Action Control")
        col_id, col_stat, col_btn = st.columns([2, 2, 1])
        
        with col_id:
            target_id = st.selectbox("Select Lead ID to update", df_view['ID'])
        with col_stat:
            target_status = st.selectbox("Change Status To", ["Pending", "Ok", "No Answer", "Hold", "Canceled"])
        with col_btn:
            st.write(" ") # Padding
            if st.button("UPDATE NOW"):
                for order in st.session_state.orders:
                    if order['ID'] == target_id:
                        order['Status'] = target_status
                        st.success(f"ID {target_id} updated to {target_status}!")
                        st.rerun()

    # STOCKS VIEW
    elif menu == "📊 Stocks":
        st.subheader(f"Stocks > {sub_menu}")
        if sub_menu == "View Stocks":
            st.table(pd.DataFrame(st.session_state.stocks))
        else:
            st.info(f"Management for {sub_menu} is active. No waste recorded yet.")

    # RETURN SECTION
    elif menu == "↩️ Return":
        st.subheader(f"Returns > {sub_menu}")
        st.write("Current Return List (Empty)")
        st.dataframe(pd.DataFrame(columns=["Order ID", "Reason", "Return Date"]), use_container_width=True)

    # PRODUCTS
    elif menu == "🏷️ Products":
        st.subheader("Product Inventory Settings")
        st.info("Add or Edit items available for sale.")
        with st.expander("Add New Product"):
            st.text_input("Product Name")
            st.text_input("Product Code")
            st.button("Register Product")
