import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් සැකසුම් ---
st.set_page_config(
    page_title="HappyShop Official ERP",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS: උඹ එවපු HTML මෙනු එකේ පෙනුම ලබා ගැනීමට ---
st.markdown("""
    <style>
    /* මුළු App එකේ පසුබිම */
    .stApp { background-color: #f4f4f4; color: #333; }

    /* --- TOP BAR (කළු පාට) --- */
    header[data-testid="stHeader"] {
        background-color: #111111 !important;
        color: white !important;
    }
    
    /* Hamburger Icon එක සුදු කිරීම */
    [data-testid="stHeader"] button svg {
        fill: white !important;
    }

    /* --- SIDEBAR (තද කළු පාට) --- */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        color: white !important;
        border-right: 1px solid #222;
    }

    /* Sidebar අකුරු සහ අයිකන් සුදු කිරීම */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Sidebar Header (Sandun) */
    .sidebar-user {
        padding: 20px;
        font-size: 22px;
        font-weight: bold;
        border-bottom: 1px solid #222;
        text-align: center;
        color: #f1c40f !important;
    }

    /* මෙනු අයිටම් වල පෙනුම */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    /* Section Boxes */
    .section-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
        margin-top: 20px;
    }

    /* අනවශ්‍ය දේවල් අයින් කිරීම */
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (දත්ත පාලනය) ---
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
        st.markdown("<h2 style='text-align:center;'>Sandun ERP Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Sandun"
                st.rerun()
            else:
                st.error("විස්තර වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR MENU (Dark Sidebar with Submenu) ---
    with st.sidebar:
        st.markdown("<div class='sidebar-user'>Sandun</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ප්‍රධාන මෙනු එක
        main_choice = st.selectbox("MAIN MENU", [
            "🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks"
        ])

        # Orders තේරුවොත් පමණක් Submenu එක පෙන්වීම (උඹේ HTML එකේ විදියට)
        sub_choice = "None"
        if "Orders" in main_choice:
            st.markdown("---")
            st.markdown("<p style='color:#ccc; font-size:12px; margin-left:10px;'>ORDERS SUBMENU</p>", unsafe_allow_html=True)
            sub_choice = st.radio("Select Action", [
                "New Order", "Pending Orders", "Order Search", 
                "Import Lead", "View Lead", "Add Lead", 
                "Order History", "Exchanging Orders", "Blacklist Manager"
            ], label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 6. අන්තර්ගතය (Main Content Area) ---
    st.markdown(f"### {main_choice}")
    
    if main_choice == "🏠 Dashboard":
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Welcome back, Sandun!")
        st.write("අද දින ඕඩර් ප්‍රමාණය සහ සාරාංශය මෙහි පෙන්වයි.")
        st.markdown("</div>", unsafe_allow_html=True)

    elif "Orders" in main_choice:
        st.markdown(f"#### 🧾 {sub_choice}")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        
        if sub_choice == "New Order":
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name")
                phone = st.text_input("Contact")
            with c2:
                item = st.selectbox("Product", ["Hair Oil", "Herbal Kit"])
                amt = st.number_input("Amount")
            if st.button("Save Order"):
                st.session_state.orders.append({
                    "Date": str(datetime.now().date()), 
                    "Name": name, "Phone": phone, 
                    "Item": item, "Amount": amt
                })
                st.success("Order Saved!")

        elif sub_choice == "Order Search":
            q = st.text_input("සෙවීමට නම ඇතුළත් කරන්න")
            if st.session_state.orders:
                df = pd.DataFrame(st.session_state.orders)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("දත්ත කිසිවක් නැත.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info(f"{main_choice} සඳහා දත්ත පද්ධතිය සකස් වෙමින් පවතී.")

