import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Happy Shop ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. PROFESSIONAL DARK UI CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    header[data-testid="stHeader"] { background-color: #000000 !important; border-bottom: 2px solid #e67e22; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Sidebar Brand Styling */
    .sidebar-brand { font-size: 28px; font-weight: bold; color: #e67e22; text-align: center; padding: 20px; border-bottom: 1px solid #333; margin-bottom: 20px; }
    
    /* Form & Section Containers */
    .form-container { background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }
    .section-header { background: linear-gradient(90deg, #e67e22, #d35400); color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] { color: #e67e22 !important; }
    
    .stButton>button { background-color: #e67e22 !important; color: white !important; border-radius: 5px; width: 100%; border: none; font-weight: bold; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state: st.session_state.orders = []

# --- 4. LOGIN SYSTEM ---
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='form-container'><h2 style='text-align:center;'>Happy Shop ERP</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Access Denied!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR NAVIGATION (පින්තූරවල තිබූ අනුපිළිවෙලට) ---
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>Happy Shop</div>", unsafe_allow_html=True)
        
        menu = st.selectbox("MAIN NAVIGATION", [
            "🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"
        ])
        
        # Sub-menus based on your screenshots
        sub_menu = "None"
        if menu == "📦 GRN":
            sub_menu = st.radio("GRN Options", ["New GRN", "GRN List", "Reorder List", "New PO", "PO List", "Packing", "Packing List"])
        elif menu == "🧾 Orders":
            sub_menu = st.radio("Order Options", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Options", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills", "Courier Feedback Summary"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Options", ["Add Returns", "Returned Orders", "Pending Returns"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Options", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
        elif menu == "🏷️ Products":
            sub_menu = st.radio("Product Options", ["Create Product", "View Products", "Raw Items"])

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. MAIN CONTENT AREA ---
    
    # 🏠 DASHBOARD
    if menu == "🏠 Dashboard":
        st.markdown("## 🏠 Welcome to Dashboard")
        m1, m2, m3, m4 = st.columns(4)
        total_sales = sum(float(d['Amount']) for d in st.session_state.orders) if st.session_state.orders else 0.0
        m1.metric("Total Sales", f"LKR {total_sales:,.2f}")
        m2.metric("Orders", len(st.session_state.orders))
        m3.metric("Pending", "0")
        m4.metric("Shipped", "0")
        
        st.info("මෙහි දත්ත සාරාංශය පෙන්වයි.")

    # 🧾 NEW ORDER ENTRY (පින්තූරයේ තිබූ සම්පූර්ණ විස්තර සහිතව)
    elif menu == "🧾 Orders" and sub_menu == "New Order":
        st.markdown("<div class='section-header'>NEW ORDER ENTRY</div>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👤 Customer Details")
                c_name = st.text_input("Customer Name *")
                c_address = st.text_area("Address *")
                c_city = st.text_input("City *")
                c_district = st.selectbox("Select District...", ["Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya", "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar", "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee", "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla", "Moneragala", "Ratnapura", "Kegalle"])
                c_phone1 = st.text_input("Contact Number One *")
                c_phone2 = st.text_input("Contact Number Two")
                c_email = st.text_input("Email")
                c_source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Tiktok", "Web Site", "Other"])
                c_cod = st.selectbox("Payment Type", ["COD", "Bank Transfer", "Card Payment"])
                
            with col2:
                st.markdown("#### 📦 Product & Courier Details")
                p_item = st.selectbox("Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go", "Other"])
                p_qty = st.number_input("Qty", min_value=1, value=1)
                p_amt = st.number_input("Sale Amount (Total Price)", min_value=0.0)
                p_note = st.text_input("Product Note")
                p_discount = st.number_input("Product Discount", min_value=0.0)
                
                st.markdown("---")
                courier_co = st.selectbox("Courier Company", ["Any", "Koombiyo Delivery", "Domex", "Pronto", "Flash"])
                ref_no = st.text_input("Reference No")
                weight = st.number_input("Pkg Weight (kgs)", min_value=0.0)
                del_charge = st.number_input("Delivery Charge", min_value=0.0)
                
                st.markdown("#### 💰 Summary")
                final_total = (p_amt + del_charge) - p_discount
                st.write(f"**Total Amount to Collect: LKR {final_total:,.2f}**")
                
            if st.button("🚀 SUBMIT ORDER"):
                if c_name and c_phone1:
                    st.session_state.orders.append({
                        "ID": f"HS-{1000 + len(st.session_state.orders)}",
                        "Name": c_name, "Phone": c_phone1, "District": c_district,
                        "Item": p_item, "Amount": final_total, "Date": str(datetime.now().date())
                    })
                    st.success("ඕඩර් එක සාර්ථකව ඇතුළත් කළා!")
                else: st.warning("කරුණාකර අනිවාර්ය කොටස් (Name, Address, Phone) සම්පූර්ණ කරන්න.")

    # 📊 VIEW STOCKS (පින්තූරයේ තිබූ Table එකට අනුව)
    elif menu == "📊 Stocks" and sub_menu == "View Stocks":
        st.markdown("<div class='section-header'>CURRENT STOCK LEVELS</div>", unsafe_allow_html=True)
        # Sample stock data as per your image
        stock_data = [
            {"Product": "Hair Oil", "Product Code": "VGLS0005", "Price": 2950.00, "Available Qty": 272, "Packed Qty": 0},
            {"Product": "Crown 1", "Product Code": "VGLS0001", "Price": 2400.00, "Available Qty": 50, "Packed Qty": 0},
            {"Product": "Kalkaya", "Product Code": "VGLS0003", "Price": 2800.00, "Available Qty": 624, "Packed Qty": 0},
            {"Product": "Capsules", "Product Code": "VGLS0006", "Price": 2500.00, "Available Qty": 90, "Packed Qty": 0}
        ]
        st.table(pd.DataFrame(stock_data))

    # 🏷️ CREATE PRODUCT (පින්තූරයේ තිබූ Form එකට අනුව)
    elif menu == "🏷️ Products" and sub_menu == "Create Product":
        st.markdown("<div class='section-header'>CREATE NEW PRODUCT</div>", unsafe_allow_html=True)
        pc1, pc2 = st.columns(2)
        with pc1:
            st.text_input("Product Name")
            st.text_input("Product Price")
            st.text_input("Barcode")
        with pc2:
            st.text_input("Product Code")
            st.text_input("Maximum Price")
            st.text_input("Reorder Qty")
        st.file_uploader("Upload Product Image")
        st.button("Save Product")

    else:
        st.info(f"{menu} > {sub_menu} අංශය දැනට සැකසෙමින් පවතී.")

