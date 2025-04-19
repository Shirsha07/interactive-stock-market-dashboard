import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar for stock selection
st.sidebar.header("🔍 Stock Selector")
stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ["today", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# Determine interval based on timeframe
def get_interval(timeframe):
    if timeframe == "today":
        return "5m", "1d"
    return "1d", timeframe

interval, period = get_interval(timeframe)

@st.cache_data(show_spinner=True)
def fetch_data(symbol, period, interval):
    try:
        symbol = symbol.upper() + ".NS"
        df = yf.download(symbol, period=period, interval=interval, progress=False)

        if df.empty or "Close" not in df.columns:
            return pd.DataFrame()

        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)
        return df

    except Exception as e:
        st.error(f"❌ Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Fetch data
data = fetch_data(stock, period, interval)

if not data.empty:
    st.subheader(f"📊 Data for {stock.upper()} ({timeframe})")
    st.write(data.tail())

    # Calculate Indicators (make sure 'Close' is a Series)
    try:
        close = data["Close"]

        data["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        data["MACD"] = MACD(close=close).macd_diff()
        data["RSI"] = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        data["BB_upper"] = bb.bollinger_hband()
        data["BB_lower"] = bb.bollinger_lband()
        data["Touching_Upper_Band"] = data["Close"] >= data["BB_upper"]

        # Drop rows with NaNs after indicator calculation
        data.dropna(subset=["EMA20", "MACD", "RSI", "BB_upper", "BB_lower"], inplace=True)

        # Line chart of indicators
        st.subheader("📈 Price & Indicators")
        st.line_chart(data[["Close", "EMA20", "BB_upper", "BB_lower"]])

        # Filter signals
        st.subheader("📌 Filtered Signals")
        filtered = data[
            (data["MACD"] > 0) &
            (data["RSI"] > 50) &
            (data["Touching_Upper_Band"]) &
            (data["Close"] > data["EMA20"])
        ]

        st.success(f"✅ {len(filtered)} signal(s) matched the criteria.")
        st.dataframe(filtered.tail(10), use_container_width=True)

        # Candlestick chart with indicators
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

        # Export Chart
        st.subheader("📤 Export Chart")
        export_format = st.radio("Select Export Format", ("PNG", "HTML"))
        if export_format == "PNG":
            st.error("Exporting as PNG is not yet implemented. Please use HTML export for now.")
        elif export_format == "HTML":
            fig.write_html("stock_chart.html")
            with open("stock_chart.html", "r") as f:
                st.download_button(label="Download Chart as HTML", data=f, file_name="stock_chart.html", mime="text/html")

    except Exception as e:
        st.error(f"❌ Error calculating indicators for {stock.upper()}: {e}")

else:
    st.warning("⚠️ No data available. Please check the symbol or try a different one.")
















