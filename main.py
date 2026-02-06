import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Ultimate ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOADERS & SESSION STATE ---
districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]
cities = ["Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya", "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya", "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"]

if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = date.today()

# Daily Reset: හැමදාම උදේට සීරෝ (0) කිරීම
if st.session_state.last_reset_date != date.today():
    st.session_state.orders = []
    st.session_state.last_reset_date = date.today()

# --- 3. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 4. PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 12px; border-radius: 10px; text-align: center; min-width: 120px;
        color: white; font-weight: bold; font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; }
    
    /* Table Styling */
    .styled-table { width: 100%; border-collapse: collapse; font-size: 14px; background: #161b22; border-radius: 8px; overflow: hidden; }
    .styled-table th { background: #21262d; color: #ffa500; padding: 12px; text-align: left; }
    .styled-table td { padding: 12px; border-bottom: 1px solid #30363d; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "🧾 Orders", "📦 GRN", "📊 Stocks"])
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Actions", ["New Order", "View Lead", "Add Lead"])
    if st.button("🚪 Logout"): st.session_state.user = None; st.rerun()

# --- 6. TOP METRIC CARDS (එක පාරක් පමණක් පෙන්වයි) ---
if menu == "🏠 Dashboard" or sub_menu == "View Lead":
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL LEADS<span class="val">{get_count('total')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. PAGE CONTENT ---
if menu == "🏠 Dashboard":
    st.title("Business Summary")
    st.info(f"System Operational. Date: {date.today()}")

elif sub_menu in ["New Order", "Add Lead"]:
    st.subheader(f"📝 {sub_menu}")
    with st.form("order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Customer Name *")
        phone = c1.text_input("Contact Number *")
        addr = c1.text_area("Address")
        dist = c2.selectbox("District", sorted(districts))
        city = c2.selectbox("City", sorted(cities))
        amt = c2.number_input("Sale Amount", min_value=0.0)
        if st.form_submit_button("SAVE LEAD"):
            if name and phone:
                new_id = len(st.session_state.orders) + 1
                st.session_state.orders.append({
                    "id": new_id, "order_id": f"HS-{821384+new_id}", 
                    "customer": name, "phone": phone, "status": "pending"
                })
                st.success("Lead Saved!")
                st.rerun()

elif sub_menu == "View Lead":
    st.subheader("📋 Leads Management Table")
    
    if not st.session_state.orders:
        st.warning("No leads found for today.")
    else:
        # Table Header
        cols = st.columns([1, 2, 2, 1.5, 3])
        cols[0].write("**ID**")
        cols[1].write("**Customer**")
        cols[2].write("**Phone**")
        cols[3].write("**Status**")
        cols[4].write("**Actions**")
        st.divider()

        for idx, order in enumerate(st.session_state.orders):
            c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 1.5, 3])
            
            # පේළියේ දත්ත
            c1.write(order['order_id'])
            c2.write(order['customer'])
            c3.write(order['phone'])
            
            # Status Badge එක පාටත් එක්ක
            st_color = {"pending": "#6c757d", "confirm": "#28a745", "noanswer": "#ffc107", "cancel": "#dc3545", "fake": "#343a40"}
            c4.markdown(f'<span class="status-badge" style="background:{st_color[order["status"]]}; color:white;">{order["status"].upper()}</span>', unsafe_allow_html=True)
            
            # Action Buttons (මෙය එබූ සැනින් Python වල update වේ)
            btn_cols = c5.columns(4)
            if btn_cols[0].button("✔", key=f"conf_{idx}"):
                st.session_state.orders[idx]['status'] = "confirm"; st.rerun()
            if btn_cols[1].button("☎", key=f"noa_{idx}"):
                st.session_state.orders[idx]['status'] = "noanswer"; st.rerun()
            if btn_cols[2].button("✖", key=f"can_{idx}"):
                st.session_state.orders[idx]['status'] = "cancel"; st.rerun()
            if btn_cols[3].button("⚠", key=f"fak_{idx}"):
                st.session_state.orders[idx]['status'] = "fake"; st.rerun()
