import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="HappyShop ERP", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("shop_system.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        code TEXT,
        description TEXT,
        min_price REAL,
        max_price REAL,
        stock INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        qty INTEGER,
        status TEXT,
        amount REAL,
        district TEXT,
        created_at TEXT
    )""")
    conn.commit()

init_db()

# ================= SECURITY =================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ================= DEFAULT OWNER =================
def create_owner():
    email = "happyshop@gmail.com"
    password = make_hashes("happy123")
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if not c.fetchone():
        c.execute("INSERT INTO users(name,email,password,role) VALUES (?,?,?,?)",
                  ("HappyShop Owner", email, password, "owner"))
        conn.commit()

create_owner()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ================= LOGIN UI =================
def login_page():
    st.markdown("""
    <style>
    body {background:#0f172a;}
    .login-box {
        width:420px;
        margin:auto;
        margin-top:120px;
        padding:40px;
        background:#020617;
        border-radius:15px;
        animation: fadeIn 1.2s;
        color:white;
        box-shadow:0 0 40px rgba(0,0,0,0.8);
    }
    @keyframes fadeIn {
        from {opacity:0; transform:translateY(40px);}
        to {opacity:1; transform:translateY(0);}
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("## 🛒 HappyShop ERP")
    st.markdown("### Owner Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        hashed = make_hashes(password)
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed))
        user = c.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid Login")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= SIDEBAR =================
def sidebar():
    user = st.session_state.user
    st.sidebar.title("HappyShop ERP")
    st.sidebar.write("👤", user[1])
    st.sidebar.write("Role:", user[4])

    if user[4] == "owner":
        menu = ["Dashboard", "Products", "Orders", "Users", "Logout"]
    else:
        menu = ["Dashboard", "Products", "New Order", "Logout"]

    return st.sidebar.radio("MENU", menu)

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Business Dashboard")

    c.execute("""
    SELECT COUNT(*),
           SUM(amount),
           SUM(CASE WHEN status='confirmed' THEN 1 ELSE 0 END)
    FROM orders
    """)
    total, revenue, confirmed = c.fetchone()

    col1,col2,col3 = st.columns(3)
    col1.metric("Total Orders", total or 0)
    col2.metric("Revenue", f"LKR {revenue or 0:,.2f}")
    col3.metric("Confirmed Orders", confirmed or 0)

    if total:
        df = pd.DataFrame({
            "Status":["Total","Confirmed"],
            "Count":[total, confirmed]
        })
        fig = px.bar(df, x="Status", y="Count", color="Status")
        st.plotly_chart(fig, use_container_width=True)

# ================= PRODUCTS =================
def products_page():
    st.title("📦 Product Management")

    with st.expander("➕ Add Product"):
        with st.form("prod"):
            name = st.text_input("Name")
            code = st.text_input("Code")
            desc = st.text_area("Description")
            minp = st.number_input("Min Price",0.0)
            maxp = st.number_input("Max Price",0.0)
            stock = st.number_input("Stock",0)
            if st.form_submit_button("Save"):
                c.execute("""INSERT INTO products
                (name,code,description,min_price,max_price,stock)
                VALUES (?,?,?,?,?,?)""",
                (name,code,desc,minp,maxp,stock))
                conn.commit()
                st.success("Product Added")

    df = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(df, use_container_width=True)

# ================= NEW ORDER =================
def new_order():
    st.title("📝 New Order")

    products = pd.read_sql("SELECT * FROM products WHERE stock>0", conn)
    if products.empty:
        st.warning("No stock available")
        return

    with st.form("order"):
        prod = st.selectbox("Product", products['name'])
        qty = st.number_input("Quantity",1)
        district = st.selectbox("District",["Colombo","Gampaha","Kandy","Galle"])
        status = st.selectbox("Status",["pending","confirmed"])

        price = products[products['name']==prod]['max_price'].values[0]
        amount = price * qty
        st.info(f"Total: LKR {amount:,.2f}")

        if st.form_submit_button("Place Order"):
            pid = products[products['name']==prod]['id'].values[0]
            c.execute("""INSERT INTO orders
            (user_id,product_id,qty,status,amount,district,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (st.session_state.user[0], pid, qty, status,
             amount, district, str(datetime.now())))
            c.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty,pid))
            conn.commit()
            st.success("Order Placed")

# ================= USERS =================
def users_page():
    st.title("👥 Users (Owner Only)")
    df = pd.read_sql("SELECT id,name,email,role FROM users", conn)
    st.dataframe(df, use_container_width=True)

# ================= MAIN =================
if not st.session_state.logged_in:
    login_page()
else:
    choice = sidebar()

    if choice == "Dashboard":
        dashboard()
    elif choice == "Products":
        products_page()
    elif choice == "New Order":
        new_order()
    elif choice == "Orders":
        dashboard()
    elif choice == "Users":
        users_page()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()
