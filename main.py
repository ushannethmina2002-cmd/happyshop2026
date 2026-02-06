import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP (ස්ථිර sidebar එක සමඟ) ---
st.set_page_config(
    page_title="Happy Shop Official ERP",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS FOR PROFESSIONAL DARK UI (පින්තූරවල තිබූ layout එක) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    header[data-testid="stHeader"] { background-color: #000000 !important; border-bottom: 2px solid #e67e22; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Status Boxes Styling (පින්තූරයේ තිබූ පාට පෙට්ටි) */
    .status-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .status-item {
        padding: 8px 15px; border-radius: 5px; font-weight: bold; font-size: 14px; color: #000;
    }
    .bg-green { background-color: #2ecc71; }
    .bg-orange { background-color: #f39c12; }
    .bg-red { background-color: #e74c3c; }
    .bg-gray { background-color: #95a5a6; }
    .bg-blue { background-color: #3498db; }

    /* Forms & Tables */
    .form-box { background-color: #1a1c23; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    .stButton>button { background-color: #e67e22 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 5px; height: 45px; }
    
    .sidebar-brand { font-size: 24px; font-weight: bold; color: #e67e22; text-align: center; padding: 10px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (Data Handling & Bug Fix) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders_data' not in st.session_state:
    # පින්තූරවල තිබූ අනුපිළිවෙලට sample data
    st.session_state.orders_data = [
        {"ID": "HS-1001", "Date": "2026-02-06", "Customer": "Wasantha Bandara", "Phone": "0773411920", "District": "Matale", "Item": "Hair Oil", "Qty": 1, "Amount": 2950.0, "Status": "Pending"}
    ]

# --- 4. LOGIN SYSTEM ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        st.markdown("<div class='form-box'><h2 style='text-align:center;'>Happy Shop Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Login Details Incorrect!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR (පින්තූරවල තිබූ සියලුම Options ඇතුළත් කර ඇත) ---
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>Happy Shop</div>", unsafe_allow_html=True)
        
        main_nav = st.selectbox("MAIN NAVIGATION", [
            "🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"
        ])
        
        sub_nav = "Default"
        if main_nav == "🧾 Orders":
            sub_nav = st.radio("Order Options", [
                "New Order", "Pending Orders", "Order Search", "Import Lead", 
                "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"
            ])
        elif main_nav == "🚚 Shipped Items":
            sub_nav = st.radio("Shipped Options", [
                "Ship", "Shipped List", "Shipped Summary", "Delivery Summary", 
                "Courier Feedback", "Confirm Dispatch", "Search Waybills"
            ])
        elif main_nav == "📊 Stocks":
            sub_nav = st.radio("Stock Options", ["View Stocks", "Stock Adjustment", "Add Waste", "Stock Values"])
        elif main_nav == "📦 GRN":
            sub_nav = st.radio("GRN Options", ["New GRN", "GRN List", "Reorder List", "New PO", "Packing"])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. MAIN CONTENT ---

    # --- STATUS BAR (පින්තූරවල තිබූ පාට පෙට්ටි ටික - සෑම ප්‍රධාන පිටුවකම පෙන්වයි) ---
    st.markdown(f"## {main_nav} > {sub_nav}")
    st.markdown("""
        <div class='status-container'>
            <div class='status-item bg-green'>Pending | 1</div>
            <div class='status-item bg-orange'>Ok | 0</div>
            <div class='status-item bg-red'>No Answer | 0</div>
            <div class='status-item bg-gray'>Rejected | 0</div>
            <div class='status-item bg-blue'>Fake | 0</div>
        </div>
    """, unsafe_allow_html=True)

    # NEW ORDER ENTRY
    if main_nav == "🧾 Orders" and sub_nav == "New Order":
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Contact Number One *")
            address = st.text_area("Full Address *")
            district = st.selectbox("District", ["Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Galle", "Other"])
        with c2:
            item = st.selectbox("Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            qty = st.number_input("Qty", min_value=1, value=1)
            amt = st.number_input("Sale Amount", min_value=0.0)
            courier = st.selectbox("Courier Company", ["Koombiyo Delivery", "Domex", "Pronto", "Flash"])
            pay_type = st.selectbox("Payment Type", ["COD", "Bank Transfer"])
            
        if st.button("🚀 SUBMIT ORDER"):
            if name and phone:
                st.session_state.orders_data.append({
                    "ID": f"HS-{1000 + len(st.session_state.orders_data) + 1}",
                    "Date": str(datetime.now().date()), "Customer": name, "Phone": phone,
                    "District": district, "Item": item, "Qty": qty, "Amount": amt, "Status": "Pending"
                })
                st.success("Order Saved Successfully!")
            else: st.warning("Please fill the required fields.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ORDER SEARCH / VIEW LEAD
    elif main_nav == "🧾 Orders" and (sub_nav == "Order Search" or sub_nav == "View Lead"):
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        f1.text_input("Search Name")
        f2.text_input("Search Phone")
        f3.date_input("Filter Date")
        st.button("🔍 Search")
        st.markdown("</div>", unsafe_allow_html=True)
        
        df = pd.DataFrame(st.session_state.orders_data)
        st.dataframe(df, use_container_width=True)

    # STOCKS VIEW
    elif main_nav == "📊 Stocks" and sub_nav == "View Stocks":
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        stock_data = [
            {"Product": "Kesharaia Hair Oil", "Code": "VGLS0005", "Price": 2950.00, "Available Qty": 272},
            {"Product": "Herbal Crown", "Code": "VGLS0001", "Price": 2400.00, "Available Qty": 50}
        ]
        st.table(pd.DataFrame(stock_data))
        st.markdown("</div>", unsafe_allow_html=True)

    # DASHBOARD (Bug Fix: KeyError වැලැක්වීමට)
    elif main_nav == "🏠 Dashboard":
        total_sales = sum(float(d['Amount']) for d in st.session_state.orders_data)
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Revenue", f"LKR {total_sales:,.2f}")
        k2.metric("Total Orders", len(st.session_state.orders_data))
        k3.metric("Shipped Orders", "0")
        
        st.markdown("<div class='form-box'>Recent Transactions</div>", unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.orders_data).tail())

    else:
        st.info(f"{main_nav} > {sub_nav} අංශය දැනට සැකසෙමින් පවතී.")
