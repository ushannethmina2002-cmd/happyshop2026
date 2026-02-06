import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් එකේ සැකසුම් (මෙනු එක සහ Icon සුදු පාට කිරීම) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (Hamburger Icon එක සුදු පාටට එන්න) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    
    /* ☰ මෙනු ඉරි කෑලි 3 සුදු පාට කිරීම */
    [data-testid="stHeader"] button svg {
        fill: white !important;
        color: white !important;
    }
    
    /* Sidebar (Sidebar එකේ පාට) */
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* මෙනු Headers */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 8px;
        margin-top: 15px;
        text-align: center;
    }

    /* කොටු (Boxes) */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #e67e22;
        margin-bottom: 20px;
    }

    /* අනවශ්‍ය දේවල් අයින් කිරීම */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ඩේටා ටික තියාගන්න (Session State) ---
if 'orders_list' not in st.session_state:
    st.session_state.orders_list = [
        {"Date": "2026-02-06", "Name": "Wasantha Bandara", "Phone": "0773411920", "Address": "Matale", "Product": "Kesharaia Hair Oil", "Status": "Pending", "Total": 2500.0}
    ]

# --- 4. LOGIN SYSTEM ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login_view():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
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
    login_view()
else:
    # --- සයිඩ් බාර් මෙනු එක (SIDEBAR) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>🛒 HappyShop</h2>", unsafe_allow_html=True)
        st.markdown("<div class='menu-header'>ORDERS</div>", unsafe_allow_html=True)
        
        # මෙනු එකේ තේරීම්
        choice = st.radio("Navigation", [
            "New Order", "Pending Orders", "Order Search", 
            "Order History", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-header'>SYSTEM</div>", unsafe_allow_html=True)
        st.write("🚚 Shipped Items")
        st.write("🔄 Return Orders")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- පේජ් වලට අදාළ ඩේටා පෙන්වීම ---
    df = pd.DataFrame(st.session_state.orders_list)

    if choice == "New Order":
        st.markdown("## 📝 New Order Entry")
        c1, c2 = st.columns([1.6, 1], gap="large")
        with c1:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            phone = st.text_input("Phone Number *")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='section-box'><b>📦 Product Info</b>", unsafe_allow_html=True)
            prod = st.selectbox("Item", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            amt = st.number_input("Sale Price", min_value=0.0)
            if st.button("🚀 SAVE ORDER", use_container_width=True):
                new_data = {"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Address": addr, "Product": prod, "Status": "Pending", "Total": amt}
                st.session_state.orders_list.append(new_data)
                st.success("සාර්ථකව සේව් කළා!")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Order Search":
        st.header("🔍 Order Search")
        q = st.text_input("සෙවීමට නම හෝ දුරකථනය ටයිප් කරන්න")
        if q:
            res = df[df.apply(lambda row: q.lower() in str(row).lower(), axis=1)]
            st.dataframe(res, use_container_width=True)

    elif choice == "Order History":
        st.header("📜 Order History")
        st.dataframe(df, use_container_width=True)
