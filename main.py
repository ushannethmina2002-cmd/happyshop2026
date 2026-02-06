import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests # Courier API එකට කනෙක්ට් වෙන්න
from datetime import datetime

# --- 1. WATERMARK REMOVAL & CUSTOM STYLING ---
st.set_page_config(page_title="HappyShop Enterprise CRM", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            /* 'Made with Streamlit' අයින් කිරීමට */
            footer:after {
                content:'Copyright © 2026 HappyShop Enterprise'; 
                visibility: visible;
                display: block;
                position: relative;
                padding: 5px;
                top: 2px;
                color: #555;
            }
            /* Custom Scrollbar for better UI */
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #1e212b;
            }
            ::-webkit-scrollbar-thumb {
                background: #ffcc00;
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #e0b300;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. ENGINE & DATA ARCHITECTURE ---
class HappyShopPro:
    def __init__(self):
        self.conn = sqlite3.connect('happyshop_enterprise_v5.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Leads & Delivery Table
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            customer_name TEXT, phone TEXT, address TEXT, city TEXT, 
            item_name TEXT, selling_price REAL, cost_price REAL, 
            status TEXT, tracking_id TEXT, staff_id TEXT, date TEXT)''')
        # User Management Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, password TEXT, role TEXT)''')
        
        # Super Admin (Owner) Account Seed
        owner_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", ("happyshop@gmail.com", owner_pass))
        self.conn.commit()

db = HappyShopPro()

# --- 3. COURIER API (ROYAL EXPRESS INTEGRATION) ---
# NOTE: Replace "YOUR_ROYAL_API_KEY" with your actual key once you obtain it.
# This function currently simulates the Royal Express API response.
def send_to_royal_express(order_data):
    api_url = "https://api.royalexpress.lk/v1/orders/create" # Royal Express API Endpoint
    headers = {"Authorization": "Bearer YOUR_ROYAL_API_KEY"}
    
    payload = {
        "recipient_name": order_data['customer_name'],
        "recipient_phone": order_data['phone'],
        "address": order_data['address'],
        "city": order_data['city'],
        "cod_amount": order_data['selling_price'],
        "item_description": order_data['item_name']
    }
    
    try:
        # response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        # response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        # return response.json()['tracking_number']
        
        # --- SIMULATION (API Key එක ලැබෙනකන් මේක වැඩ කරයි) ---
        import random
        return f"RE-{random.randint(100000, 999999)}" 
    except requests.exceptions.RequestException as e:
        st.error(f"Royal Express API Error: {e}")
        return None

# --- 4. CORE FUNCTIONS ---
def get_profit_stats():
    df = pd.read_sql("SELECT * FROM orders WHERE status='Delivered'", db.conn)
    if df.empty: return 0, 0, 0
    total_revenue = df['selling_price'].sum()
    total_cost = df['cost_price'].sum()
    total_profit = total_revenue - total_cost
    return total_revenue, total_cost, total_profit

def send_whatsapp_message(phone, message):
    phone = phone.replace("+", "").replace(" ", "")
    if phone.startswith("0"): phone = "94" + phone[1:]
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded_message}"

# --- 5. OWNER PANEL ---
def owner_view():
    st.markdown("<h1 style='color:#ffcc00; text-align:center;'>👑 HappyShop Enterprise: Owner Console</h1>", unsafe_allow_html=True)
    
    # Analytics Row
    rev, cost, profit = get_profit_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='stat-card'><h4>Total Revenue (Delivered)</h4><h2>Rs.{rev:,.0f}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='stat-card'><h4>Total Cost (Delivered)</h4><h2 style='color:#d73a49'>Rs.{cost:,.0f}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='stat-card'><h4>Net Profit (Delivered)</h4><h2 style='color:#238636'>Rs.{profit:,.0f}</h2></div>", unsafe_allow_html=True)
    
    pending_leads_count = pd.read_sql("SELECT count(*) FROM orders WHERE status='New'", db.conn).iloc[0,0]
    shipped_orders_count = pd.read_sql("SELECT count(*) FROM orders WHERE status='Shipped'", db.conn).iloc[0,0]
    
    c4.markdown(f"<div class='stat-card' style='border-left: 5px solid #ffcc00;'><h4>Pending Leads / Shipped</h4><h2>{pending_leads_count} / {shipped_orders_count}</h2></div>", unsafe_allow_html=True)

    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["👥 Staff Management", "📜 All Orders (History)", "➕ Add Order Manually"])
    with tab1:
        st.subheader("Add New Staff Member")
        with st.form("staff_reg"):
            s_em = st.text_input("Staff Email")
            s_pw = st.text_input("Temporary Password", type="password")
            if st.form_submit_button("Register Staff"):
                h_pw = hashlib.sha256(s_pw.encode()).hexdigest()
                try:
                    db.conn.cursor().execute("INSERT INTO users VALUES (?,?,'STAFF')", (s_em, h_pw))
                    db.conn.commit(); st.success("Staff member added successfully!")
                except sqlite3.IntegrityError: st.error("Email already exists for a user!")

    with t2:
        st.subheader("Complete Order History")
        all_orders_df = pd.read_sql("SELECT * FROM orders ORDER BY id DESC", db.conn)
        st.dataframe(all_orders_df, use_container_width=True)

    with t3:
        st.subheader("Manually Add New Lead / Order (for testing or direct orders)")
        with st.form("manual_order_entry"):
            mc1, mc2 = st.columns(2)
            m_name = mc1.text_input("Customer Name*")
            m_phone = mc2.text_input("Phone Number*")
            
            m_addr = st.text_area("Delivery Address*", height=70)
            m_city = st.text_input("City* (e.g., Colombo 01)")
            
            mi_name = st.text_input("Item Name*")
            ms_price = st.number_input("Selling Price (COD Amount)*", value=0.0, min_value=0.0)
            mc_price = st.number_input("Cost Price (for Profit Calculation)*", value=0.0, min_value=0.0)
            
            if st.form_submit_button("Submit New Order"):
                if not all([m_name, m_phone, m_addr, m_city, mi_name, ms_price, mc_price]):
                    st.error("Please fill in all required fields.")
                else:
                    db.conn.cursor().execute(
                        "INSERT INTO orders (customer_name, phone, address, city, item_name, selling_price, cost_price, status, date) VALUES (?,?,?,?,?,?,?,?,?)",
                        (m_name, m_phone, m_addr, m_city, mi_name, ms_price, mc_price, 'New', datetime.now().strftime("%Y-%m-%d"))
                    )
                    db.conn.commit(); st.success("New order added to 'New Leads' list!")

# --- 6. STAFF PANEL ---
def staff_view():
    st.markdown("<h1 style='color:#ffcc00; text-align:center;'>📦 Royal Express Dispatch & Processing Hub</h1>", unsafe_allow_html=True)
    
    # Section 1: New Leads to Confirm (from FB/Manual)
    st.subheader("🔔 New Leads to Confirm & Assign")
    new_leads_df = pd.read_sql("SELECT * FROM orders WHERE status='New' ORDER BY id DESC", db.conn)
    
    if new_leads_df.empty:
        st.info("No new leads to process. Great job, or wait for new leads from Facebook!")
    
    for i, row in new_leads_df.iterrows():
        with st.container():
            st.markdown(f"""<div class='order-card'>
                <b>ORDER #{row['id']}</b><br>
                Customer: <b>{row['customer_name']}</b> | Phone: <b>{row['phone']}</b><br>
                Item: {row['item_name']} | COD: Rs.{row['selling_price']}<br>
                Received: {row['date']}
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,1,2])
            # WhatsApp Button
            whatsapp_msg = f"Hello {row['customer_name']}, Your order for {row['item_name']} (Rs.{row['selling_price']}) is being processed by HappyShop. Please reply to confirm delivery details: {row['address']}, {row['city']}"
            c1.markdown(f"[<button style='background-color:#25D366;color:white;border:none;padding:8px 15px;border-radius:5px;cursor:pointer;'>WhatsApp</button>]({send_whatsapp_message(row['phone'], whatsapp_msg)})", unsafe_allow_html=True)
            
            if c2.button(f"✅ Confirm Order", key=f"conf_{row['id']}"):
                db.conn.cursor().execute(
                    "UPDATE orders SET status='Confirmed', staff_id=? WHERE id=?", 
                    (st.session_state.user['email'], row['id'])
                )
                db.conn.commit(); st.success("Order Confirmed! Now ready for Dispatch.")
                st.rerun()
            
            if c3.button(f"❌ Reject / Invalid Lead", key=f"rej_{row['id']}"):
                db.conn.cursor().execute("UPDATE orders SET status='Rejected' WHERE id=?", (row['id'],))
                db.conn.commit(); st.error("Lead Rejected.")
                st.rerun()
    
    st.divider()

    # Section 2: Confirmed Orders for Royal Express Dispatch
    st.subheader("🚀 Confirmed Orders Ready for Royal Express Dispatch")
    confirmed_for_dispatch_df = pd.read_sql("SELECT * FROM orders WHERE status='Confirmed' ORDER BY id DESC", db.conn)
    
    if confirmed_for_dispatch_df.empty:
        st.info("No confirmed orders waiting for Royal Express dispatch.")
    
    for i, row in confirmed_for_dispatch_df.iterrows():
        with st.container():
            st.markdown(f"""<div class='order-card' style='border-left: 5px solid #ffcc00;'>
                <b>ORDER #{row['id']}</b> - <b>{row['customer_name']}</b><br>
                📍 Delivery: {row['address']}, {row['city']} | 📞 {row['phone']}<br>
                📦 Item: {row['item_name']} | COD: Rs.{row['selling_price']}
            </div>""", unsafe_allow_html=True)
            
            if st.button(f"Generate Waybill & Dispatch via Royal Express", key=f"dispatch_{row['id']}"):
                order_data = {
                    "customer_name": row['customer_name'],
                    "phone": row['phone'],
                    "address": row['address'],
                    "city": row['city'],
                    "item_name": row['item_name'],
                    "selling_price": row['selling_price']
                }
                tracking_no = send_to_royal_express(order_data)
                
                if tracking_no:
                    db.conn.cursor().execute(
                        "UPDATE orders SET status='Shipped', tracking_id=?, staff_id=? WHERE id=?",
                        (tracking_no, st.session_state.user['email'], row['id'])
                    )
                    db.conn.commit()
                    st.success(f"Order #{row['id']} Dispatched! Tracking ID: {tracking_no}")
                    st.rerun()
                else:
                    st.error("Failed to dispatch to Royal Express. Please check API settings or try again.")

    st.divider()

    # Section 3: Shipped Orders (Tracking & Delivery Update)
    st.subheader("🚚 Shipped Orders - Update Delivery Status")
    shipped_df = pd.read_sql("SELECT * FROM orders WHERE status='Shipped' ORDER BY id DESC", db.conn)
    
    if shipped_df.empty:
        st.info("No orders currently in 'Shipped' status.")
    
    for i, row in shipped_df.iterrows():
        with st.container():
            st.markdown(f"""<div class='order-card' style='border-left: 5px solid #238636;'>
                <b>ORDER #{row['id']}</b> - <b>{row['customer_name']}</b><br>
                Tracking ID: <b>{row['tracking_id']}</b><br>
                Current Status: <b>{row['status']}</b> | Shipped Date: {row['date']}
            </div>""", unsafe_allow_html=True)
            
            col_u1, col_u2, col_u3 = st.columns(3)
            if col_u1.button(f"✅ Mark Delivered", key=f"delivered_{row['id']}"):
                db.conn.cursor().execute("UPDATE orders SET status='Delivered' WHERE id=?", (row['id'],))
                db.conn.commit(); st.success("Order marked as Delivered!")
                st.rerun()
            if col_u2.button(f"↩️ Mark Returned", key=f"returned_{row['id']}"):
                db.conn.cursor().execute("UPDATE orders SET status='Returned' WHERE id=?", (row['id'],))
                db.conn.commit(); st.warning("Order marked as Returned.")
                st.rerun()
            whatsapp_msg_delivered = f"Hello {row['customer_name']}, Your order #{row['id']} from HappyShop has been successfully delivered! Thank you for shopping with us."
            col_u3.markdown(f"[<button style='background-color:#25D366;color:white;border:none;padding:8px 15px;border-radius:5px;cursor:pointer;'>Notify WhatsApp</button>]({send_whatsapp_message(row['phone'], whatsapp_msg_delivered)})", unsafe_allow_html=True)

# --- 7. AUTHENTICATION FLOW ---
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6A3C2F98C0XF_CqMToO6_m-Fv0SjYw5Xpog&s", width=100) # Royal Express Style Logo
        st.markdown("<h1 style='text-align: center; color: #ffcc00;'>HappyShop Login</h1>", unsafe_allow_html=True)
        
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Login to Dashboard"):
            hashed_password = hashlib.sha256(password_input.encode()).hexdigest()
            user_data = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND password=?", (email_input, hashed_password)).fetchone()
            
            if user_data:
                st.session_state.user = {"email": email_input, "role": user_data[0]}
                st.rerun()
            else:
                st.error("Invalid Login Credentials. Please check your email and password.")
else:
    # Sidebar Logout Button
    with st.sidebar:
        st.header(f"Welcome, {st.session_state.user['role'].title()}")
        st.write(f"Logged in as: {st.session_state.user['email']}")
        if st.button("Logout", key="sidebar_logout"):
            st.session_state.user = None
            st.rerun()
    
    # Render view based on user role
    if st.session_state.user['role'] == "OWNER":
        owner_view()
    else:
        staff_view()
