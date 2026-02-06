import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් එකේ සැකසුම් (මෙනු එක සහ ලේඅවුට් එක) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" # මෙනු එක හැමවෙලේම පේන්න තැබීම
)

# --- 2. සයිට් එකේ පෙනුම (CSS) - Screenshot එකේ පෙනුම ලබා ගැනීමට ---
st.markdown("""
    <style>
    /* මුළු සයිට් එකම Dark පෙනුමක් ලබා දීම */
    .stApp { background-color: #0d1117; color: white; }
    
    /* වම් පැත්තේ Sidebar (මෙනු බාර්) එක තද නිල් පාට කිරීම */
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;
        min-width: 260px !important;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* මෙනු හෙඩර්ස් (Orange Color) */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 8px;
        margin: 15px 0px 5px 0px;
        text-align: center;
        color: white;
    }

    /* කොටු (Boxes) ලස්සන කිරීම */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #e67e22;
        margin-bottom: 25px;
    }

    /* අනවශ්‍ය Streamlit අංග සැඟවීම */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN පද්ධතිය ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login_view():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        email = st.text_input("Username / Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In to Dashboard", use_container_width=True):
            if email == "happyshop@gmail.com" and pwd == "VLG0005":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif email == "demo1@gmail.com" and pwd == "demo1":
                st.session_state.user = {"name": "Staff 01", "role": "STAFF"}
                st.rerun()
            else:
                st.error("විස්තර වැරදියි. නැවත උත්සාහ කරන්න.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. APP එකේ ඇතුලත (ප්‍රධාන කොටස) ---
if st.session_state.user is None:
    login_view()
else:
    # --- සයිඩ් බාර් මෙනු එක (ඔන්න මචං උඹ ඉල්ලපු මෙනු එක මෙතන තියෙනවා) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>🛒 HappyShop</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>User: <b>{st.session_state.user['name']}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # සාමාන්‍ය මෙනු අයිතම
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        # Orders මෙනු එක
        st.markdown("<div class='menu-header'>ORDERS</div>", unsafe_allow_html=True)
        choice = st.radio("Navigation", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        # අනිත් අංශ
        st.markdown("<div class='menu-header'>SHIPPED & RETURN</div>", unsafe_allow_html=True)
        st.write("🚚 Shipped Items")
        st.write("🔄 Return Orders")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Logout බටන් එක (Error එක එන්නේ නැති වෙන්න හැදුවා)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- මෙනු එකේ තෝරන පේජ් එක අනුව පෙනුම වෙනස් වීම ---
    if choice == "New Order":
        st.markdown("## 📝 Customer / Waybill Entry")
        
        # පිටුව කොටස් දෙකකට බෙදීම (Screenshot එකේ තිබුණු විදිහට)
        col_main, col_side = st.columns([1.6, 1], gap="large")
        
        with col_main:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            st.selectbox("Target User", ["All", "Registered", "Guest"])
            st.text_input("Customer Name *", placeholder="Enter customer's name")
            st.text_area("Address *", placeholder="Enter delivery address")
            
            c1, c2 = st.columns(2)
            c1.selectbox("Select City *", ["Colombo", "Kandy", "Galle", "Matale"])
            c2.selectbox("Select District *", ["Colombo", "Gampaha", "Kalutara", "Kandy"])
            
            p1, p2 = st.columns(2)
            p1.text_input("Contact Number One *")
            p2.text_input("Contact Number Two")
            
            st.date_input("Due Date", value=datetime.now())
            st.selectbox("Order Source", ["FB Lead", "WhatsApp", "Web", "Call"])
            st.selectbox("Payment Method", ["COD (Cash on Delivery)", "Bank Transfer"])
            st.markdown("</div>", unsafe_allow_html=True)

        with col_side:
            st.markdown("<div class='section-box'><b>📦 Product & Pricing</b>", unsafe_allow_html=True)
            st.selectbox("Select Product *", [
                "Kesharaia Hair Oil [VGLS0005]", 
                "Herbal Crown: 1 [VGLS0001]", 
                "Maas Go Capsules [VGLS0006]"
            ])
            st.number_input("Qty", min_value=1, value=1)
            st.number_input("Sale Amount (LKR)", min_value=0.0)
            st.text_area("Product Note", height=80)
            st.number_input("Discount", min_value=0.0)
            
            st.markdown("<b>🚚 Courier Info</b>", unsafe_allow_html=True)
            st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
            st.number_input("Delivery Charge", min_value=0.0)
            
            st.divider()
            st.markdown("<h3 style='text-align:right;'>Total: Rs. 0.00</h3>", unsafe_allow_html=True)
            
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                st.success("Order Saved Successfully!")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.write(f"### {choice}")
        st.info("මෙම අංශය දැනට සකස් කරමින් පවතියි.")
