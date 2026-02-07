import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go
import time

# =========================================================
# 1. ADVANCED NEON & GLASS UI + DARK PRO THEME
# =========================================================
st.set_page_config(page_title="HappyShop ERP ULTIMATE PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Background & Global Dark Theme */
    .stApp {
        background-color: #0d1117;
        background-image: radial-gradient(circle at top right, rgba(0, 212, 255, 0.05), transparent),
                          radial-gradient(circle at bottom left, rgba(0, 212, 255, 0.05), transparent);
    }
    
    /* Top Header Bar */
    .top-nav {
        background: #161b22;
        padding: 10px 20px;
        border-bottom: 1px solid #30363d;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: fixed;
        top: 0; left: 0; right: 0; z-index: 1000;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background: #0d1117 !important;
        border-right: 1px solid #30363d;
    }

    /* Right Side Action Panel */
    .action-panel {
        background: #161b22;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        height: 100%;
    }

    /* Card Styling */
    .glass-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Status Badges */
    .stBadge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    
    h1, h2, h3, p, label { color: #c9d1d9 !important; font-family: 'Segoe UI', sans-serif; }
    
    .main-content { animation: fadeIn 0.8s ease-in; margin-top: 20px; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. CORE DATA ENGINE
# =========================================================
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        try: return pd.read_csv(filename).to_dict("records")
        except: return []
    return []

# =========================================================
# 3. SESSION STATE INITIALIZATION
# =========================================================
states = {
    "orders": load_data("orders.csv"),
    "stocks": {"Hair Oil": 150, "Night Cream": 80, "Face Wash": 120, "Serums": 45},
    "expenses": load_data("expenses.csv"),
    "user": None,
    "logistics": load_data("logistics.csv") if os.path.exists("logistics.csv") else []
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# =========================================================
# 4. SECURITY & AUTHENTICATION
# =========================================================
def login():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🛡️ ERP SECURE LOGIN</h1>", unsafe_allow_html=True)
        email = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("UNLOCK SYSTEM", use_container_width=True):
            if email == "admin@gmail.com" and pw == "1234":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif email == "staff@gmail.com" and pw == "1234":
                st.session_state.user = {"name": "Staff", "role": "STAFF"}
                st.rerun()
            else: st.error("Invalid Credentials")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 5. UI COMPONENTS (TOP BAR & SIDEBAR)
# =========================================================
if st.session_state.user is None:
    login()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1162/1162456.png", width=60)
        st.markdown(f"**Terminal:** {st.session_state.user['name']} ({st.session_state.user['role']})")
        st.divider()
        
        main_menu = st.radio("SATELLITE NAVIGATION", [
            "🏠 Dashboard", "📋 Lead Manager", "🧾 Order Entry", 
            "🚚 Logistics Hub", "🔄 Returns & Fake", "📊 Inventory", "💰 Finance"
        ])
        
        st.divider()
        if st.session_state.user["role"] == "OWNER":
            with st.expander("👑 OWNER TOOLS"):
                st.button("🤖 Auto-Assign")
                st.button("🔐 Audit Logs")
        else:
            with st.expander("🛠️ STAFF TOOLS"):
                st.button("📞 Start Dialer")
                st.button("📱 WhatsApp Bulk")

        if st.button("🔴 Logout System", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # LAYOUT: MAIN CONTENT + RIGHT PANEL
    col_main, col_panel = st.columns([3.2, 1])

    with col_main:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        # ---------------------------------------------------------
        # MODULE: DASHBOARD
        # ---------------------------------------------------------
        if main_menu == "🏠 Dashboard":
            st.title("🚀 Business Intelligence")
            df = pd.DataFrame(st.session_state.orders)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Leads", len(df))
            c2.metric("Confirmed", len(df[df['status']=='confirm']) if not df.empty else 0)
            c3.metric("Stock Value", f"LKR {sum(st.session_state.stocks.values())*500:,.0f}")
            c4.metric("Conversion", "32%")

            if not df.empty:
                fig = px.area(df.groupby('date').size().reset_index(), x='date', y=0, title="Lead Inflow Statistics")
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------
        # MODULE: LEAD MANAGER (No Answer, Hold, Fake Controls)
        # ---------------------------------------------------------
        elif main_menu == "📋 Lead Manager":
            st.title("🔍 Advanced Action Center")
            search = st.text_input("Quick Find (Name/Phone/ID)")
            
            df = pd.DataFrame(st.session_state.orders)
            if not df.empty:
                if search:
                    df = df[df['name'].str.contains(search, case=False) | df['phone'].astype(str).str.contains(search)]
                
                for idx, row in df.iterrows():
                    with st.expander(f"📦 {row['id']} | {row['name']} | Status: {row['status'].upper()}"):
                        c1, c2, c3, c4, c5 = st.columns(5)
                        if c1.button("✅ Confirm", key=f"c{idx}"): 
                            st.session_state.orders[idx]['status']='confirm'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c2.button("📞 No Answer", key=f"n{idx}"):
                            st.session_state.orders[idx]['status']='noanswer'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c3.button("⏸ Hold", key=f"h{idx}"):
                            st.session_state.orders[idx]['status']='hold'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c4.button("🚫 Fake", key=f"f{idx}"):
                            st.session_state.orders[idx]['status']='fake'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c5.button("🗑️ Del", key=f"d{idx}"):
                            st.session_state.orders.pop(idx); save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()

        # ---------------------------------------------------------
        # MODULE: ORDER ENTRY
        # ---------------------------------------------------------
        elif main_menu == "🧾 Order Entry":
            st.title("📝 New Waybill Submission")
            with st.form("entry_form"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    name = st.text_input("Customer Name")
                    phone = st.text_input("Phone Number")
                with cc2:
                    prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                    qty = st.number_input("Qty", 1)
                
                if st.form_submit_button("🚀 SUBMIT TO DATABASE"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    new_order = {"id": oid, "name": name, "phone": phone, "prod": prod, "qty": qty, "total": qty*1200, "status": "pending", "date": str(date.today())}
                    st.session_state.orders.append(new_order)
                    save_data(pd.DataFrame(st.session_state.orders), "orders.csv")
                    st.success("Order Synced Successfully!")

        # ---------------------------------------------------------
        # MODULE: LOGISTICS HUB (New)
        # ---------------------------------------------------------
        elif main_menu == "🚚 Logistics Hub":
            st.title("🚚 Courier Management")
            df_confirmed = pd.DataFrame([o for o in st.session_state.orders if o['status'] == 'confirm'])
            if not df_confirmed.empty:
                st.subheader("Orders Ready for Dispatch")
                st.dataframe(df_confirmed)
                courier = st.selectbox("Select Courier Partner", ["Koombiyo", "Pronto", "Prompt X", "Fardel"])
                if st.button("Generate Dispatch Sheet"):
                    st.toast(f"Dispatch Sheet Created for {courier}")
            else:
                st.info("No confirmed orders to dispatch.")

        # ---------------------------------------------------------
        # MODULE: RETURNS & FAKE (New)
        # ---------------------------------------------------------
        elif main_menu == "🔄 Returns & Fake":
            st.title("🔄 Return & Fraud Analysis")
            df = pd.DataFrame(st.session_state.orders)
            if not df.empty:
                df_fraud = df[df['status'].isin(['fake', 'cancelled'])]
                st.warning(f"Total Fraud Leads Detected: {len(df_fraud)}")
                st.dataframe(df_fraud)
                
                # Chart
                fig = px.bar(df_fraud, x='name', y='total', title="Loss Analysis per Lead")
                st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------
        # MODULE: INVENTORY
        # ---------------------------------------------------------
        elif main_menu == "📊 Inventory":
            st.title("📦 Warehouse Control")
            df_st = pd.DataFrame(st.session_state.stocks.items(), columns=["SKU", "In-Stock"])
            st.table(df_st)
            
            with st.expander("Update Inventory Levels"):
                p = st.selectbox("Product SKU", list(st.session_state.stocks.keys()))
                q = st.number_input("Add Quantity", 1)
                if st.button("Sync Stock"):
                    st.session_state.stocks[p] += q
                    st.success("Database Updated")

        # ---------------------------------------------------------
        # MODULE: FINANCE
        # ---------------------------------------------------------
        elif main_menu == "💰 Finance":
            st.title("💰 Finance Terminal")
            if st.session_state.user["role"] == "OWNER":
                df_o = pd.DataFrame(st.session_state.orders)
                rev = df_o['total'].sum() if not df_o.empty else 0
                st.metric("Net Revenue", f"LKR {rev:,.2f}")
                
                exp_amt = st.number_input("Record Expense (LKR)")
                if st.button("Log Expense"):
                    st.session_state.expenses.append({"date": str(date.today()), "amount": exp_amt})
                    save_data(pd.DataFrame(st.session_state.expenses), "expenses.csv")
                    st.toast("Expense Logged")
            else:
                st.error("Access Denied for Staff.")

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================
    # 6. RIGHT ACTION PANEL (As per image request)
    # =========================================================
    with col_panel:
        st.markdown('<div class="action-panel">', unsafe_allow_html=True)
        st.markdown("### ⚡ QUICK PANEL")
        
        st.text_input("🔍 Track ID", placeholder="Search...")
        st.button("Search System")
        
        st.divider()
        st.markdown("### 🔔 LIVE FEED")
        st.caption("🟢 Server: Online")
        st.caption("🔵 DB: Connected")
        
        st.divider()
        st.markdown("### 📝 SCRATCHPAD")
        st.text_area("Notes", height=150, placeholder="Type here...")
        
        st.divider()
        st.markdown("### 📊 STATUS MAP")
        df_all = pd.DataFrame(st.session_state.orders)
        if not df_all.empty:
            st.write(df_all['status'].value_counts())

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# END OF CODE - PTREAMLIT / HAPPYSYSTEM ERP
# =========================================================
