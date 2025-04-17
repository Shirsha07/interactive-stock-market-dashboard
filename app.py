import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
from io import BytesIO

st.set_page_config(layout="wide", page_title="Stock Market Visualizer")

st.title("📈 Stock Market Visualizer")

# Load Nifty 200 symbols (or custom list from CSV)
@st.cache_data
def load_nifty200():
    url = "https://www1.nseindia.com/content/indices/ind_nifty200list.csv"
    df = pd.read_csv(url)
    return df["Symbol"].tolist()

nifty200_symbols = load_nifty200()

# Utility to fetch and calculate indicators
@st.cache_data(show_spinner=False)
def fetch_data(symbol, period="1y"):
    df = yf.download(symbol + ".NS", period=period)
    df.dropna(inplace=True)

    # Technical Indicators
    df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    macd = MACD(close=df["Close"])
    df["MACD"] = macd.macd_diff()
    df["RSI"] = RSIIndicator(close=df["Close"]).rsi()
    bollinger = BollingerBands(close=df["Close"])
    df["BB_upper"] = bollinger.bollinger_hband()
    df["BB_lower"] = bollinger.bollinger_lband()
    df["Touching_Upper_Band"] = df["Close"] >= df["BB_upper"]

    return df

# Section: Stock Trend Analysis
st.header("📊 Upward / Downward Trend Stock Analyzer")

upward = []
downward = []

for symbol in nifty200_symbols:
    try:
        df = fetch_data(symbol)
        latest = df.iloc[-1]

        if (latest["MACD"] > 0 and latest["RSI"] > 50 and
            latest["Touching_Upper_Band"] and latest["EMA20"] < latest["Close"]):
            upward.append(symbol)
        else:
            downward.append(symbol)
    except:
        continue

col1, col2 = st.columns(2)
with col1:
    st.subheader("🟢 Stocks in Upward Trend")
    st.write(upward if upward else "No stocks found matching upward trend criteria.")

with col2:
    st.subheader("🔴 Stocks in Downward Trend")
    st.write(downward if downward else "No stocks found matching downward trend criteria.")

# Section: Interactive Chart
st.header("📉 Interactive Candlestick Chart")

stock = st.selectbox("Select Stock", nifty200_symbols)
timeframe = st.selectbox("Timeframe", ["3mo", "6mo", "1y", "2y"], index=2)

data = fetch_data(stock, period=timeframe)

fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Candlestick")])

fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='orange'), name='EMA20'))
fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], line=dict(color='blue', dash='dot'), name='BB Upper'))
fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], line=dict(color='blue', dash='dot'), name='BB Lower'))

st.plotly_chart(fig, use_container_width=True)

# Section: Upload Your Own Portfolio / Report
st.header("📂 Upload Your Own Dashboard/Portfolio")

uploaded_file = st.file_uploader("Upload Google Sheet (CSV), Excel or Dashboard CSV", type=['csv', 'xlsx'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.write("📁 Uploaded Data Preview:")
    st.dataframe(df)

# Section: Financial Ratios / Correlation Matrix
st.header("📈 Financial Ratios & Correlation")

symbols_corr = st.multiselect("Select stocks for correlation", nifty200_symbols[:50], default=nifty200_symbols[:5])
correlation_df = pd.DataFrame()

for sym in symbols_corr:
    try:
        df = fetch_data(sym)
        correlation_df[sym] = df["Close"]
    except:
        continue

if not correlation_df.empty:
    st.write("📊 Correlation Matrix")
    st.dataframe(correlation_df.corr())

# Section: Export Chart
st.header("📤 Export Chart")

export_format = st.selectbox("Choose export format", ["PNG", "HTML"])
btn = st.button("Export")

if btn:
    if export_format == "PNG":
        fig.write_image("chart.png")
        with open("chart.png", "rb") as f:
            st.download_button("Download PNG", f, file_name="chart.png")
    else:
        html_buf = BytesIO()
        fig.write_html(html_buf)
        st.download_button("Download HTML", html_buf, file_name="chart.html")

# Section: Save Configs
st.header("🛠️ Save & Share Configuration")

user_config = {
    "selected_stock": stock,
    "timeframe": timeframe,
    "upward": upward,
    "downward": downward
}
st.json(user_config)
