import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් සැකසුම් ---
st.set_page_config(
    page_title="HappyShop Official ERP",
    page_icon="🛒",
    layout="wide"
)

# --- 2. CSS & HTML (උඹ එවපු Side Menu Layout එක) ---
st.markdown("""
    <style>
    /* මුළු පසුබිම */
    .stApp { background-color: #f8f9fa; color: #333; }

    /* --- TOP BAR --- */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: #ffffff;
        padding: 12px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        z-index: 999;
    }

    .menu-btn {
        font-size: 26px;
        cursor: pointer;
        margin-right: 15px;
        color: #333;
    }

    .brand-name {
        font-weight: bold;
        font-size: 20px;
        color: #333;
    }

    /* --- CUSTOM SIDE MENU (උඹ එවපු විදිහටම) --- */
    /* Streamlit Sidebar එක වෙනුවට මේක පාවිච්චි කරමු */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eee;
    }
    
    [data-testid="stSidebar"] * {
        color: #333 !important;
    }

    /* කොටු ලස්සන කිරීම */
    .section-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #eef0f2;
        margin-top: 80px; /* Top bar එකට යට නොවීමට */
    }

    /* Streamlit Default Header අයින් කිරීම */
    header {visibility: hidden;}
    #MainMenu, footer {visibility: hidden;}
    </style>

    <div class="top-bar">
        <span class="menu-btn">☰</span>
        <div class="brand-name">My Odds System / HappyShop ERP</div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (දත්ත සහ Login) ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 4. LOGIN පද්ධතිය ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>System Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("විස්තර වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR MENU (උඹ එවපු Menu Links ටික) ---
    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🗄️ Navigation")
        choice = st.radio("Menu", [
            "Home", "Live Odds", "VIP Tips", "Results", "New Order", "Order Search", "Contact"
        ])
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. අදාළ පේජ් වල ඩේටා (FEATURES) ---
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    
    if choice == "Home":
        st.subheader("🏠 Welcome to Dashboard")
        st.write("පද්ධතියේ සාරාංශය මෙහි පෙන්වයි.")
        
    elif choice == "Live Odds":
        st.subheader("📊 Live Odds System")
        st.info("දැනට ක්‍රියාත්මක වන Odds මෙතැනින් බලන්න.")

    elif choice == "New Order":
        st.subheader("📝 Create New Order")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
        with c2:
            item = st.selectbox("Product", ["Hair Oil", "Herbal Pack"])
            price = st.number_input("Price")
        
        if st.button("Save Order"):
            st.session_state.orders.append({"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Item": item, "Price": price})
            st.success("Order Saved Successfully!")

    elif choice == "Order Search":
        st.subheader("🔍 Order History / Search")
        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("දත්ත කිසිවක් නැත.")

    st.markdown("</div>", unsafe_allow_html=True)

