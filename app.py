import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 Stock Market Visualizer", layout="wide")

st.sidebar.header("🔍 Stock Selector")
symbol = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "today"])

# Convert user-friendly 'today' to intraday-compatible format
if timeframe == "today":
    interval = "5m"
    start_date = datetime.now().replace(hour=9, minute=15)  # Market open
    end_date = datetime.now()
else:
    interval = "1d"
    start_date = None
    end_date = None

nse_symbol = symbol.upper() + ".NS"

def fetch_data(symbol, interval, start=None, end=None):
    try:
        if start and end:
            df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
        else:
            df = yf.download(symbol, period=timeframe, interval=interval, progress=False)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    try:
        df = df.copy()

        # EMA
        df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()

        # RSI
        df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()

        # MACD
        macd = MACD(close=df["Close"])
        df["MACD"] = macd.macd()

        # Bollinger Bands
        bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()

        return df
    except Exception as e:
        st.error(f"❌ Error calculating indicators for {symbol.upper()}: {e}")
        return pd.DataFrame()

# Fetch and calculate
data = fetch_data(nse_symbol, interval, start_date, end_date)
data = calculate_indicators(data)

if not data.empty:
    # Drop rows with NaNs in indicator columns to align data
    cols_to_check = ["EMA20", "RSI", "MACD", "BB_upper", "BB_lower"]
    data.dropna(subset=cols_to_check, inplace=True)

    # Calculate condition safely with aligned DataFrame
    data["Touching_Upper_Band"] = data["Close"] >= data["BB_upper"]
    filtered = data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Touching_Upper_Band"]) &
        (data["Close"] > data["EMA20"])
    ]

    st.markdown(f"## 📊 Stock Market Visualizer")
    st.markdown(f"### Data for {nse_symbol}:")

    st.dataframe(data[["Close", "High", "Low", "Open", "Volume"]].tail())

    # ✅ Interactive Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price")])

    # Add EMA and BB overlays
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20"))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_upper"], mode="lines", name="BB Upper", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_lower"], mode="lines", name="BB Lower", line=dict(dash='dot')))

    fig.update_layout(title=f"{symbol.upper()} - Price Chart with Indicators",
                      xaxis_title="Date", yaxis_title="Price",
                      xaxis_rangeslider_visible=False)

    st.plotly_chart(fig, use_container_width=True)

    # 📈 Show filtered stocks matching technical criteria
    if not filtered.empty:
        st.success("✅ Stocks matching Uptrend Conditions (MACD>0, RSI>50, BB Upper Touch, EMA20):")
        st.dataframe(filtered[["Close", "MACD", "RSI", "EMA20", "BB_upper"]].tail())
    else:
        st.warning("⚠️ No stocks currently matching the uptrend conditions.")
else:
    st.warning("⚠️ No data available. Please check the symbol or try a different timeframe.")

















