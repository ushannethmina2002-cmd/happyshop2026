import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
import plotly.express as px

# ==========================================
# 1. පද්ධති සැකසුම් & Database Connection
# ==========================================
st.set_page_config(page_title="HappyShop Ultimate ERP", layout="wide")

# Database එක සාදා ගැනීම (ඔබේ SQL ව්‍යුහය මෙහි ඇත)
conn = sqlite3.connect('shop_system.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, role TEXT)''')
    # Products Table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, description TEXT, 
                  min_price REAL, max_price REAL, stock INTEGER, image TEXT)''')
    # Orders Table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, status TEXT, 
                  amount REAL, district TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

# Password Hashing සඳහා සරල ශ්‍රිතයක්
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# ==========================================
# 2. UI Styling
# ==========================================
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Authentication Logic (Login/Register)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Login to Shop System")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type='password', key="login_pass")
            if st.button("Login"):
                hashed_pswd = make_hashes(password)
                c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_pswd))
                data = c.fetchone()
                if data:
                    st.session_state.logged_in = True
                    st.session_state.user_info = data
                    st.success(f"Welcome back {data[1]}!")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password")

        with tab2:
            st.subheader("Create New Account")
            new_user = st.text_input("Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type='password')
            if st.button("Sign Up"):
                c.execute('INSERT INTO users(name, email, password, role) VALUES (?,?,?,?)', 
                          (new_user, new_email, make_hashes(new_password), "user"))
                conn.commit()
                st.success("Account created! Please Login.")

# ==========================================
# 4. Main Application (Logged In)
# ==========================================
else:
    # Sidebar Navigation
    with st.sidebar:
        st.title(f"👋 {st.session_state.user_info[1]}")
        st.write(f"Role: {st.session_state.user_info[4]}")
        st.divider()
        
        menu = ["📊 Dashboard", "📦 Products", "📝 New Order", "⚙️ Menu Manager", "🚪 Logout"]
        choice = st.radio("MAIN MENU", menu)
        
        if choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD (Chart.js logic converted to Plotly) ---
    if choice == "📊 Dashboard":
        st.title("Business Analytics")
        
        # SQL Query for totals (ඔබේ Node.js එකේ තිබූ query එක)
        c.execute('''SELECT COUNT(*) as total, SUM(amount) as revenue, 
                     SUM(CASE WHEN status='confirmed' THEN 1 ELSE 0 END) as confirmed 
                     FROM orders''')
        stats = c.fetchone()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", stats[0] if stats[0] else 0)
        col2.metric("Total Revenue", f"LKR {stats[1]:,.2f}" if stats[1] else "LKR 0.00")
        col3.metric("Confirmed Orders", stats[2] if stats[2] else 0)

        # Visual Chart
        if stats[0] and stats[0] > 0:
            df_chart = pd.DataFrame({
                'Status': ['Total Orders', 'Confirmed'],
                'Count': [stats[0], stats[2]]
            })
            fig = px.bar(df_chart, x='Status', y='Count', color='Status', title="Order Summary")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for charts yet.")

    # --- PRODUCTS (Add & View) ---
    elif choice == "📦 Products":
        st.title("Product Management")
        
        with st.expander("➕ Add New Product"):
            with st.form("prod_form"):
                p_name = st.text_input("Product Name")
                p_code = st.text_input("Product Code")
                p_desc = st.text_area("Description")
                p_min = st.number_input("Min Price", min_value=0.0)
                p_max = st.number_input("Max Price", min_value=0.0)
                p_stock = st.number_input("Initial Stock", min_value=0)
                if st.form_submit_button("Save Product"):
                    c.execute('''INSERT INTO products(name, code, description, min_price, max_price, stock) 
                                 VALUES (?,?,?,?,?,?)''', (p_name, p_code, p_desc, p_min, p_max, p_stock))
                    conn.commit()
                    st.success("Product added successfully!")

        st.subheader("Current Stock")
        products_df = pd.read_sql_query("SELECT id, name, code, max_price as Price, stock FROM products", conn)
        st.dataframe(products_df, use_container_width=True)

    # --- NEW ORDER ---
    elif choice == "📝 New Order":
        st.title("Create New Order")
        
        # පද්ධතියේ ඇති නිෂ්පාදන ලැයිස්තුව ලබා ගැනීම
        products = pd.read_sql_query("SELECT id, name, max_price FROM products WHERE stock > 0", conn)
        
        if not products.empty:
            with st.form("order_form"):
                selected_prod_name = st.selectbox("Select Product", products['name'])
                district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
                qty = st.number_input("Quantity", min_value=1, value=1)
                status = st.selectbox("Status", ["pending", "confirmed"])
                
                # මිල ගණනය කිරීම
                price = products[products['name'] == selected_prod_name]['max_price'].values[0]
                total_amount = price * qty
                
                st.info(f"Total Amount: LKR {total_amount:,.2f}")
                
                if st.form_submit_button("Place Order"):
                    # Insert Order
                    c.execute('''INSERT INTO orders(user_id, status, amount, district) 
                                 VALUES (?,?,?,?)''', (st.session_state.user_info[0], status, total_amount, district))
                    # Update Stock
                    c.execute('UPDATE products SET stock = stock - ? WHERE name = ?', (qty, selected_prod_name))
                    conn.commit()
                    st.success("Order placed successfully!")
        else:
            st.warning("No products in stock.")

    # --- MENU MANAGER ---
    elif choice == "⚙️ Menu Manager":
        st.title("System Menu Manager")
        st.info("මෙමගින් පද්ධතියේ මෙනු අයිතම පාලනය කළ හැක (Admin Only)")
        # මෙහිදී ඔබට මෙනු Table එකක් සාදා තවදුරටත් Edit කළ හැක.
        st.write("Current User ID:", st.session_state.user_info[0])
