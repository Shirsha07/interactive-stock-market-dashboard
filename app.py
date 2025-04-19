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
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

# Fetch & process data
@st.cache_data
def fetch_data(symbol, period="1y"):
    df = yf.download(symbol + ".NS", period=period, progress=False)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    try:
        close = df["Close"]

        # Indicators
        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["MACD"] = MACD(close=close).macd_diff()
        df["RSI"] = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()

        # Drop rows with NaNs
        df.dropna(subset=["Close", "BB_upper"], inplace=True)

        # Align & compare
        close_aligned, bb_upper_aligned = df["Close"].align(df["BB_upper"], join="inner")
        df = df.loc[close_aligned.index]
        df["Touching_Upper_Band"] = close_aligned >= bb_upper_aligned

        return df

    except Exception as e:
        st.error(f"Error calculating indicators for {symbol}: {e}")
        return pd.DataFrame()

data = fetch_data(stock, period=timeframe)

if not data.empty:
    st.subheader(f"📊 Indicators for {stock.upper()}")
    st.line_chart(data[["Close", "EMA20", "BB_upper", "BB_lower"]])

    st.subheader("📌 Filtered Signals")
    filtered = data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Touching_Upper_Band"]) &
        (data["Close"] > data["EMA20"])
    ]
    st.write(f"✅ {len(filtered)} signal(s) matched the criteria.")
    st.dataframe(filtered.tail(10), use_container_width=True)

    # Optional: candlestick chart
    st.subheader("📉 Candlestick Chart")
    required_cols = ["Open", "High", "Low", "Close"]
    if all(col in data.columns for col in required_cols):
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Candlestick chart not shown. 'Open/High/Low/Close' data not available.")
else:
    st.warning("No data available. Please check the symbol or try a different one.")


