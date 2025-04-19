import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar for stock selection
st.sidebar.header("🔍 Stock Selector")
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

# Function to fetch and process data
@st.cache_data
def fetch_data(symbol, period="1y"):
    try:
        symbol = symbol.upper() + ".NS"  # Ensure correct symbol format for NSE stocks
        st.write(f"Fetching data for: {symbol}")  # Debugging: Show symbol being fetched
        df = yf.download(symbol, period=period, progress=False)

        # Debugging: Check if the data was fetched correctly
        st.write(f"Data for {symbol}:")
        st.write(df.head())  # Display the first few rows to confirm data retrieval

        if df.empty or "Close" not in df.columns:
            st.warning(f"⚠️ No data available for {symbol}. Please check the symbol or try a different one.")
            return pd.DataFrame()

        # Ensure Close is strictly 1-dimensional (Series)
        close = pd.Series(df["Close"].values, index=df.index)

        # Calculate Indicators
        ema = EMAIndicator(close=close, window=20).ema_indicator()
        macd = MACD(close=close).macd_diff()
        rsi = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()

        # Add indicators to DataFrame
        df["EMA20"] = ema
        df["MACD"] = macd
        df["RSI"] = rsi
        df["BB_upper"] = bb_upper
        df["BB_lower"] = bb_lower

        # Drop rows with any NaNs
        df.dropna(subset=["EMA20", "MACD", "RSI", "BB_upper", "BB_lower"], inplace=True)

        # Boolean if price is touching upper band
        df["Touching_Upper_Band"] = df["Close"] >= df["BB_upper"]

        return df

    except Exception as e:
        st.error(f"❌ Error calculating indicators for {symbol}: {e}")
        return pd.DataFrame()

# Load data
data = fetch_data(stock, period=timeframe)

if not data.empty:
    # Display indicators
    st.subheader(f"📊 Indicators for {stock.upper()}")
    st.line_chart(data[["Close", "EMA20", "BB_upper", "BB_lower"]])

    # Filtered signals based on criteria
    st.subheader("📌 Filtered Signals")
    filtered = data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Touching_Upper_Band"]) &
        (data["Close"] > data["EMA20"])
    ]
    st.success(f"✅ {len(filtered)} signal(s) matched the criteria.")
    st.dataframe(filtered.tail(10), use_container_width=True)

    # Candlestick Chart with indicators
    st.subheader("📉 Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_upper"], mode="lines", name="BB Upper", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_lower"], mode="lines", name="BB Lower", line=dict(color="red")))
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ No data available. Please check the symbol or try a different one.")








