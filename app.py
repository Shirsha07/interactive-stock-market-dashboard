import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta

# Streamlit setup
st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar for user input
st.sidebar.header("🔍 Stock Selector")
symbol = st.sidebar.text_input("Enter NSE Symbol", "RELIANCE").upper()
timeframe = st.sidebar.selectbox("Select Timeframe", ["5d", "1mo", "3mo", "6mo", "1y", "today"])

# Map timeframe to yfinance parameters
def get_data_range(timeframe):
    if timeframe == "today":
        return {"period": "1d", "interval": "5m"}
    elif timeframe == "5d":
        return {"period": "5d", "interval": "15m"}
    elif timeframe == "1mo":
        return {"period": "1mo", "interval": "30m"}
    elif timeframe == "3mo":
        return {"period": "3mo", "interval": "1h"}
    elif timeframe == "6mo":
        return {"period": "6mo", "interval": "1d"}
    elif timeframe == "1y":
        return {"period": "1y", "interval": "1d"}
    else:
        return {"period": "6mo", "interval": "1d"}  # default

params = get_data_range(timeframe)

# Fetch stock data
@st.cache_data(ttl=3600)
def fetch_data(symbol, period, interval):
    ticker = yf.Ticker(symbol + ".NS")
    data = ticker.history(period=period, interval=interval)
    return data

data = fetch_data(symbol, params["period"], params["interval"])

# Calculate technical indicators
def calculate_indicators(df):
    try:
        df = df.copy()
        close = df["Close"]

        # Ensure close is strictly 1D
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()  # converts DataFrame to Series if shape (N, 1)

        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["RSI"] = RSIIndicator(close=close, window=14).rsi()
        df["MACD"] = MACD(close=close).macd()

        bb = BollingerBands(close=close, window=20, window_dev=2)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()

        return df
    except Exception as e:
        st.error(f"❌ Error calculating indicators for {symbol}: {e}")
        return pd.DataFrame()

if not data.empty:
    data = calculate_indicators(data)

    if not data.empty:
        st.subheader(f"Data for {symbol}.NS:")

        # Display recent OHLCV
        st.dataframe(
            data[["Open", "High", "Low", "Close", "Volume", "EMA20", "RSI", "MACD", "BB_upper", "BB_lower"]].tail(10),
            use_container_width=True
        )
    else:
        st.warning("⚠️ No data available after applying indicators.")
else:
    st.warning("⚠️ No data available. Please check the symbol or try a different one.")


















