import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import fetch_stock_data, calculate_indicators, filter_upward_trending_stocks, filter_downward_trending_stocks
from io import BytesIO
import base64

st.set_page_config(page_title="Interactive Stock Market Dashboard", layout="wide")

st.title("📈 Interactive Stock Market Dashboard")

# Sidebar
st.sidebar.header("Options")

ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS)", value="RELIANCE.NS")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
ma_periods = st.sidebar.multiselect("Select Moving Averages (days)", [10, 20, 50, 100, 200], default=[20, 50])

# Upload Portfolio
st.sidebar.subheader("📤 Portfolio Analysis")
uploaded_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)", type=["csv", "xlsx"])

# Fetch data
df = fetch_stock_data(ticker, start_date, end_date)
df = calculate_indicators(df)

# --- Candlestick Chart ---
st.subheader(f"📊 Candlestick Chart: {ticker}")
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'],
    name='Candlesticks'
))

# EMA overlays
for period in ma_periods:
    ema_col = f"EMA{period}"
    df[ema_col] = df["Close"].ewm(span=period, adjust=False).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df[ema_col], mode='lines', name=f'EMA{period}'))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='rgba(200,0,0,0.3)'), name='BB Upper'))
fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='rgba(0,0,200,0.3)'), name='BB Lower', fill='tonexty'))

# Layout
fig.update_layout(
    xaxis_rangeslider_visible=False,
    height=600,
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# --- Daily Returns ---
st.subheader("📉 Daily Returns & Summary")
df["Daily Return (%)"] = df["Close"].pct_change() * 100
st.dataframe(df[["Close", "Daily Return (%)"]].dropna().tail(10), use_container_width=True)

# --- Trend Detection ---
st.subheader("📈 Trend Detection")
upward = filter_upward_trending_stocks(df)
downward = filter_downward_trending_stocks(df)

st.success(f"🔼 Upward Trend Matches: {len(upward)} days")
st.dataframe(upward[["Close", "MACD", "RSI", "EMA20", "BB_upper"]].tail(5), use_container_width=True)

st.warning(f"🔽 Downward Trend Matches: {len(downward)} days")
st.dataframe(downward[["Close", "MACD", "RSI", "EMA20", "BB_lower"]].tail(5), use_container_width=True)

# --- Upload Portfolio (CSV/XLSX/Google Sheet) ---
st.subheader("📂 Upload Custom Portfolio Report")
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file)
        st.dataframe(df_upload.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- Export Chart ---
st.subheader("📤 Export Chart")
export_btns = st.columns(2)

with export_btns[0]:
    if st.button("📸 Download PNG"):
        fig.write_image("chart.png")
        with open("chart.png", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="chart.png">Click to download</a>'
        st.markdown(href, unsafe_allow_html=True)

with export_btns[1]:
    if st.button("💾 Download HTML"):
        fig.write_html("chart.html")
        with open("chart.html", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="chart.html">Click to download</a>'
        st.markdown(href, unsafe_allow_html=True)
