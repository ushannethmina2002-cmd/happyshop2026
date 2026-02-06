import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Happy Shop ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS FOR PROFESSIONAL UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; color: #1c1e21; }
    header[data-testid="stHeader"] { background-color: #111 !important; border-bottom: 3px solid #e67e22; }
    [data-testid="stSidebar"] { background-color: #0f0f0f !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* පින්තූරවල තිබුණු වගේ ලස්සන White Cards */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    .sidebar-title { font-size: 24px; font-weight: bold; color: #e67e22; text-align: center; padding: 20px; border-bottom: 1px solid #333; }
    .stButton>button { background-color: #e67e22 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 8px; }
    
    /* Table Styling */
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state: st.session_state.orders = []

# --- 4. LOGIN ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='info-card'><h2 style='text-align:center;'>Happy Shop Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR ---
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>Happy Shop</div>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped", "📊 Stocks"])
        
        if menu == "🧾 Orders":
            sub_menu = st.radio("ACTIONS", ["New Order", "Order Search", "Pending Orders", "Order History", "Blacklist"])
        else: sub_menu = "Default"
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. CONTENT ---
    if menu == "🧾 Orders" and sub_menu == "New Order":
        st.subheader("📝 New Order Registration")
        
        with st.container():
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("##### 👤 Customer Info")
                name = st.text_input("Full Name")
                phone = st.text_input("Phone Number 1")
                phone2 = st.text_input("Phone Number 2 (Optional)")
                address = st.text_area("Full Address")
                district = st.selectbox("District", ["Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Galle", "Matara", "Hambantota", "Jaffna", "Kurunegala", "Anuradhapura", "Ratnapura", "Badulla", "Other"])
            
            with col2:
                st.markdown("##### 📦 Product Details")
                item = st.selectbox("Select Item", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go", "Combo Pack"])
                qty = st.number_input("Quantity", min_value=1, value=1)
                courier = st.selectbox("Courier Service", ["Koombiyo", "Domex", "Pronto", "Flash"])
                tracking = st.text_input("Tracking ID (If available)")
            
            with col3:
                st.markdown("##### 💰 Payment & Status")
                pay_method = st.selectbox("Payment Method", ["Cash on Delivery (COD)", "Bank Transfer", "Paid"])
                total_amt = st.number_input("Final Amount (LKR)", min_value=0.0)
                order_date = st.date_input("Order Date", datetime.now())
                note = st.text_input("Special Notes")
                
            if st.button("🚀 SUBMIT ORDER TO SYSTEM"):
                if name and phone:
                    order_id = f"HS-{1000 + len(st.session_state.orders)}"
                    st.session_state.orders.append({
                        "ID": order_id, "Date": str(order_date), "Name": name, "Phone": phone, 
                        "District": district, "Item": item, "Qty": qty, "Amount": total_amt, 
                        "Courier": courier, "Status": "Pending"
                    })
                    st.success(f"Order {order_id} Saved!")
                else: st.warning("නම සහ දුරකථනය අනිවාර්යයි!")
            st.markdown("</div>", unsafe_allow_html=True)

    elif sub_menu == "Order Search":
        st.subheader("🔍 Order Management & Search")
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        s1.text_input("Search Name")
        s2.text_input("Search Phone")
        s3.selectbox("Filter Status", ["All", "Pending", "Shipped", "Delivered", "Return"])
        s4.date_input("Filter Date")
        st.button("SEARCH")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)
            st.dataframe(df, use_container_width=True)
        else: st.info("දත්ත කිසිවක් නැත.")

    elif menu == "🏠 Dashboard":
        st.subheader("Business Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sales", f"LKR {sum(d['Amount'] for d in st.session_state.orders):,.2f}")
        m2.metric("Orders", len(st.session_state.orders))
        m3.metric("Returns", "0")
        m4.metric("Pending", len([d for d in st.session_state.orders if d['Status'] == 'Pending']))
