import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar
st.sidebar.header("🔍 Stock Selector")
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE").upper()
timeframe = st.sidebar.selectbox("Select Timeframe", ["today", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# Adjust period and interval based on selection
if timeframe == "today":
    period = "1d"
    interval = "5m"
else:
    period = timeframe
    interval = "1d"

# Fetch and process data
@st.cache_data
def fetch_data(symbol, period, interval):
    try:
        symbol += ".NS"
        df = yf.download(symbol, period=period, interval=interval, progress=False)

        if df.empty or "Close" not in df.columns:
            st.warning(f"⚠️ No data for {symbol}.")
            return pd.DataFrame()

        # Ensure Close is 1D Series
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        # Calculate indicators
        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["MACD"] = MACD(close=close).macd_diff()
        df["RSI"] = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()
        df["Touching_Upper_Band"] = df["Close"] >= df["BB_upper"]

        df.dropna(inplace=True)
        return df

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return pd.DataFrame()

# Load and display
data = fetch_data(stock, period, interval)

if not data.empty:
    st.subheader(f"📊 Indicators for {stock}")
    st.line_chart(data[["Close", "EMA20", "BB_upper", "BB_lower"]])

    st.subheader("📌 Filtered Signals")
    filtered = data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Touching_Upper_Band"]) &
        (data["Close"] > data["EMA20"])
    ]
    st.success(f"✅ {len(filtered)} signal(s) matched.")
    st.dataframe(filtered.tail(10), use_container_width=True)

    st.subheader("📉 Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], name="EMA20", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_upper"], name="BB Upper", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_lower"], name="BB Lower", line=dict(color="red")))
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📤 Export Chart")
    export_format = st.radio("Select Export Format", ("PNG", "HTML"))
    if export_format == "HTML":
        fig.write_html("stock_chart.html")
        with open("stock_chart.html", "r") as f:
            st.download_button("Download Chart as HTML", f, "stock_chart.html")
    else:
        st.error("PNG export not yet supported.")
else:
    st.warning("⚠️ No data found. Try a different symbol or timeframe.")














