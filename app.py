import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar input
st.sidebar.header("🔍 Stock Selector")
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

# Fetch data function
@st.cache_data
def fetch_data(symbol, period="1y"):
    df = yf.download(symbol + ".NS", period=period, progress=False)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    try:
        # Ensure 1D series
        close = df["Close"].squeeze()

        # Technical indicators
        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["MACD"] = MACD(close=close).macd_diff()
        df["RSI"] = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()

        df.dropna(subset=["Close", "BB_upper"], inplace=True)

        # Check if touching upper band
        df["Touching_Upper_Band"] = df["Close"] >= df["BB_upper"]

        return df

    except Exception as e:
        st.error(f"Error calculating indicators for {symbol}: {e}")
        return pd.DataFrame()

# Load and display data
data = fetch_data(stock, period=timeframe)

if not data.empty:
    st.subheader(f"📊 Indicators for {stock.upper()}")
    st.line_chart(data[["Close", "EMA20", "BB_upper", "BB_lower"]])

    st.subheader("📌 Filtered Signals (MACD > 0, RSI > 50, BB Touching Upper, EMA > 20)")
    filtered = data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Touching_Upper_Band"]) &
        (data["Close"] > data["EMA20"])
    ]
    st.success(f"✅ {len(filtered)} signal(s) matched the criteria.")
    st.dataframe(filtered.tail(10), use_container_width=True)

    # Candlestick chart
    st.subheader("📉 Interactive Candlestick Chart")
    required_cols = ["Open", "High", "Low", "Close"]
    if all(col in data.columns for col in required_cols):
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )])
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20"))
        fig.add_trace(go.Scatter(x=data.index, y=data["BB_upper"], mode="lines", name="BB Upper"))
        fig.add_trace(go.Scatter(x=data.index, y=data["BB_lower"], mode="lines", name="BB Lower"))
        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Candlestick chart not available — missing OHLC data.")
else:
    st.warning("No data available. Please check the symbol or try a different one.")

