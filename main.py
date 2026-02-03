import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="SignalMaster AI", layout="centered")
st.title("🎯 SignalMaster AI Bot")

# කාසි වර්ග තෝරන්න
coin = st.selectbox("Select Crypto", ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "XRP-USD"])

if st.button('Analyze Market'):
    with st.spinner('Checking Market Data...'):
        # දත්ත ලබා ගැනීම
        df = yf.download(coin, period="1d", interval="15m")
        
        if not df.empty:
            # RSI ගණනය කිරීම
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # අන්තිම අගයන් ලබා ගැනීම
            price = float(df['Close'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1])
            
            # පෙන්වන ආකාරය (මෙතන තමයි කලින් වැරදුණේ)
            st.metric(label="Current Price", value=f"${price:,.2f}")
            st.write(f"Market RSI: {rsi:.2f}")

            if rsi < 35:
                st.success("🚀 BUY SIGNAL: Market is Oversold!")
            elif rsi > 65:
                st.error("⚠️ SELL SIGNAL: Market is Overbought!")
            else:
                st.info("⚖️ Neutral: No clear signal yet.")
        else:
            st.warning("දත්ත ලබා ගැනීමට නොහැකි විය. නැවත උත්සාහ කරන්න.")
