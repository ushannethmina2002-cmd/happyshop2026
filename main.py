import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import urllib.parse
from datetime import datetime

# --- 1. SET PAGE CONFIG & REMOVE ALL WATERMARKS ---
st.set_page_config(page_title="HappyShop Enterprise", page_icon="🛒", layout="centered")

# CSS මගින් Streamlit branding සියල්ල ඉවත් කිරීම සහ UI එක ඔයාගේ Screenshot එකට ගැලපීම
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            
            /* මුළු ඇප් එකම සුදු පාට කිරීම */
            .stApp { background-color: white; }
            
            /* Inputs සහ Labels කළු පාට කිරීම */
            label { color: #333 !important; font-weight: bold !important; }
            .stTextInput>div>div>input { background-color: #f0f2f6 !important; border-radius: 8px !important; }
            
            /* කහ පාට Title එක (Screenshot එකේ විදිහට) */
            .yellow-title {
                color: #f1c40f; 
                text-align: center; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 45px;
                font-weight: bold;
                line-height: 1.1;
                margin-bottom: 20px;
            }
            
            /* බටන් එකේ පෙනුම */
            .stButton>button {
                background-color: white;
                color: #444;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
                height: 45px;
            }
            
            /* Dashboard එකේ කාඩ් පෙනුම */
            .card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #f1c40f;
                margin-bottom: 10px;
                color: #333;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
class HappyShopDB:
    def __init__(self):
        self.conn = sqlite3.connect('happyshop_final_v5.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Orders Table
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            customer_name TEXT, phone TEXT, address TEXT, city TEXT, 
            item_name TEXT, selling_price REAL, cost_price REAL, 
            status TEXT, tracking_id TEXT, date TEXT)''')
        # Users Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, password TEXT, role TEXT)''')
        
        # Owner Account (Email: happyshop@gmail.com | Pass: VLG0005)
        h_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", ("happyshop@gmail.com", h_pass))
        self.conn.commit()

db = HappyShopDB()

# --- 3. LOGIN PAGE (EXACT MATCH TO YOUR SCREENSHOT) ---
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Shopping Cart Logo (Screenshot එකේ එකට සමාන එකක්)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1170/1170678.png", width=120)
    
    st.markdown("<div class='yellow-title'>HappyShop<br>Login</div>", unsafe_allow_html=True)
    
    email = st.text_input("Email", placeholder="Email")
    password = st.text_input("Password", type="password", placeholder="Password")
    
    if st.button("Login to Dashboard"):
        hp = hashlib.sha256(password.encode()).hexdigest()
        res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND password=?", (email, hp)).fetchone()
        if res:
            st.session_state.user = {"email": email, "role": res[0]}
            st.rerun()
        else:
            st.error("Invalid Credentials!")

# --- 4. OWNER & STAFF DASHBOARDS ---
def owner_panel():
    st.markdown("<h2 style='color:#333;'>👑 Owner Console</h2>", unsafe_allow_html=True)
    
    # Analytics
    df = pd.read_sql("SELECT * FROM orders", db.conn)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Leads", len(df))
    c2.metric("Confirmed", len(df[df['status']=='Confirmed']))
    
    delivered_df = df[df['status']=='Delivered']
    profit = (delivered_df['selling_price'] - delivered_df['cost_price']).sum()
    c3.metric("Net Profit", f"Rs.{profit:,.0f}")

    # Add Staff
    with st.expander("👤 Manage Staff Members"):
        s_email = st.text_input("New Staff Email")
        s_pass = st.text_input("New Staff Password")
        if st.button("Add Staff"):
            hp = hashlib.sha256(s_pass.encode()).hexdigest()
            db.conn.cursor().execute("INSERT INTO users VALUES (?,?,'STAFF')", (s_email, hp))
            db.conn.commit(); st.success("Staff added!")

    st.subheader("All Orders Data")
    st.dataframe(df, use_container_width=True)

def staff_panel():
    st.markdown("<h2 style='color:#333;'>🎧 Staff Processing</h2>", unsafe_allow_html=True)
    
    # Manual Order Entry
    with st.expander("➕ Add New Lead Manually"):
        with st.form("add_l"):
            n = st.text_input("Name")
            p = st.text_input("Phone")
            a = st.text_area("Address")
            c = st.text_input("City")
            item = st.text_input("Item Name")
            sp = st.number_input("Selling Price")
            cp = st.number_input("Cost Price")
            if st.form_submit_button("Save Lead"):
                db.conn.cursor().execute(
                    "INSERT INTO orders (customer_name, phone, address, city, item_name, selling_price, cost_price, status, date) VALUES (?,?,?,?,?,?,?,?,?)",
                    (n, p, a, c, item, sp, cp, 'New', datetime.now().strftime("%Y-%m-%d"))
                )
                db.conn.commit(); st.success("Saved!"); st.rerun()

    # New Leads Processing
    leads = pd.read_sql("SELECT * FROM orders WHERE status='New' ORDER BY id DESC", db.conn)
    for i, row in leads.iterrows():
        st.markdown(f"""<div class='card'>
            <b>#{row['id']} - {row['customer_name']}</b><br>
            📞 {row['phone']} | 📍 {row['city']}<br>
            📦 {row['item_name']} | Rs.{row['selling_price']}
        </div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        # WhatsApp Link
        wa_msg = f"Hello {row['customer_name']}, Your order for {row['item_name']} is received. Confirm?"
        wa_url = f"https://wa.me/{row['phone']}?text={urllib.parse.quote(wa_msg)}"
        col1.markdown(f"[<button style='width:100%; border-radius:5px;'>💬 WhatsApp</button>]({wa_url})", unsafe_allow_html=True)
        
        if col2.button(f"✅ Confirm", key=f"c_{row['id']}"):
            db.conn.cursor().execute("UPDATE orders SET status='Confirmed' WHERE id=?", (row['id'],))
            db.conn.commit(); st.rerun()

# --- 5. MAIN LOGIC ---
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    login_page()
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    if st.session_state.user['role'] == "OWNER":
        owner_panel()
    else:
        staff_panel()
