import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. පද්ධතියේ පෙනුම (Modern Professional UI)
# =========================================================
st.set_page_config(page_title="HappyShop ERP v8.0 PRO", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .metric-card {
        background: #161b22; padding: 20px; border-radius: 12px;
        border: 1px solid #30363d; text-align: center;
        border-top: 4px solid #FFD700;
    }
    .metric-card h2 { color: #FFD700; margin: 10px 0; font-size: 32px; }
    .metric-card h4 { color: #8b949e; text-transform: uppercase; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. Database Engine (Zero-Error Architecture)
# =========================================================
# පින්තූරවල තිබූ නිවැරදි Column Names මෙන්න
COLS = ["ID", "Date", "Customer", "Phone", "Location", "Product", "Qty", "Total", "Status", "Staff"]

def initialize_database():
    file = "leads.csv"
    # වැදගත්ම කොටස: පරණ දත්ත සහ අලුත් කේතය නොගැලපේ නම් පරණ එක මකා දමයි
    if os.path.exists(file):
        try:
            df = pd.read_csv(file)
            if list(df.columns) != COLS:
                os.remove(file)
                return pd.DataFrame(columns=COLS)
            return df
        except:
            os.remove(file)
            return pd.DataFrame(columns=COLS)
    return pd.DataFrame(columns=COLS)

if "db" not in st.session_state:
    st.session_state.db = initialize_database()

# Stock දත්ත (පින්තූරවල තිබූ මිල ගණන් සමග)
if "stock" not in st.session_state:
    st.session_state.stock = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 225, "Price": 2950},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 85, "Price": 1800}
    ])

# =========================================================
# 3. Sidebar Navigation
# =========================================================
with st.sidebar:
    st.markdown("<h2 style='color: #FFD700;'>HAPPY SHOP ERP</h2>", unsafe_allow_html=True)
    menu = st.radio("GO TO MODULE", ["📊 Dashboard", "📝 Add/Manage Leads", "📦 Inventory"])
    st.divider()
    if st.button("🔄 Clean & Fix System"):
        if os.path.exists("leads.csv"): os.remove("leads.csv")
        st.rerun()

# =========================================================
# 4. Dashboard (පින්තූරවල තිබූ විදියටම)
# =========================================================
if menu == "📊 Dashboard":
    df = st.session_state.db
    
    # පින්තූරවල තිබූ Metrics 5
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.markdown(f'<div class="metric-card"><h4>Total Leads</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><h4>Confirmed</h4><h2>{len(df[df["Status"]=="Confirmed"])}</h2></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><h4>No Answer</h4><h2>{len(df[df["Status"]=="No Answer"])}</h2></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><h4>Cancelled</h4><h2>{len(df[df["Status"]=="Cancelled"])}</h2></div>', unsafe_allow_html=True)
    with m5: st.markdown(f'<div class="metric-card"><h4>On Hold</h4><h2>{len(df[df["Status"]=="Hold"])}</h2></div>', unsafe_allow_html=True)

    st.divider()
    
    if not df.empty:
        fig = px.bar(df, x="Date", y="Total", color="Status", title="Daily Sales Status", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("පද්ධතියට තවම දත්ත ඇතුළත් කර නැත.")

# =========================================================
# 5. Lead Entry (ඔබ එවූ පින්තූරවල තිබූ විදියටම)
# =========================================================
elif menu == "📝 Add/Manage Leads":
    st.subheader("📝 Lead & Order Management")
    
    # ඇණවුමක් ඇතුළත් කරන Form එක
    with st.expander("➕ Click to Add New Lead", expanded=True):
        with st.form("lead_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Customer Name")
            phone = c1.text_input("Phone Number")
            loc = c1.text_input("City/Location")
            
            prod = c2.selectbox("Product", st.session_state.stock["Product"])
            qty = c2.number_input("Qty", 1)
            
            status = c3.selectbox("Status", ["Pending", "Confirmed", "No Answer", "Hold", "Cancelled"])
            staff = c3.text_input("Staff Name", "Admin")
            
            if st.form_submit_button("SAVE LEAD"):
                if name and phone:
                    price = st.session_state.stock.loc[st.session_state.stock["Product"] == prod, "Price"].values[0]
                    new_id = f"HS-{uuid.uuid4().hex[:4].upper()}"
                    new_row = {
                        "ID": new_id, "Date": str(date.today()), "Customer": name, "Phone": phone,
                        "Location": loc, "Product": prod, "Qty": qty, "Total": price*qty,
                        "Status": status, "Staff": staff
                    }
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state.db.to_csv("leads.csv", index=False)
                    st.success("Lead Saved Successfully!")
                    st.rerun()

    st.markdown("### 📋 Lead Data Table")
    st.dataframe(st.session_state.db, use_container_width=True)

# =========================================================
# 6. Inventory
# =========================================================
elif menu == "📦 Inventory":
    st.subheader("📦 Product Stock")
    st.table(st.session_state.stock)
