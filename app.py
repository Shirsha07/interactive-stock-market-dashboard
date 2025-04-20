import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objs as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import base64

st.set_page_config(page_title="📈 Interactive Stock Market Dashboard", layout="wide")
st.title("📈 Interactive Stock Market Dashboard")

# Load Nifty 200 symbols from Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/1fiuz2q9ur6SVwWOrBxgk1ejCgEdEwCnLNBfHd1Ku7U0/edit#gid=0"
csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
nifty200_df = pd.read_csv(csv_url)
nifty200_symbols = nifty200_df['Symbol'].dropna().astype(str).str.strip().tolist()

# Timeframe mapping
timeframes = {
    "Today": ("1d", "5m"),
    "5 Minutes": ("1d", "5m"),
    "1 Day": ("5d", "15m"),
    "1 Week": ("1mo", "1h"),
    "1 Month": ("2mo", "1d"),
    "3 Months": ("3mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "5 Years": ("5y", "1wk")
}

# Sidebar filters
timeframe = st.selectbox("Select Timeframe", list(timeframes.keys()))
period, interval = timeframes[timeframe]

selected_symbols = st.multiselect(
    "Enter Stock Symbols (e.g., INFY.NS, TCS.NS)",
    nifty200_symbols
)

# Function to fetch and calculate indicators
def get_stock_data(symbol):
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    if data.empty:
        return None
    data['Close'] = data['Close'].astype(float)
    data['EMA20'] = EMAIndicator(close=data['Close'].squeeze(), window=20).ema_indicator()
    data['MACD'] = MACD(close=data['Close'].squeeze()).macd()
    data['RSI'] = RSIIndicator(close=data['Close'].squeeze()).rsi()
    bb = BollingerBands(close=data['Close'].squeeze(), window=20, window_dev=2)
    data['bb_upper'] = bb.bollinger_hband()
    data['bb_lower'] = bb.bollinger_lband()
    return data

# Section 1: Upward Trend Stocks (Improved Logic)
st.subheader("📊 Stocks in Upward Trend")
if st.button("🔼 Show Stocks in Upward Trend"):
    upward_trend = []
    with st.spinner("Scanning Nifty 200 stocks for upward trends..."):
        for symbol in nifty200_symbols:
            data = get_stock_data(symbol)
            if data is None or len(data) < 20:
                continue
            latest = data.iloc[-1]

            if pd.isna(latest['MACD']) or pd.isna(latest['RSI']) or pd.isna(latest['EMA20']) or pd.isna(latest['bb_upper']):
                continue

            if (
                latest['MACD'] > 0 and
                latest['RSI'] > 50 and
                latest['Close'] >= 0.98 * latest['bb_upper'] and
                latest['Close'] > latest['EMA20']
            ):
                upward_trend.append(symbol)

    if upward_trend:
        st.success("Stocks currently in upward trend:")
        st.write(upward_trend)
    else:
        st.warning("No stocks currently meet all the upward trend criteria.")

# Section 2: Candlestick Chart and Stock Details
st.subheader("📉 Candlestick Chart with Indicators")
selected_chart_stock = st.selectbox("Select a stock to visualize", selected_symbols)

if selected_chart_stock:
    data = get_stock_data(selected_chart_stock)
    if data is not None:
        # Candlestick with indicators
        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Candlestick'
            ),
            go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='blue'), name='EMA20'),
            go.Scatter(x=data.index, y=data['bb_upper'], line=dict(color='red', dash='dot'), name='Upper BB'),
            go.Scatter(x=data.index, y=data['bb_lower'], line=dict(color='green', dash='dot'), name='Lower BB')
        ])
        fig.update_layout(title=f"Candlestick Chart for {selected_chart_stock}", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

        # Stock detail table
        latest = data.iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else latest['Close']
        st.subheader("📄 Stock Details")
        info_table = pd.DataFrame({
            "Metric": ["Current Price", "Yesterday's Close", "Change", "Change %", "52 Week High", "52 Week Low"],
            "Value": [
                round(latest['Close'], 2),
                round(prev_close, 2),
                round(latest['Close'] - prev_close, 2),
                round((latest['Close'] - prev_close) / prev_close * 100, 2),
                round(data['High'].max(), 2),
                round(data['Low'].min(), 2)
            ]
        })
        st.table(info_table)

# Section 3: Upload Dashboard Reports
st.subheader("📂 Upload Your Dashboard Reports")
uploaded_file = st.file_uploader("Upload CSV/XLSX report or paste Google Sheet/Looker URL below", type=["csv", "xlsx"])
sheet_url = st.text_input("Or paste public Google Sheet/Looker dashboard URL")

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            uploaded_data = pd.read_csv(uploaded_file)
        else:
            uploaded_data = pd.read_excel(uploaded_file)
        st.dataframe(uploaded_data.head())
    except Exception as e:
        st.error(f"Failed to load file: {e}")
elif sheet_url:
    try:
        if "docs.google.com" in sheet_url:
            csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
            sheet_data = pd.read_csv(csv_url)
            st.dataframe(sheet_data.head())
        else:
            st.warning("Only Google Sheets are currently supported.")
    except Exception as e:
        st.error(f"Failed to load data from URL: {e}")

# Footer
st.caption("Developed with ❤️ using Streamlit")





