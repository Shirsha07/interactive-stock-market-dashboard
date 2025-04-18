import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
from io import BytesIO
import concurrent.futures

st.set_page_config(layout="wide", page_title="Stock Market Visualizer")
st.title("📈 Stock Market Visualizer")

# Load Nifty 200 symbols from GitHub (static copy)
@st.cache_data
def load_nifty200():
    url = "https://raw.githubusercontent.com/Shirsha07/interactive-stock-market-dashboard/main/nifty200.csv"
    df = pd.read_csv(url)
    return df["Symbol"].tolist()

nifty200_symbols = load_nifty200()

# Fetch stock data + indicators
def fetch_data(symbol, period="1y"):
    df = yf.download(symbol + ".NS", period=period, progress=False)

    if df.empty:
        st.warning(f"No data fetched for {symbol}")
        return pd.DataFrame()

    if "Close" not in df.columns:
        st.error(f"'Close' column is missing for {symbol}")
        return pd.DataFrame()

    try:
        # Calculate indicators
        close = df["Close"]
        df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
        df["MACD"] = MACD(close=close).macd_diff()
        df["RSI"] = RSIIndicator(close=close).rsi()
        bb = BollingerBands(close=close)
        df["BB_upper"] = bb.bollinger_hband()
        df["BB_lower"] = bb.bollinger_lband()
        st.write(f"Columns after indicators for {symbol}:", df.columns.tolist())

    # Drop only if both exist
    required_cols = ["Close", "BB_upper"]
    if all(col in df.columns for col in required_cols):
        df.dropna(subset=required_cols, inplace=True)
    else:
        missing = [col for col in required_cols if col not in df.columns]
        st.error(f"Missing required columns: {missing}")
        return pd.DataFrame()

    # Align and compare
    close_aligned, bb_upper_aligned = df["Close"].align(df["BB_upper"], join='inner')
    df = df.loc[close_aligned.index]
    df["Touching_Upper_Band"] = close_aligned >= bb_upper_aligned

    st.write(f"Final DataFrame preview for {symbol}:", df.head())

    return df
    except Exception as e:
        st.error(f"Error calculating indicators for {symbol}: {e}")
        return pd.DataFrame()

    # ✅ Only drop NaNs if both columns exist
    missing_cols = [col for col in ["Close", "BB_upper"] if col not in df.columns]
    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        return pd.DataFrame()

    # Drop rows with NaNs in required columns
    df.dropna(subset=["Close", "BB_upper"], inplace=True)

    # Ensure 1D and aligned series
    close = df["Close"]
    bb_upper = df["BB_upper"]
    close_aligned, bb_upper_aligned = close.align(bb_upper, join="inner")
    df = df.loc[close_aligned.index]

    # Perform the comparison
    df["Touching_Upper_Band"] = close_aligned >= bb_upper_aligned

    return df

# Analyze stock for trend
def analyze_stock(symbol):
    try:
        df = fetch_data(symbol)
        latest = df.iloc[-1]
        if (latest["MACD"] > 0 and latest["RSI"] > 50 and
            latest["Touching_Upper_Band"] and latest["EMA20"] < latest["Close"]):
            return symbol, "up"
        else:
            return symbol, "down"
    except:
        return None, None

# Parallel trend analysis
@st.cache_data(show_spinner=False)
def analyze_trends(symbols):
    up, down = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(analyze_stock, symbols)
        for symbol, trend in results:
            if trend == "up":
                up.append(symbol)
            elif trend == "down":
                down.append(symbol)
    return up, down

# Button-triggered analysis
st.header("📊 Upward / Downward Trend Stock Analyzer")

upward, downward = [], []

if st.button("🔍 Analyze Live Trends"):
    with st.spinner("Analyzing live stock data..."):
        upward, downward = analyze_trends(nifty200_symbols)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Upward Trend")
        st.write(upward if upward else "No matching stocks.")

    with col2:
        st.subheader("🔴 Downward Trend")
        st.write(downward if downward else "No matching stocks.")

# Interactive Chart
st.header("📉 Candlestick Chart")

stock = st.selectbox("Select Stock", nifty200_symbols)
timeframe = st.selectbox("Timeframe", ["3mo", "6mo", "1y", "2y"], index=2)
data = fetch_data(stock, period=timeframe)

fig = go.Figure(data=[go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'])])

fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='orange'), name='EMA20'))
fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], line=dict(color='blue', dash='dot'), name='BB Upper'))
fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], line=dict(color='blue', dash='dot'), name='BB Lower'))

st.plotly_chart(fig, use_container_width=True)

# Upload Portfolio
st.header("📂 Upload Portfolio CSV")

uploaded_file = st.file_uploader("Upload your portfolio (CSV/XLSX)", type=['csv', 'xlsx'])
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.dataframe(df)

# Correlation Matrix
st.header("📈 Correlation Matrix")

symbols_corr = st.multiselect("Choose stocks for correlation", nifty200_symbols[:50], default=nifty200_symbols[:5])
correlation_df = pd.DataFrame()

for sym in symbols_corr:
    try:
        df = fetch_data(sym)
        correlation_df[sym] = df["Close"]
    except:
        continue

if not correlation_df.empty:
    st.dataframe(correlation_df.corr())

# Export Chart
st.header("📤 Export Chart")
export_format = st.selectbox("Export format", ["PNG", "HTML"])
if st.button("Export"):
    if export_format == "PNG":
        fig.write_image("chart.png")
        with open("chart.png", "rb") as f:
            st.download_button("Download PNG", f, file_name="chart.png")
    else:
        html_buf = BytesIO()
        fig.write_html(html_buf)
        st.download_button("Download HTML", html_buf, file_name="chart.html")

# Config Save
st.header("🛠️ Save Config")
st.json({
    "selected_stock": stock,
    "timeframe": timeframe,
    "upward": upward,
    "downward": downward
})



