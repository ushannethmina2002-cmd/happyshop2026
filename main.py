import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Happy Shop Official ERP",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS (පින්තූරවල තිබුණු Layout එක සැකසීම) ---
st.markdown("""
    <style>
    /* මුළු පසුබිම සහ අකුරු */
    .stApp { background-color: #f0f2f5; color: #1c1e21; }
    
    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: #111111 !important;
        border-bottom: 3px solid #e67e22;
    }
    header[data-testid="stHeader"] button svg { fill: white !important; }

    /* Sidebar (Dark Menu) */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #222;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .sidebar-brand {
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #e67e22 !important;
        border-bottom: 1px solid #333;
        margin-bottom: 15px;
    }

    /* Professional Boxes (Cards) */
    .section-box {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
        margin-bottom: 20px;
    }
    
    /* Metrics / KPI Cards */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e67e22;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Buttons */
    .stButton>button {
        background-color: #e67e22 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
        width: 100%;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    # පින්තූරයේ තිබුණු විදිහට sample ඩේටා කිහිපයක්
    st.session_state.orders = [
        {"Order ID": "HS-101", "Date": "2026-02-06", "Name": "Wasantha Bandara", "City": "Matale", "Phone": "0773411920", "Product": "Kesharaia Hair Oil", "Status": "Pending", "Amount": 2500.0}
    ]

# --- 4. LOGIN ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='section-box'><h2 style='text-align:center;'>Happy Shop ERP</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Invalid Details")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR (Dark Sidebar with Menu Options) ---
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>Happy Shop</div>", unsafe_allow_html=True)
        
        main_choice = st.radio("MAIN NAVIGATION", [
            "🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks"
        ])

        if "Orders" in main_choice:
            st.markdown("---")
            sub_choice = st.selectbox("ORDER ACTIONS", [
                "New Order", "Pending Orders", "Order Search", 
                "Import Lead", "Order History", "Blacklist Manager"
            ])
        else:
            sub_choice = "Default"

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. MAIN INTERFACE ---
    
    # DASHBOARD (පින්තූරවල තිබුණු Metrics පෙනුම)
    if main_choice == "🏠 Dashboard":
        st.subheader("System Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown("<div class='metric-card'><h4>Total Orders</h4><h2>124</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown("<div class='metric-card'><h4>Shipped</h4><h2>85</h2></div>", unsafe_allow_html=True)
        with c3: st.markdown("<div class='metric-card'><h4>Returns</h4><h2>5</h2></div>", unsafe_allow_html=True)
        with c4: st.markdown("<div class='metric-card'><h4>Revenue</h4><h2>LKR 250k</h2></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-box'><h4>Recent Activities</h4>", unsafe_allow_html=True)
        st.write("අද දින සිදුකළ සියලුම ගනුදෙනු මෙහි දිස්වේ.")
        st.table(pd.DataFrame(st.session_state.orders).head())
        st.markdown("</div>", unsafe_allow_html=True)

    # NEW ORDER FORM (පින්තූරයේ තිබුණු විදිහට)
    elif main_choice == "🧾 Orders" and sub_choice == "New Order":
        st.subheader("📝 New Order Entry")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            cust_name = st.text_input("Customer Name *")
            cust_phone = st.text_input("Phone Number *")
            cust_address = st.text_area("Address")
        with col2:
            district = st.selectbox("District", ["Colombo", "Kandy", "Matale", "Galle", "Other"])
            product = st.selectbox("Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            amount = st.number_input("Amount (LKR)", min_value=0.0)
            
        if st.button("🚀 SAVE ORDER"):
            if cust_name and cust_phone:
                new_id = f"HS-{100 + len(st.session_state.orders) + 1}"
                st.session_state.orders.append({
                    "Order ID": new_id, "Date": str(datetime.now().date()), 
                    "Name": cust_name, "City": district, "Phone": cust_phone, 
                    "Product": product, "Status": "Pending", "Amount": amount
                })
                st.success(f"Order {new_id} saved successfully!")
            else: st.warning("Please fill required fields.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ORDER SEARCH (පින්තූරයේ තිබුණු filter Layout එක)
    elif main_choice == "🧾 Orders" and sub_choice == "Order Search":
        st.subheader("🔍 Search Orders / Leads")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: st.text_input("Search by Name")
        with f2: st.text_input("Search by Phone")
        with f3: st.date_input("Select Date")
        st.button("FILTER RESULTS")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)
            st.dataframe(df, use_container_width=True)
        else: st.info("No data available.")

    # අනෙකුත් අංශ
    else:
        st.subheader(f"{main_choice}")
        st.info(f"{main_choice} අංශය දැනට සැකසෙමින් පවතී.")
