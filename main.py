import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="SignalMaster Elite AI", layout="wide")

# UI එක පට්ට විදිහට ලස්සන කරන CSS කෝඩ් එක
st.markdown("""
    <style>
    /* මුළු ඇප් එකේ පසුබිම */
    .stApp {
        background: radial-gradient(circle, #1a1a2e 0%, #16213e 100%);
        color: #e94560;
    }
    /* කොටු වල පෙනුම (Metric Cards) */
    div[data-testid="stMetricValue"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e94560;
        box-shadow: 0px 4px 15px rgba(233, 69, 96, 0.3);
    }
    /* Header එක ලස්සන කිරීම */
    h1 {
        text-shadow: 2px 2px #0f3460;
        letter-spacing: 2px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Navigation
st.sidebar.markdown("### 🛡️ SignalMaster Elite")
menu = st.sidebar.radio("Main Menu", ["🚀 Dashboard", "📊 Advanced Analysis", "⚙️ My Profile"])

# --- 🚀 DASHBOARD (HOME SCREEN) ---
if menu == "🚀 Dashboard":
    st.markdown("<h1>SIGNALMASTER ELITE AI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # ට්‍රෙන්ඩ් එක පෙන්වන ලස්සන කාඩ්ස්
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔥 Top Gainer", "SOL-USD", "+12.5%")
    with col2:
        st.metric("💎 AI Confidence", "High", "94%")
    with col3:
        st.metric("🌐 Global Trend", "Bullish", "🚀")

    st.write("## 💹 Real-Time Market Watch")
    major_coins = ["BTC-USD", "ETH-USD", "ADA-USD", "XRP-USD"]
    
    for c in major_coins:
        price = yf.Ticker(c).history(period="1d")['Close'].iloc[-1]
        st.markdown(f"**{c}** : `${price:,.2f}`")
        st.progress(65 if price > 100 else 40) # පෙනුම සඳහා පාවිච්චි කරන ලස්සන බාර් එකක්

# --- 📊 ADVANCED ANALYSIS ---
elif menu == "📊 Advanced Analysis":
    st.subheader("📊 Deep Market Inspection")
    target = st.sidebar.selectbox("Select Asset", ["BTC-USD", "ETH-USD", "SOL-USD"])
    
    # Candlestick Chart with Neon Styling
    df = yf.download(target, period="1d", interval="15m")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#e94560")
    )
    st.plotly_chart(fig, use_container_width=True)

# --- ⚙️ MY PROFILE ---
elif menu == "⚙️ My Profile":
    st.title("👤 Trader Profile")
    st.info("Username: Ushan Nethmina | License: PRO Edition")
