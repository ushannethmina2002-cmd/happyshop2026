import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් සැකසුම් (Page Configurations) ---
st.set_page_config(
    page_title="Happy Shop Official ERP",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS: පැහැදිලි වර්ණ සහ සුපිරි පෙනුම ---
st.markdown("""
    <style>
    /* මුළු App එකේ පසුබිම - Light Grey for clarity */
    .stApp { background-color: #f8f9fa; color: #212529; }

    /* --- TOP BAR (තද කළු) --- */
    header[data-testid="stHeader"] {
        background-color: #111111 !important;
        border-bottom: 2px solid #e67e22;
    }
    
    /* Hamburger Icon එක සුදු කිරීම */
    [data-testid="stHeader"] button svg {
        fill: #ffffff !important;
    }

    /* --- SIDEBAR (තද කළු සහ තැඹිලි) --- */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 2px solid #222;
    }

    /* Sidebar Header (Happy Shop) */
    .sidebar-brand {
        padding: 25px 10px;
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        color: #e67e22 !important; /* Orange Color */
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar අකුරු සුදු කිරීම */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Section Boxes (Cards) - ඉතා පැහැදිලිව පෙනෙන ලෙස */
    .section-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8;
        margin-top: 10px;
    }

    /* Input Field Labels */
    .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
        color: #344767 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Buttons Style */
    .stButton>button {
        background-color: #e67e22 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #d35400 !important;
        box-shadow: 0 4px 15px rgba(230, 126, 34, 0.4) !important;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state: st.session_state.orders = []

# --- 4. LOGIN SYSTEM ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#2d3436;'>Happy Shop Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username / Email")
        p = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("Login තොරතුරු වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR MENU (Dark Sidebar with Happy Shop Logo) ---
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>Happy Shop</div>", unsafe_allow_html=True)
        
        main_choice = st.selectbox("GO TO SECTION", [
            "🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "📊 Stocks"
        ])

        # Submenu for Orders
        sub_choice = "None"
        if "Orders" in main_choice:
            st.markdown("<hr style='border: 0.5px solid #333;'>", unsafe_allow_html=True)
            sub_choice = st.radio("Order Actions", [
                "New Order", "Pending Orders", "Order Search", 
                "Order History", "Blacklist Manager"
            ])
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 6. MAIN CONTENT ---
    st.markdown(f"<h1 style='color:#2d3436;'>{main_choice}</h1>", unsafe_allow_html=True)
    
    if main_choice == "🏠 Dashboard":
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Welcome to Happy Shop Management System")
        st.write("අද දින පද්ධතියේ ක්‍රියාකාරීත්වය සහ දත්ත සාරාංශය පහතින් බලන්න.")
        
        # Summary Tiles
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Orders", len(st.session_state.orders))
        kpi2.metric("New Leads", "12")
        kpi3.metric("Revenue", "LKR 45,000")
        st.markdown("</div>", unsafe_allow_html=True)

    elif "Orders" in main_choice:
        st.markdown(f"### {sub_choice}")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        
        if sub_choice == "New Order":
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name")
                phone = st.text_input("Contact Number")
                address = st.text_area("Delivery Address")
            with c2:
                item = st.selectbox("Select Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
                qty = st.number_input("Quantity", min_value=1, value=1)
                amt = st.number_input("Total Amount (LKR)")
                
            if st.button("🚀 Confirm & Save Order"):
                if name and phone:
                    st.session_state.orders.append({
                        "Date": str(datetime.now().date()), 
                        "Name": name, "Phone": phone, 
                        "Item": item, "Amount": amt
                    })
                    st.success("ඕඩර් එක සාර්ථකව පද්ධතියට ඇතුළත් කළා!")
                else:
                    st.warning("කරුණාකර නම සහ දුරකථනය ඇතුළත් කරන්න.")

        elif sub_choice == "Order Search":
            q = st.text_input("සෙවීමට නම හෝ දුරකථනය ඇතුළත් කරන්න...")
            if st.session_state.orders:
                df = pd.DataFrame(st.session_state.orders)
                st.table(df) # පැහැදිලි Table එකක් ලෙස
            else:
                st.info("දත්ත කිසිවක් හමු නොවීය.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info(f"{main_choice} අංශය දැනට සැකසෙමින් පවතී.")

