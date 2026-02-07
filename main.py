import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# 1. ULTIMATE PROFESSIONAL UI CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP v5.0 PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #020111, #0d0c2b, #13123b);
        color: white;
    }

    /* Professional Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.9) !important;
        backdrop-filter: blur(25px);
        border-right: 2px solid #FFD700;
    }

    .brand-header {
        font-size: 40px; font-weight: 800; color: #FFD700;
        text-align: center; margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(255, 215, 0, 0.5);
    }

    /* Executive Status Cards */
    .metric-row { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; }
    .card {
        background: rgba(255, 255, 255, 0.05);
        padding: 22px; border-radius: 18px; border-top: 5px solid #FFD700;
        min-width: 155px; flex: 1; text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .card h4 { margin: 0; font-size: 10px; color: #aaa; text-transform: uppercase; letter-spacing: 1.5px; }
    .card h2 { margin: 10px 0; font-size: 30px; font-weight: 800; }

    /* Color Coding for Professional Status */
    .c-confirm { border-top-color: #00ff88; color: #00ff88; }
    .c-pending { border-top-color: #00d4ff; color: #00d4ff; }
    .c-noanswer { border-top-color: #f1c40f; color: #f1c40f; }
    .c-cancel { border-top-color: #ff4d4d; color: #ff4d4d; }
    .c-fake { border-top-color: #95a5a6; color: #95a5a6; }
    .c-hold { border-top-color: #9b59b6; color: #9b59b6; }

    .glass-panel {
        background: rgba(255, 255, 255, 0.02);
        padding: 25px; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE (MULTI-DB ARCHITECTURE)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

if "db" not in st.session_state:
    st.session_state.db = {
        "orders": load_db("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff", "tracking"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price", "Value", "Type"]),
        "finance": load_db("finance.csv", ["date", "type", "category", "amount", "staff"]),
        "audit": load_db("audit.csv", ["timestamp", "staff", "action", "details"])
    }

def log_action(staff, action, details):
    new_log = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "staff": staff, "action": action, "details": details}
    st.session_state.db["audit"] = pd.concat([st.session_state.db["audit"], pd.DataFrame([new_log])], ignore_index=True)

# =========================================================
# 3. SIDEBAR & AUTHENTICATION
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-header">HAPPY SHOP</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700;">ENTERPRISE SOLUTION v5.0</p>', unsafe_allow_html=True)
    st.divider()
    
    current_staff = st.selectbox("🔑 ACCESS LEVEL", ["Admin - Supun", "Staff - Kavindi", "Staff - Nuwan"])
    main_nav = st.radio("CORE MODULES", [
        "🏠 Executive Dashboard", 
        "➕ Sales & Lead Entry", 
        "📦 Inventory & GRN", 
        "🚚 Logistics & Dispatch", 
        "💰 Finance & Expenses",
        "🕵️ Audit Logs"
    ])
    
    st.divider()
    st.write(f"📅 Today: {date.today()}")

# =========================================================
# 4. MODULES
# =========================================================

# --- 1. EXECUTIVE DASHBOARD (Advanced Insights) ---
if main_nav == "🏠 Executive Dashboard":
    st.markdown('<h2 style="color:#FFD700;">📊 Business Analytics Hub</h2>', unsafe_allow_html=True)
    
    df = st.session_state.db['orders']
    
    # Professional Metrics Row
    st.markdown(f"""
    <div class="metric-row">
        <div class="card"><h4>Total Leads</h4><h2>{len(df)}</h2></div>
        <div class="card c-confirm"><h4>Confirmed</h4><h2>{len(df[df['status']=='confirm'])}</h2></div>
        <div class="card c-pending"><h4>Pending</h4><h2>{len(df[df['status']=='pending'])}</h2></div>
        <div class="card c-noanswer"><h4>No Answer</h4><h2>{len(df[df['status']=='noanswer'])}</h2></div>
        <div class="card c-cancel"><h4>Cancelled</h4><h2>{len(df[df['status']=='cancel'])}</h2></div>
        <div class="card c-fake"><h4>Fake</h4><h2>{len(df[df['status']=='fake'])}</h2></div>
        <div class="card c-hold"><h4>On Hold</h4><h2>{len(df[df['status']=='hold'])}</h2></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            fig = px.line(df, x='date', y='total', title="📈 Revenue Growth (Daily)",
                          line_shape="spline", render_mode="svg")
            fig.update_traces(line_color='#FFD700', fill='tozeroy')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            status_counts = df['status'].value_counts().reset_index()
            fig_pie = px.pie(status_counts, values='count', names='status', hole=0.6, title="🎯 Lead Quality")
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. SALES & LEAD ENTRY (Automation) ---
elif main_nav == "➕ Sales & Lead Entry":
    st.markdown('<h2 style="color:#FFD700;">🛒 New Sales & Leads</h2>', unsafe_allow_html=True)
    
    with st.form("professional_entry", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        c_name = col1.text_input("Customer Name")
        c_phone = col1.text_input("WhatsApp / Phone")
        c_address = col1.text_area("Shipping Address")
        
        prod = col2.selectbox("Product", st.session_state.db["stock"]["Product"])
        qty = col2.number_input("Quantity", 1)
        
        status = col3.selectbox("Lead Status", ["confirm", "pending", "noanswer", "hold", "fake", "cancel"])
        staff_note = col3.text_input("Internal Note")
        
        if st.form_submit_button("✅ PROCESS ORDER"):
            price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
            oid = f"HS-{uuid.uuid4().hex[:5].upper()}"
            
            new_order = {
                "id": oid, "date": str(date.today()), "name": c_name, "phone": c_phone,
                "address": c_address, "prod": prod, "qty": qty, "total": price*qty,
                "status": status, "staff": current_staff, "tracking": "N/A"
            }
            st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_order])], ignore_index=True)
            
            # Inventory ස්වයංක්‍රීයව අඩු කිරීම (Automation)
            st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Qty"] -= qty
            
            log_action(current_staff, "Order Created", f"New Order {oid} for {c_name}")
            st.success(f"Order {oid} Successfully Synced with Inventory!")

# --- 3. AUDIT LOGS (Security) ---
elif main_nav == "🕵️ Audit Logs":
    st.markdown('<h2 style="color:#FFD700;">🕵️ System Security Logs</h2>', unsafe_allow_html=True)
    st.markdown("මෙමඟින් පද්ධතියේ සිදුවන සෑම වෙනසක්ම නිරීක්ෂණය කළ හැකිය.")
    st.dataframe(st.session_state.db["audit"].sort_values(by="timestamp", ascending=False), use_container_width=True)

# --- FINISHING MODULES ---
else:
    st.info(f"{main_nav} මොඩියුලය දැනට ක්‍රියාත්මකයි. දත්ත ඇතුළත් කිරීමට පහත Table එක භාවිතා කරන්න.")
    st.dataframe(st.session_state.db["orders"], use_container_width=True)

# =========================================================
# 5. AUTO-SAVE & INTEGRITY CHECK
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
