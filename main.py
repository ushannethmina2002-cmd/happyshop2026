import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px  # Analytics සඳහා

# --- 0. DATA PERSISTENCE (ස්ථීරව දත්ත තබා ගැනීම) ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename).to_dict('records')
    return []

# --- ලංකාවේ දිස්ත්‍රික්ක සහ නගර දත්ත ---
SL_DATA = {
    "Colombo": ["Colombo 1-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Malabe", "Battaramulla"],
    "Gampaha": ["Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Veyangoda"],
    "Kalutara": ["Kalutara", "Panadura", "Horana", "Beruwala", "Matugama"],
    "Kandy": ["Kandy", "Peradeniya", "Katugastota", "Gampola", "Nawalapitiya"],
    "Matale": ["Matale", "Dambulla", "Sigiriya"],
    "Nuwara Eliya": ["Nuwara Eliya", "Hatton", "Talawakele"],
    "Galle": ["Galle", "Hikkaduwa", "Ambalangoda", "Karapitiya"],
    "Matara": ["Matara", "Akuressa", "Weligama"],
    "Hambantota": ["Hambantota", "Tangalle", "Beliatta"],
    "Jaffna": ["Jaffna", "Chavakachcheri"],
    "Mannar": ["Mannar"],
    "Vavuniya": ["Vavuniya"],
    "Mullaitivu": ["Mullaitivu"],
    "Kilinochchi": ["Kilinochchi"],
    "Batticaloa": ["Batticaloa"],
    "Ampara": ["Ampara", "Kalmunai"],
    "Trincomalee": ["Trincomalee"],
    "Kurunegala": ["Kurunegala", "Kuliyapitiya", "Narammala", "Pannala"],
    "Puttalam": ["Puttalam", "Chilaw", "Marawila"],
    "Anuradhapura": ["Anuradhapura", "Eppawala", "Kekirawa"],
    "Polonnaruwa": ["Polonnaruwa"],
    "Badulla": ["Badulla", "Bandarawela", "Hali-Ela"],
    "Moneragala": ["Moneragala", "Wellawaya"],
    "Ratnapura": ["Ratnapura", "Embilipitiya", "Balangoda"],
    "Kegalle": ["Kegalle", "Mawanella", "Warakapola"]
}

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = load_data('orders.csv')

if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil [VGLS0005]": 100, "Crown 1": 50, "Kalkaya": 75}
        save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data('expenses.csv')

if 'grn_history' not in st.session_state:
    st.session_state.grn_history = load_data('grn.csv')

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. LOGIN SYSTEM ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pw == "happy123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- 4. CSS & PRINTING DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 12px; border-radius: 10px; text-align: center; min-width: 120px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-f { background: #343a40; } .bg-t { background: #007bff; }
    .val { font-size: 24px; display: block; }
    
    .ship-header { background-color: #1f2937; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #374151; }
    .status-tab { padding: 5px 15px; border-radius: 5px; font-weight: bold; font-size: 12px; margin-right: 5px; }

    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible !important; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; color: black !important; background: white !important; padding: 20px; }
        .bill-head { border-bottom: 2px solid black; padding-bottom: 10px; font-size: 24px; }
        .bc-box { border: 2px solid black; padding: 10px; font-size: 28px; text-align: center; margin: 10px 0; }
        .way-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .way-table td, .way-table th { border: 1px solid black; padding: 10px; font-size: 16px; text-align: left; color: black; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Order Menu", ["New Order", "View Lead", "Order Tracking", "Add Lead"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Shipping Menu", ["Shipping Dashboard", "Confirm Dispatch", "Dispatch & Print", "Shipped List"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD ---
if menu == "🏠 Dashboard":
    low_stock_items = [item for item, qty in st.session_state.stocks.items() if int(qty) < 10]
    if low_stock_items:
        st.error(f"⚠️ **Low Stock Alert:** {', '.join(low_stock_items)} are running low!")

    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-x">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-f">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-t">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Profit & Loss Overview")
    total_rev = sum([float(o['total']) for o in st.session_state.orders if o['status'] == 'shipped'])
    total_exp = sum([float(e['amount']) for e in st.session_state.expenses])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Shipped Revenue", f"LKR {total_rev:,.2f}")
    c2.metric("Total Expenses", f"LKR {total_exp:,.2f}")
    c3.metric("Net Profit", f"LKR {total_rev - total_exp:,.2f}")

    if st.session_state.orders:
        df_orders = pd.DataFrame(st.session_state.orders)
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.write("**Sales by District**")
            fig1 = px.pie(df_orders, names='dist', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with col_chart2:
            st.write("**Order Status Distribution**")
            fig2 = px.bar(df_orders, x='status', color='status')
            st.plotly_chart(fig2, use_container_width=True)

# --- 7. ORDERS ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        st.subheader(f"📝 Happy Shop - {sub}")
        with st.form("full_order", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                phone = st.text_input("Contact Number 1 *")
                addr = st.text_area("Address *")
                dist = st.selectbox("District", list(SL_DATA.keys()))
                city = st.selectbox("City", SL_DATA[dist])
            with c2:
                prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Sale Amount", value=2950.0)
                delivery = st.number_input("Delivery Charge", value=350.0)
                discount = st.number_input("Discount", value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto", "Royal Express"])
            
            if st.form_submit_button("🚀 SAVE ORDER"):
                oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                st.session_state.orders.append({
                    "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                    "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), "courier": courier, "printed": "No"
                })
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                st.success(f"Order {oid} Saved Successfully!")

    elif sub == "View Lead":
        st.subheader("📋 Lead List")
        search_q = st.text_input("🔍 Search by Name or Phone")
        filter_status = st.multiselect("Filter Status", ["pending", "confirm", "noanswer", "cancel", "fake"], default=["pending"])
        
        for idx, o in enumerate(st.session_state.orders):
            if (search_q.lower() in str(o['name']).lower() or search_q in str(o['phone'])) and (o['status'] in filter_status):
                with st.expander(f"{o['id']} - {o['name']} ({o['status'].upper()})"):
                    st.write(f"📞 {o['phone']} | 📍 {o['addr']}, {o['city']}, {o['dist']}")
                    cols = st.columns(5)
                    if cols[0].button("Confirm ✅", key=f"c{idx}"): 
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if cols[1].button("No Answer ☎", key=f"n{idx}"): 
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if cols[2].button("Cancel ❌", key=f"x{idx}"): 
                        st.session_state.orders[idx]['status'] = 'cancel'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if cols[3].button("Fake ⚠️", key=f"f{idx}"): 
                        st.session_state.orders[idx]['status'] = 'fake'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if cols[4].button("Delete 🗑️", key=f"d{idx}"): 
                        st.session_state.orders.pop(idx)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()

    elif sub == "Order Tracking":
        search = st.text_input("Search by Phone Number")
        if search:
            results = [o for o in st.session_state.orders if search in str(o['phone'])]
            if results: st.table(pd.DataFrame(results))
            else: st.warning("No records found.")

# --- 8. SHIPPED ITEMS (නව Shipping Dashboard එක සමඟ) ---
elif menu == "🚚 Shipped Items":
    if sub == "Shipping Dashboard":
        st.markdown('<div class="ship-header"><h3>🔍 Search orders for shipping</h3>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        f_user = c1.selectbox("User", ["Any", "Admin"])
        f_date = c2.selectbox("Date Range", ["Disable", "Today", "Last 7 Days"])
        f_courier = c3.selectbox("Courier", ["All", "Koombiyo", "Domex", "Pronto", "Royal Express"])
        f_drop = c4.selectbox("Dropshipper", ["Only Company Orders"])
        
        st.markdown('<button style="background-color: #059669; color: white; border: none; padding: 8px 20px; border-radius: 5px;">Search</button></div>', unsafe_allow_html=True)
        
        # දත්ත පෙරීම
        ready_orders = [o for o in st.session_state.orders if o['status'] in ['confirm', 'ready_print']]
        
        st.info(f"{len(ready_orders)} items have to ship | Total: 0")
        
        st.markdown("---")
        st.subheader(f"Ready to Ship List ({len(ready_orders)})")
        
        # පින්තූරයේ ඇති ආකාරයටම Status ටැබ් පෙන්වීම
        st.markdown("""
            <span class="status-tab" style="background-color: #ec4899;">HELD ORDERS</span>
            <span class="status-tab" style="background-color: #ef4444;">WRONG WAY</span>
            <span class="status-tab" style="background-color: #f59e0b;">RESET</span>
            <span class="status-tab" style="background-color: #10b981;">WEB ORDERS</span>
            <span class="status-tab" style="background-color: #3b82f6;">EXCHANGING</span>
        """, unsafe_allow_html=True)
        
        if ready_orders:
            df_ready = pd.DataFrame(ready_orders)
            # වගුව පෙන්වීමට අවශ්‍ය කොලම්ස් පමණක් තේරීම
            display_cols = ['date', 'id', 'prod', 'qty', 'price', 'name', 'addr', 'city', 'phone', 'status']
            st.dataframe(df_ready[display_cols], use_container_width=True)
        else:
            st.warning("No data available in table")

    elif sub == "Confirm Dispatch":
        st.subheader("✅ Confirm Orders for Dispatch")
        ready_to_confirm = [o for o in st.session_state.orders if o['status'] == 'confirm']
        if not ready_to_confirm:
            st.info("No orders waiting for dispatch confirmation.")
        else:
            for idx, o in enumerate(ready_to_confirm):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{o['id']}** - {o['name']} | {o['city']} | {o['prod']} (x{o['qty']})")
                if col2.button("Ready to Print", key=f"conf_{idx}"):
                    o['status'] = 'ready_print'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.rerun()

    elif sub == "Dispatch & Print":
        st.subheader("🖨️ Dispatch & Print Label")
        to_print = [o for o in st.session_state.orders if o['status'] == 'ready_print']
        if not to_print:
            st.info("No orders ready for printing.")
        for idx, ro in enumerate(to_print):
            st.markdown(f"""
            <div class="print-area">
                <div class="bill-head"><b>HAPPY SHOP (PVT) LTD</b><br>Order ID: {ro['id']}</div>
                <div class="bc-box">CODE: {ro['id']}</div>
                <table class="way-table">
                    <tr><th>Customer Details</th><th>Item & Total</th></tr>
                    <tr>
                        <td><b>{ro['name']}</b><br>{ro['addr']}<br>{ro['city']}, {ro['dist']}<br>Tel: {ro['phone']}</td>
                        <td>{ro['prod']} (x{ro['qty']})<br>Courier: {ro['courier']}<br><b>Total: LKR {float(ro['total']):.2f}</b></td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Print & Move to Shipped {ro['id']}", key=f"p_{idx}"):
                st.session_state.stocks[ro['prod']] -= int(ro['qty'])
                for o in st.session_state.orders: 
                    if o['id'] == ro['id']: 
                        o['status'] = 'shipped'
                        o['printed'] = 'Yes'
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.components.v1.html("<script>window.print(); setTimeout(()=>window.location.reload(), 2000);</script>")

    elif sub == "Shipped List":
        st.subheader("📦 Shipped Items List")
        shipped = [o for o in st.session_state.orders if o['status'] == 'shipped']
        if shipped:
            df_shipped = pd.DataFrame(shipped)
            st.dataframe(df_shipped)
            st.download_button("📥 Download Shipped List", df_shipped.to_csv(index=False).encode('utf-8'), "shipped_list.csv")
        else: st.info("No shipped items yet.")

# --- 9. GRN, EXPENSES & RETURNS (කිසිවක් ඉවත් කර නැත) ---
elif menu == "📦 GRN":
    if sub == "New GRN":
        with st.form("grn"):
            p = st.selectbox("Product", list(st.session_state.stocks.keys()))
            q = st.number_input("Received Qty", min_value=1)
            if st.form_submit_button("Add to Stock"):
                st.session_state.stocks[p] += q
                st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                save_data(pd.DataFrame(st.session_state.grn_history), 'grn.csv')
                st.success("Stock Updated!")
    else: 
        if st.session_state.grn_history: st.table(pd.DataFrame(st.session_state.grn_history))

elif menu == "💰 Expense":
    with st.form("exp"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["Marketing", "Packaging", "Courier Fee", "Salary", "Rent", "Utility"])
        amt = c2.number_input("Amount")
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
            save_data(pd.DataFrame(st.session_state.expenses), 'expenses.csv')
            st.success("Expense Logged!")
    if st.session_state.expenses: st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "🔄 Return":
    rid = st.text_input("Enter Order ID to Return (RTS)")
    if st.button("Confirm RTS"):
        for o in st.session_state.orders:
            if o['id'] == rid:
                o['status'] = 'returned'
                st.session_state.stocks[o['prod']] += int(o['qty'])
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.success(f"Stock for {rid} Added Back.")

elif menu == "📊 Stocks":
    st.subheader("📈 Inventory Status")
    df_s = pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Available Qty"])
    st.table(df_s)
    
    st.write("**Quick Adjustment**")
    adj_p = st.selectbox("Product to Adjust", list(st.session_state.stocks.keys()))
    adj_q = st.number_input("New Total Qty", value=int(st.session_state.stocks[adj_p]))
    if st.button("Update Stock"):
        st.session_state.stocks[adj_p] = adj_q
        save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
        st.success("Stock Adjusted!")
        st.rerun()

elif menu == "🛍️ Products":
    with st.form("p"):
        n = st.text_input("New Product Name")
        if st.form_submit_button("Add Product"):
            if n and n not in st.session_state.stocks:
                st.session_state.stocks[n] = 0
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.success(f"{n} Added!")
                st.rerun()
