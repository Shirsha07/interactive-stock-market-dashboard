import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar for stock selection
st.sidebar.header("🔍 Stock Selector")
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["today", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# Function to fetch and clean data
@st.cache_data
def fetch_stock_data(symbol, period):
    symbol = symbol.upper() + ".NS"
    
    if period == "today":
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
    else:
        data = yf.download(symbol, period=period, progress=False)

    if data.empty:
        return pd.DataFrame()

    data.reset_index(inplace=True)
    data.set_index("Datetime" if "Datetime" in data.columns else "Date", inplace=True)

    return data

# Function to calculate indicators
def calculate_indicators(df):
    try:
        close = df["Close"]

        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["MACD"] = MACD(close=close).macd_diff()
        df["RSI"] = RSIIndicator(close=close).rsi()

        bb = BollingerBands(close=close)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()
        df["Touching_Upper_Band"] = df["Close"] >= df["BB_upper"]

        return df.dropna()

    except Exception as e:
        st.error(f"❌ Error calculating indicators for {stock.upper()}: {e}")
        return pd.DataFrame()

# Fetch data
df = fetch_stock_data(stock, timeframe)

if not df.empty:
    st.subheader(f"📊 Data for {stock.upper()}.NS:")
    st.dataframe(df.tail(), use_container_width=True)

    df = calculate_indicators(df)

    if not df.empty:
        st.subheader("📌 Filtered Signals Based on Strategy")
        signals = df[
            (df["MACD"] > 0) &
            (df["RSI"] > 50) &
            (df["Touching_Upper_Band"]) &
            (df["Close"] > df["EMA20"])
        ]

        if not signals.empty:
            st.success(f"✅ {len(signals)} signal(s) matched the criteria.")
            st.dataframe(signals.tail(), use_container_width=True)
        else:
            st.info("ℹ️ No signals matched the criteria.")

        st.subheader("📉 Candlestick Chart with Indicators")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        )])
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], mode="lines", name="BB Upper", line=dict(color="green")))
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], mode="lines", name="BB Lower", line=dict(color="red")))

        fig.update_layout(xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ No data available. Please check the symbol or try a different one.")













