import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. පිටුවේ සැකසුම් සහ Watermark ඉවත් කිරීම ---
st.set_page_config(page_title="HappyShop Enterprise ERP", page_icon="🛒", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            
            /* Sidebar එකේ නිල් පාට පසුබිම (Screenshot එකේ විදිහට) */
            [data-testid="stSidebar"] { background-color: #001f3f !important; }
            [data-testid="stSidebar"] * { color: white !important; }
            
            /* මෙනු කැටගරි වල තැඹිලි පාට (Screenshot එකේ විදිහට) */
            .menu-category {
                background-color: #e67e22;
                padding: 10px;
                font-weight: bold;
                color: white;
                margin-top: 10px;
            }
            
            /* ලොගින් ටයිටල් එක */
            .login-title {
                color: #f1c40f; 
                text-align: center; 
                font-size: 45px;
                font-weight: bold;
                line-height: 1.1;
                margin-bottom: 20px;
            }
            
            /* Order Form එකේ Section Headers */
            .section-header {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border-left: 5px solid #e67e22;
                margin-bottom: 15px;
                color: #333;
            }
            .stApp { background-color: white; }
            label { color: #333 !important; font-weight: bold !important; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. ඩේටාබේස් එක සැකසීම ---
conn = sqlite3.connect('happyshop_pro_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, 
            city TEXT, district TEXT, product TEXT, qty INTEGER, price REAL, 
            courier TEXT, status TEXT, date TEXT)''')
conn.commit()

# --- 3. ලොගින් පේජ් එක (Screenshot 1 ට අනුව) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # ලෝගෝ එක
        st.image("https://cdn-icons-png.flaticon.com/512/1170/1170678.png", width=120)
        st.markdown("<div class='login-title'>HappyShop<br>Login</div>", unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login to Dashboard", use_container_width=True):
            if email == "happyshop@gmail.com" and password == "VLG0005":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials. Please try again.")

# --- 4. සිස්ටම් එකේ ඇතුළත (Sidebar & Forms) ---
if not st.session_state.logged_in:
    login_view()
else:
    # මෙනු බාර් එක (Sidebar - Screenshot 3 ට අනුව)
    with st.sidebar:
        st.markdown("### 🛒 HappyShop ERP")
        st.markdown("<hr style='margin:5px;'>", unsafe_allow_html=True)
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        st.markdown("<div class='menu-category'>Orders</div>", unsafe_allow_html=True)
        choice = st.radio("Menu", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-category'>Shipped Items</div>", unsafe_allow_html=True)
        st.markdown("<div class='menu-category'>Return</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # New Order පේජ් එක (Screenshot 2 ට අනුව)
    if choice == "New Order":
        st.markdown("## 📝 New Order / Waybill Entry")
        col_left, col_right = st.columns([1.5, 1], gap="large")
        
        with col_left:
            st.markdown("<div class='section-header'>Customer Details</div>", unsafe_allow_html=True)
            u_type = st.selectbox("User", ["All", "Registered", "Guest"])
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *", height=80)
            city = st.selectbox("Select City *", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            district = st.selectbox("Select District *", ["Colombo", "Gampaha", "Kalutara", "Kandy"])
            
            ph_c1, ph_c2 = st.columns(2)
            phone1 = ph_c1.text_input("Contact Number One *")
            phone2 = ph_c2.text_input("Contact Number Two")
            
            email_field = st.text_input("Email")
            o_date = st.date_input("Order Date", value=datetime.now())
            source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Web", "Direct"])
            payment = st.selectbox("Payment Method", ["COD", "Bank Transfer"])

        with col_right:
            st.markdown("<div class='section-header'>Product & Pricing</div>", unsafe_allow_html=True)
            product = st.selectbox("Select Product *", ["Product A", "Product B", "Product C"])
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Sale Amount (Rs.)", min_value=0.0)
            note = st.text_area("Product Note")
            discount = st.number_input("Product Discount", min_value=0.0)
            
            st.markdown("<div class='section-header'>Courier Info</div>", unsafe_allow_html=True)
            courier = st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
            ref_no = st.text_input("Reference No")
            weight = st.number_input("Pkg Weight (kgs)", value=0.5)
            
            st.divider()
            total = price - discount
            st.write(f"### Total Amount: Rs. {total:,.2f}")
            
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                if name and phone1 and address:
                    c.execute("INSERT INTO orders (name, phone, address, city, district, product, qty, price, courier, status, date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (name, phone1, address, city, district, product, qty, price, courier, 'Pending', str(o_date)))
                    conn.commit()
                    st.success("Order Saved Successfully!")
                else:
                    st.error("කරුණාකර අනිවාර්ය ක්ෂේත්‍ර (*) සම්පූර්ණ කරන්න.")

    elif choice == "Pending Orders":
        st.subheader("⏳ Pending Orders List")
        df = pd.read_sql("SELECT * FROM orders WHERE status='Pending'", conn)
        st.dataframe(df, use_container_width=True)
        
    elif choice == "Blacklist Manager":
        st.subheader("🚫 Blacklist Manager")
        st.info("No blacklisted customers found yet.")
    
    else:
        st.info(f"The '{choice}' section is currently being updated.")

