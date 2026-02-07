import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. පද්ධතියේ පෙනුම සහ සැකසුම් (Professional Dark Theme)
# =========================================================
st.set_page_config(page_title="HappyShop ERP v7.0 PRO", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .metric-card {
        background: #1c2128; padding: 20px; border-radius: 12px;
        border-top: 4px solid #FFD700; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .metric-card h4 { color: #8b949e; font-size: 12px; text-transform: uppercase; margin-bottom: 8px; }
    .metric-card h2 { color: #FFD700; font-size: 28px; font-weight: bold; margin: 0; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. දත්ත ගබඩාව ආරක්ෂිතව හැසිරවීම (Robust Data Engine)
# =========================================================

# පින්තූරවල තිබූ දත්ත ව්‍යුහය (Full Column Structure)
COLUMNS = {
    "leads": ["ID", "Date", "Customer", "Phone", "Location", "Product", "Qty", "Total", "Status", "Staff"],
    "stock": ["Code", "Product", "Qty", "Price", "Category"]
}

def safe_load_db(file_name, columns):
    """CSV එකේ ගැටලුවක් තිබුණත් බිඳ නොවැටී දත්ත ලබා ගැනීමට"""
    file_path = f"{file_name}.csv"
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # තීරු වල නම් පරීක්ෂා කර අඩු තීරු ඇත්නම් නිවැරදි කිරීම (Auto-Repair)
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                for c in missing_cols:
                    df[c] = "N/A" # අලුත් තීරුවක් ඇඩ් කිරීම
                return df[columns]
            return df[columns]
        return pd.DataFrame(columns=columns)
    except Exception as e:
        # වැරැද්දක් ආවොත් හිස් එකක් ලබා දීම
        return pd.DataFrame(columns=columns)

# සෙෂන් එකේ දත්ත තැන්පත් කිරීම
if "db" not in st.session_state:
    st.session_state.db = {
        "leads": safe_load_db("leads", COLUMNS["leads"]),
        "stock": safe_load_db("stock", COLUMNS["stock"])
    }

# ආරම්භක තොග (Default Stock Data)
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 225, "Price": 2950, "Category": "Hair Care"},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 85, "Price": 1800, "Category": "Skin Care"}
    ])

# =========================================================
# 3. ප්‍රධාන මෙනුව (Navigation Sidebar)
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='color: #FFD700; text-align: center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 12px;'>PREMIUM ERP v7.0</p>", unsafe_allow_html=True)
    st.divider()
    
    main_nav = st.radio("MAIN MODULES", ["📊 Executive Dashboard", "📝 Leads & Order Entry", "📦 Stock Inventory"])
    
    st.divider()
    # පද්ධතියේ ඇති විය හැකි ගැටලු විසඳීමට Force Reset බොත්තම
    if st.button("🛠️ Force Database Repair"):
        for key in COLUMNS.keys():
            if os.path.exists(f"{key}.csv"):
                os.remove(f"{key}.csv")
        st.cache_data.clear()
        st.success("Database Repaired! Reloading...")
        st.rerun()

# =========================================================
# 4. EXECUTIVE DASHBOARD (Charts & Metrics)
# =========================================================
if main_nav == "📊 Executive Dashboard":
    st.subheader("📊 Business Intelligence Overview")
    df_leads = st.session_state.db["leads"]
    
    # පින්තූරවල තිබූ ආකාරයට Metric Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.markdown(f'<div class="metric-card"><h4>TOTAL LEADS</h4><h2>{len(df_leads)}</h2></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><h4>CONFIRMED</h4><h2>{len(df_leads[df_leads["Status"]=="Confirmed"])}</h2></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><h4>NO ANSWER</h4><h2>{len(df_leads[df_leads["Status"]=="No Answer"])}</h2></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><h4>CANCELLED</h4><h2>{len(df_leads[df_leads["Status"]=="Cancelled"])}</h2></div>', unsafe_allow_html=True)
    with m5: st.markdown(f'<div class="metric-card"><h4>ON HOLD</h4><h2>{len(df_leads[df_leads["Status"]=="Hold"])}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        if not df_leads.empty:
            fig = px.bar(df_leads, x="Date", y="Total", color="Status", title="Revenue vs Status Trend")
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if not df_leads.empty:
            fig_pie = px.pie(df_leads, names='Status', hole=0.5, title="Lead Efficiency")
            fig_pie.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

# =========================================================
# 5. LEADS & ORDER ENTRY (Data Entry Form)
# =========================================================
elif main_nav == "📝 Leads & Order Entry":
    st.subheader("📝 Process New Leads & Orders")
    
    with st.expander("➕ OPEN NEW ORDER FORM", expanded=True):
        with st.form("order_form", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            c_name = f1.text_input("Customer Name")
            c_phone = f1.text_input("WhatsApp Number")
            c_loc = f1.text_input("Location / City")
            
            prod = f2.selectbox("Product Selection", st.session_state.db["stock"]["Product"])
            qty = f2.number_input("Order Quantity", 1, 100)
            
            status = f3.selectbox("Set Initial Status", ["Pending", "Confirmed", "No Answer", "Hold", "Cancelled"])
            staff = f3.text_input("Assigned Staff", "Admin")
            
            if st.form_submit_button("🔥 SUBMIT ORDER TO SYSTEM"):
                if c_name and c_phone:
                    price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                    new_id = f"ORD-{uuid.uuid4().hex[:5].upper()}"
                    new_row = {
                        "ID": new_id, "Date": str(date.today()), "Customer": c_name, "Phone": c_phone,
                        "Location": c_loc, "Product": prod, "Qty": qty, "Total": price*qty,
                        "Status": status, "Staff": staff
                    }
                    st.session_state.db["leads"] = pd.concat([st.session_state.db["leads"], pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Order {new_id} Sync Completed!")
                    st.rerun()
                else:
                    st.error("Please fill Customer Name and Phone!")

    st.markdown("### 📋 Recent Sales / Leads Table")
    st.dataframe(st.session_state.db["leads"], use_container_width=True)

# =========================================================
# 6. STOCK INVENTORY
# =========================================================
elif main_nav == "📦 Stock Inventory":
    st.subheader("📦 Live Inventory Tracking")
    st.dataframe(st.session_state.db["stock"], use_container_width=True)
    
    # ස්ටොක් අප්ඩේට් කිරීමේ පහසුකම
    with st.expander("Update Product Stock"):
        u_prod = st.selectbox("Select Product", st.session_state.db["stock"]["Product"])
        u_qty = st.number_input("New Stock Level", value=0)
        if st.button("Save Changes"):
            st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == u_prod, "Qty"] = u_qty
            st.success("Stock Level Updated!")
            st.rerun()

# =========================================================
# 7. දත්ත ස්වයංක්‍රීයව සේව් කිරීම (Auto-Save)
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
