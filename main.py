import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. ADVANCED UI & THEME CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid #FFD700;
    }

    .brand-title {
        font-size: 35px;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.3);
    }

    /* Metric Cards */
    .metric-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 12px; border-left: 5px solid #FFD700;
        min-width: 150px; flex: 1; text-align: center;
    }
    .metric-card h4 { margin: 0; font-size: 12px; color: #ccc; text-transform: uppercase; }
    .metric-card h2 { margin: 5px 0; font-size: 22px; color: #FFD700; }

    /* Custom Status Colors for metrics */
    .status-confirmed { border-left-color: #2ecc71; }
    .status-noanswer { border-left-color: #f1c40f; }
    .status-cancel { border-left-color: #e74c3c; }
    .status-fake { border-left-color: #95a5a6; }
    .status-hold { border-left-color: #9b59b6; }

    .top-nav {
        background: rgba(255, 255, 255, 0.03);
        padding: 12px; border-radius: 12px;
        border: 1px solid rgba(255, 215, 0, 0.2); margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ADVANCED DATA ENGINE (CSV DATABASE)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# පින්තූරවල ඇති සියලුම අංශ සඳහා Database සකස් කිරීම
if "db" not in st.session_state:
    st.session_state.db = {
        "orders": load_db("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price", "Value", "Type"]),
        "expenses": load_db("expenses.csv", ["date", "type", "category", "amount", "note"]),
        "logistics": load_db("logistics.csv", ["order_id", "waybill", "courier", "status", "dispatch_date"]),
        "returns": load_db("returns.csv", ["order_id", "date", "reason", "status"]),
        "grn_po": load_db("grn_po.csv", ["type", "id", "date", "supplier", "items", "total", "status"]),
        "leads": load_db("leads.csv", ["id", "date", "source", "customer", "phone", "status"]),
        "blacklist": load_db("blacklist.csv", ["phone", "reason", "date"])
    }

# Default Stock Data
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 225, "Price": 2950, "Value": 663750, "Type": "Finished"},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 85, "Price": 1800, "Value": 153000, "Type": "Finished"},
        {"Code": "FWG-03", "Product": "Face Wash Gold", "Qty": 110, "Price": 1200, "Value": 132000, "Type": "Finished"}
    ])

# =========================================================
# 3. SIDEBAR NAVIGATION (With All Image Menu Items)
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-title">Happy Shop</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-size:11px; margin-top:-10px;">PREMIUM ERP SYSTEM</p>', unsafe_allow_html=True)
    st.divider()
    
    main_nav = st.selectbox("GO TO SECTION", ["🏠 Dashboard", "🔍 Orders & Leads", "🚚 Logistics & Shipping", "📦 Inventory Control", "💰 Finance & Expenses", "🔄 Returns Management"])
    
    st.markdown("---")
    # එක් එක් අංශයට අදාළ Sub-menus (පින්තූරවල තිබූ දේවල්)
    if main_nav == "🔍 Orders & Leads":
        sub_nav = st.radio("Actions", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Order History", "Blacklist Manager"])
    elif main_nav == "🚚 Logistics & Shipping":
        sub_nav = st.radio("Actions", ["Ship Items", "Shipped List", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills"])
    elif main_nav == "📦 Inventory Control":
        sub_nav = st.radio("Actions", ["View Stocks", "Stock Adjustment", "Stock Values", "Create Product", "Raw Items", "New GRN", "New PO", "Reorder List"])
    elif main_nav == "💰 Finance & Expenses":
        sub_nav = st.radio("Actions", ["New Expense", "View Expenses", "Create Expense Type", "View Expense Type", "POS Expenses", "Financial Summary"])
    elif main_nav == "🔄 Returns Management":
        sub_nav = st.radio("Actions", ["Add Returns", "Returned Orders", "Pending Returns", "Return Analysis"])
    else:
        sub_nav = "Main Dashboard"

    st.divider()
    if st.button("🚪 Logout System", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =========================================================
# 4. MODULES IMPLEMENTATION
# =========================================================

# --- 1. DASHBOARD ---
if main_nav == "🏠 Dashboard":
    st.markdown('<div class="top-nav"><h3>📊 Executive Business Intelligence</h3></div>', unsafe_allow_html=True)
    
    ord_df = st.session_state.db['orders']
    # Metrics Row
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card"><h4>TOTAL LEADS</h4><h2>{len(ord_df)}</h2></div>
        <div class="metric-card status-confirmed"><h4>CONFIRMED</h4><h2>{len(ord_df[ord_df['status']=='confirm'])}</h2></div>
        <div class="metric-card status-noanswer"><h4>NO ANSWER</h4><h2>{len(ord_df[ord_df['status']=='noanswer'])}</h2></div>
        <div class="metric-card status-cancel"><h4>CANCELLED</h4><h2>{len(ord_df[ord_df['status']=='cancel'])}</h2></div>
        <div class="metric-card status-fake"><h4>FAKE</h4><h2>{len(ord_df[ord_df['status']=='fake'])}</h2></div>
        <div class="metric-card status-hold"><h4>ON HOLD</h4><h2>{len(ord_df[ord_df['status']=='hold'])}</h2></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.line(ord_df, x='date', y='total', title="Revenue Stream", markers=True)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<div class="top-nav"><h4>Quick Status Update</h4></div>', unsafe_allow_html=True)
        st.write("Recent Activity Log...")
        st.table(ord_df.tail(5)[['id', 'status']])

# --- 2. ORDERS & LEADS ---
elif main_nav == "🔍 Orders & Leads":
    st.title(f"📑 {sub_nav}")
    if sub_nav == "New Order":
        with st.form("new_order_f"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer Name")
            phone = c1.text_input("Phone Number")
            prod = c2.selectbox("Product", st.session_state.db["stock"]["Product"])
            qty = c2.number_input("Quantity", 1)
            if st.form_submit_button("Place Order"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                oid = f"ORD-{uuid.uuid4().hex[:5].upper()}"
                new_row = {"id": oid, "date": str(date.today()), "name": name, "phone": phone, "address": "N/A", "prod": prod, "qty": qty, "total": price*qty, "status": "pending", "staff": "Admin"}
                st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Order {oid} recorded!")
    
    elif sub_nav == "Blacklist Manager":
        st.subheader("Manage Restricted Customers")
        st.dataframe(st.session_state.db["blacklist"], use_container_width=True)
    
    else:
        st.dataframe(st.session_state.db["orders"], use_container_width=True)

# --- 3. LOGISTICS ---
elif main_nav == "🚚 Logistics & Shipping":
    st.title(f"🚚 {sub_nav}")
    if sub_nav == "Search Waybills":
        wb = st.text_input("Enter Waybill Number")
        if wb: st.info(f"Searching for {wb} in Courier API...")
    
    st.dataframe(st.session_state.db["logistics"], use_container_width=True)
    col1, col2 = st.columns(2)
    col1.button("🚚 Dispatch Selected Items")
    col2.button("🖨️ Print Labels")

# --- 4. INVENTORY ---
elif main_nav == "📦 Inventory Control":
    st.title(f"📦 {sub_nav}")
    if sub_nav == "Stock Adjustment":
        p_code = st.selectbox("Product", st.session_state.db["stock"]["Code"])
        st.number_input("New Quantity")
        st.button("Update Stock")
    
    elif sub_nav == "New GRN":
        st.subheader("Good Received Note")
        st.text_input("Supplier Name")
        st.button("Save GRN")
        
    st.dataframe(st.session_state.db["stock"], use_container_width=True)

# --- 5. FINANCE ---
elif main_nav == "💰 Finance & Expenses":
    st.title(f"💰 {sub_nav}")
    if sub_nav == "New Expense":
        with st.form("exp"):
            st.selectbox("Type", ["Marketing", "Salaries", "Bills"])
            st.number_input("Amount")
            st.form_submit_button("Record Expense")
            
    st.dataframe(st.session_state.db["expenses"], use_container_width=True)

# --- 6. RETURNS ---
elif main_nav == "🔄 Returns Management":
    st.title(f"🔄 {sub_nav}")
    if sub_nav == "Add Returns":
        st.text_input("Original Order ID")
        st.selectbox("Reason", ["Damaged", "Refused", "Wrong Item"])
        st.button("Process Return")
        
    st.dataframe(st.session_state.db["returns"], use_container_width=True)

# =========================================================
# 5. AUTO-SAVE ENGINE
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
