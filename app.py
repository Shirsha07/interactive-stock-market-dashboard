import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from utils import (
    calculate_indicators, filter_nifty200_stocks,
    plot_candlestick, plot_returns,
    load_uploaded_file
)

st.set_page_config(layout="wide", page_title="Interactive Stock Market Dashboard")
st.title("Interactive Stock Market Dashboard")

st.sidebar.header("Options")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
ma_days = st.sidebar.multiselect("Select Moving Averages (days)", [20, 50, 100], [20, 50])

st.sidebar.subheader("Portfolio Analysis")
uploaded_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)", type=["csv", "xlsx"])

# Fetch and display stock data
data = yf.download(ticker, start=start_date, end=end_date)
data = calculate_indicators(data)
st.subheader(f"Stock Data for {ticker}")
st.dataframe(data.tail())

# Candlestick Chart
st.subheader("Candlestick Chart")
st.plotly_chart(plot_candlestick(data, ticker, ma_days), use_container_width=True)

# Daily and Cumulative Returns
st.subheader("Returns Analysis")
plot_returns(data)

# Volume Chart
st.subheader("Volume Chart")
fig = go.Figure([go.Bar(x=data.index, y=data["Volume"], marker_color="lightgray")])
fig.update_layout(title="Trading Volume", xaxis_title="Date", yaxis_title="Volume")
st.plotly_chart(fig, use_container_width=True)

# Upload Portfolio Section
if uploaded_file:
    df_portfolio = load_uploaded_file(uploaded_file)
    st.subheader("Uploaded Portfolio Data")
    st.dataframe(df_portfolio)

# Nifty 200 Strong Uptrend Stocks
st.subheader("Strong Uptrend Stocks in Nifty 200 (MACD > 0, RSI > 50, Close > Upper BB, Close > EMA20)")
nifty_uptrend_df = filter_nifty200_stocks()
if not nifty_uptrend_df.empty:
    st.dataframe(nifty_uptrend_df)
else:
    st.info("No Nifty 200 stocks currently meet the strong uptrend criteria.")
