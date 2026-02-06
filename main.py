import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP (මෙනු එක සහ Hamburger Icon එක පේන්න) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (පින්තූරවල තියෙන ලස්සන පෙනුම සහ සුදු ඉරි කෑලි) ---
st.markdown("""
    <style>
    /* Dark Theme */
    .stApp { background-color: #0d1117; color: white; }
    
    /* ☰ Hamburger Menu Icon එක සුදු පාට කිරීම */
    [data-testid="stHeader"] button svg {
        fill: white !important;
        color: white !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Orange Menu Headers */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 8px;
        margin-top: 15px;
        text-align: center;
        text-transform: uppercase;
        font-size: 14px;
    }

    /* ලස්සනට කොටු කිරීම (Section Boxes) */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #e67e22;
        margin-bottom: 20px;
    }

    /* අනවශ්‍ය Streamlit දේවල් අයින් කිරීම */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. DATA INITIALIZATION ---
if 'orders_list' not in st.session_state:
    st.session_state.orders_list = []

# LOGIN VIEW
def login_view():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        u = st.text_input("Username / Email")
        p = st.text_input("Password", type="password")
        if st.button("Log In to System", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("විස්තර වැරදියි. Username: happyshop@gmail.com | Password: VLG0005")
        st.markdown("</div>", unsafe_allow_html=True)

# MAIN INTERFACE
if st.session_state.user is None:
    login_view()
else:
    # --- සයිඩ් බාර් මෙනු එක (මෙන්න උඹ ඉල්ලපු මෙනු එක) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>🛒 HappyShop</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Logged in: <b>Admin</b></p>", unsafe_allow_html=True)
        
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        st.markdown("<div class='menu-header'>ORDERS</div>", unsafe_allow_html=True)
        choice = st.radio("Nav", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-header'>SHIPPED & RETURN</div>", unsafe_allow_html=True)
        st.write("🚚 Shipped Items")
        st.write("🔄 Return Orders")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- මෙනු එකේ පේජ් වලට අදාළ කෑලි ---
    if choice == "New Order":
        st.markdown("## 📝 New Order Entry")
        c1, c2 = st.columns([1.6, 1], gap="large")
        
        with c1:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            phone = st.text_input("Contact Number *")
            city = st.selectbox("Select City", ["Colombo", "Kandy", "Matale", "Galle"])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='section-box'><b>📦 Product & Pricing</b>", unsafe_allow_html=True)
            prod = st.selectbox("Select Product *", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            qty = st.number_input("Qty", min_value=1, value=1)
            amt = st.number_input("Sale Amount (LKR)", min_value=0.0)
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                new_data = {"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Product": prod, "Status": "Pending", "Total": amt}
                st.session_state.orders_list.append(new_data)
                st.success("ඕඩර් එක සාර්ථකව සේව් කළා!")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Order Search":
        st.header("🔍 Order Search")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        q = st.text_input("සෙවීමට නම හෝ දුරකථන අංකය ඇතුළත් කරන්න")
        if q and st.session_state.orders_list:
            df = pd.DataFrame(st.session_state.orders_list)
            res = df[df.apply(lambda row: q.lower() in str(row).lower(), axis=1)]
            st.dataframe(res, use_container_width=True)
        elif q:
            st.info("කිසිදු ඕඩර් එකක් හමු නොවීය.")
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Order History":
        st.header("📜 Order History")
        if st.session_state.orders_list:
            st.dataframe(pd.DataFrame(st.session_state.orders_list), use_container_width=True)
        else:
            st.info("දැනට කිසිදු ඕඩර් එකක් දත්ත පද්ධතියේ නැත.")

    else:
        st.info(f"The '{choice}' section is coming soon.")
