import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objs as go

st.set_page_config(page_title="Interactive Stock Market Dashboard", layout="wide")
st.title("📈 Interactive Stock Market Dashboard")

# --- Load Nifty 200 symbols ---
@st.cache_data
def load_nifty200_symbols():
    df = pd.read_csv("nifty200.csv")
    return df["Symbol"].dropna().tolist()

nifty200_symbols = load_nifty200_symbols()

# --- Timeframe options ---
timeframe_map = {
    "Today": "1d",
    "5 Minutes": "5m",
    "1 Day": "1d",
    "1 Week": "1wk",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y"
}

timeframe = st.selectbox("Select Timeframe", options=list(timeframe_map.keys()), index=4)
interval = timeframe_map[timeframe]

selected_symbols = st.multiselect(
    "Enter Stock Symbols (e.g., INFY.NS, TCS.NS)",
    options=nifty200_symbols
)

# --- Upward Trend Section ---
st.subheader("🚀 Stocks in Upward Trend")

def analyze_stock(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    if df.empty or len(df) < 30:
        return None

    df.dropna(inplace=True)
    df["EMA"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    boll = BollingerBands(df["Close"], window=20)
    df["bb_high"] = boll.bollinger_hband()

    last = df.iloc[-1]

    if (
        last["MACD"] > 0 and
        last["RSI"] > 50 and
        last["Close"] >= last["bb_high"] and
        last["Close"] > last["EMA"]
    ):
        return {
            "Symbol": symbol,
            "Current Price": round(last["Close"], 2),
            "Yesterday Close": round(df.iloc[-2]["Close"], 2),
            "Change": round(last["Close"] - df.iloc[-2]["Close"], 2),
            "Change %": round((last["Close"] - df.iloc[-2]["Close"]) / df.iloc[-2]["Close"] * 100, 2),
            "52W High": round(df["High"].max(), 2),
            "52W Low": round(df["Low"].min(), 2)
        }
    return None

if selected_symbols:
    upward_stocks = []
    for symbol in selected_symbols:
        stock_info = analyze_stock(symbol)
        if stock_info:
            upward_stocks.append(stock_info)

    if upward_stocks:
        st.dataframe(pd.DataFrame(upward_stocks))
    else:
        st.info("No stocks are currently in an upward trend.")

# --- Candlestick Chart ---
st.subheader("📉 Candlestick Chart with Indicators")
selected_chart_symbol = st.selectbox("Select a stock to visualize", selected_symbols)

if selected_chart_symbol:
    df = yf.download(selected_chart_symbol, period="6mo", interval=interval)
    df.dropna(inplace=True)
    df["EMA"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
    boll = BollingerBands(df["Close"], window=20)
    df["bb_high"] = boll.bollinger_hband()
    df["bb_low"] = boll.bollinger_lband()

    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick"
        ),
        go.Scatter(x=df.index, y=df["EMA"], line=dict(color='blue'), name="EMA"),
        go.Scatter(x=df.index, y=df["bb_high"], line=dict(color='green', dash='dot'), name="Upper BB"),
        go.Scatter(x=df.index, y=df["bb_low"], line=dict(color='red', dash='dot'), name="Lower BB"),
    ])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- Upload Looker/Google Sheet/CSV ---
st.subheader("📂 Upload Your Dashboard Reports")
uploaded_file = st.file_uploader("Upload CSV/XLSX report or paste Google Sheet/Looker URL below", type=["csv", "xlsx"])

dashboard_url = st.text_input("Or paste public Google Sheet/Looker dashboard URL")

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df_uploaded = pd.read_csv(uploaded_file)
    else:
        df_uploaded = pd.read_excel(uploaded_file)
    st.write("Uploaded Report Preview:")
    st.dataframe(df_uploaded.head())

elif dashboard_url:
    try:
        sheet_url = dashboard_url.replace("/edit#gid=", "/export?format=csv&gid=")
        df_uploaded = pd.read_csv(sheet_url)
        st.write("Embedded Report Preview:")
        st.dataframe(df_uploaded.head())
    except Exception as e:
        st.error(f"Failed to load dashboard from URL: {e}")


