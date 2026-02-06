import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් එකේ මූලික සැකසුම් (මෙනු එක පේන්නම) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (Hamburger Icon එක සුදු පාටට සහ සයිඩ් බාර් එක ලස්සනට) ---
st.markdown("""
    <style>
    /* මුළු පසුබිම */
    .stApp { background-color: #0d1117; color: white; }
    
    /* ☰ Hamburger Menu Icon එක සුදු පාට කිරීම - මේක අනිවාර්යයි */
    [data-testid="stHeader"] button svg {
        fill: white !important;
        color: white !important;
        width: 30px;
        height: 30px;
    }
    
    /* වම් පැත්තේ Sidebar (මෙනු බාර්) එකේ පෙනුම */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
        min-width: 260px !important;
    }
    
    /* Sidebar අකුරු සුදු පාට කිරීම */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* කොටු ලස්සන කිරීම */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        border-left: 5px solid #e67e22;
        margin-bottom: 20px;
    }

    /* අනවශ්‍ය දේවල් අයින් කිරීම */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. දත්ත කළමනාකරණය ---
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"Date": "2026-02-06", "Name": "Wasantha Bandara", "Contact": "0773411920", "Product": "Kesharaia Hair Oil", "Status": "Pending"}
    ]
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. LOGIN SYSTEM ---
def login_page():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("Login වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. පද්ධතියේ ප්‍රධාන කොටස ---
if st.session_state.user is None:
    login_page()
else:
    # --- සයිඩ් බාර් මෙනු එක (SIDEBAR) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MANAGER</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # උඹ එවපු හැම මෙනු අයිතමයක්ම මෙතන තියෙනවා
        choice = st.radio("MAIN MENU", [
            "🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", 
            "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"
        ])

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- මෙනු එකේ තෝරන පේජ් එක අනුව පෙනුම ---
    if "Orders" in choice:
        sub = st.selectbox("Order Section", ["New Order", "Order Search", "Pending Orders", "Order History"])
        
        if sub == "New Order":
            st.markdown("## 📝 New Order Entry")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("<div class='section-box'><b>👤 Customer Details</b><br><br>", unsafe_allow_html=True)
                name = st.text_input("Customer Name *")
                phone = st.text_input("Phone Number *")
                addr = st.text_area("Address *")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='section-box'><b>📦 Product</b><br><br>", unsafe_allow_html=True)
                item = st.selectbox("Select Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
                price = st.number_input("Price", min_value=0.0)
                if st.button("Save Order", use_container_width=True):
                    st.session_state.orders.append({"Date": str(datetime.now().date()), "Name": name, "Contact": phone, "Product": item, "Status": "Pending"})
                    st.success("සාර්ථකව සේව් කළා!")
                st.markdown("</div>", unsafe_allow_html=True)
        
        elif sub == "Order Search":
            st.markdown("## 🔍 Order Search")
            q = st.text_input("නම හෝ දුරකථනය ගහන්න")
            df = pd.DataFrame(st.session_state.orders)
            st.table(df)

    elif "Dashboard" in choice:
        st.header("🏠 Welcome to Dashboard")
        st.info("මෙහි දත්ත සාරාංශය පෙන්වයි.")

    else:
        st.header(choice)
        st.warning("මෙම කොටස සකස් කරමින් පවතී.")
