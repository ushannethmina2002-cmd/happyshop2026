import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# 1. UI පෙනුම සහ අයිතිය (Ownership)
st.set_page_config(page_title="SignalMaster Pro AI v3.0", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ SignalMaster Pro AI - v3.0")
st.caption("Developed by Ushan | Advanced Crypto Intelligence Engine")

# 2. Sidebar - Settings & Currencies
st.sidebar.header("📊 Market Settings")
coin = st.sidebar.selectbox("Select Asset", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "LTC-USD"])
timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"])
currency = st.sidebar.radio("Display Currency", ["USD", "LKR (Approx)"])

# 3. Data Processing
df = yf.download(coin, period="60d", interval=timeframe)

if not df.empty:
    # Technical Indicators (Technical Section)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    macd = ta.macd(df['Close'])
    df = df.join(macd)
    df.ta.bbands(length=20, append=True)
    
    # 4. AI Prediction Logic (AI Section)
    # සරල AI මොඩලයක් මගින් මීළඟ ට්‍රෙන්ඩ් එක අනුමාන කිරීම
    last_close = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    ema_200 = df['EMA_200'].iloc[-1]
    
    # 5. Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    price_val = last_close if currency == "USD" else last_close * 300 # Approx LKR
    col1.metric("Live Price", f"{'Rs.' if currency == 'LKR (Approx)' else '$'} {price_val:,.2f}")
    col2.metric("RSI Level", f"{last_rsi:.2f}")
    col3.metric("Trend", "BULLISH" if last_close > ema_200 else "BEARISH")
    col4.metric("Market Sentiment", "Fear" if last_rsi < 40 else "Greed" if last_rsi > 60 else "Neutral")

    # 6. Professional Trading Signals
    st.subheader("🎯 AI Trading Signal")
    if last_rsi < 35 and last_close > ema_200:
        st.success("💎 STRONG BUY: Dip detected in Uptrend. High probability trade!")
    elif last_rsi > 65:
        st.error("⚠️ SELL ALERT: Market is overextended. Watch for reversal.")
    else:
        st.warning("⚖️ WAIT: No clear entry. Patience is profit.")

    # 7. Candlestick Chart with Indicators
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price')])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], name='EMA 200', line=dict(color='yellow', width=1.5)))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 8. Extra Features (Calculator & News)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🧮 Profit Calculator")
        inv = st.number_input("Investment Amount ($)", value=100)
        lev = st.slider("Leverage", 1, 20, 1)
        st.write(f"Total Position Size: ${inv * lev}")
    
    with c2:
        st.subheader("📰 Market Insights")
        st.info(f"Analyzing {coin} on {timeframe} chart. {coin} shows {'high' if last_rsi > 50 else 'moderate'} buying pressure.")

else:
    st.error("දත්ත ලබා ගැනීමේ දෝෂයකි. කරුණාකර නැවත උත්සාහ කරන්න.")
