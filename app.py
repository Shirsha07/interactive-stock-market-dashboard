import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import talib

# Title
st.set_page_config(layout="wide")
st.title("📈 Stock Market Visualizer")

# Sidebar
st.sidebar.header("🔍 Stock Selector")
symbol = st.sidebar.text_input("Enter NSE Symbol", "RELIANCE")
timeframe = st.sidebar.selectbox("Select Timeframe", ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y'])

# Intraday flag and interval handling
intraday = timeframe in ['1d', '5d']
interval = '5m' if timeframe == '1d' else ('15m' if timeframe == '5d' else '1d')

# Data Fetching
@st.cache_data(show_spinner=False)
def get_data(symbol, period, interval):
    return yf.download(f"{symbol}.NS", period=period, interval=interval)

try:
    df = get_data(symbol, timeframe, interval)
    if df.empty:
        st.warning("⚠️ No data available. Please check the symbol or try a different timeframe.")
        st.stop()
    
    df.dropna(inplace=True)
    df['Close'] = df['Close'].astype(float)

    # Technical Indicators (1D Inputs Only)
    close = df['Close'].values.flatten()

    df['EMA20'] = talib.EMA(close, timeperiod=20)
    df['RSI'] = talib.RSI(close, timeperiod=14)
    df['MACD'], df['MACD_signal'], _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    upper, middle, lower = talib.BBANDS(close, timeperiod=20)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = upper, middle, lower

    # Chart
    st.subheader(f"📊 Candlestick Chart: {symbol.upper()} ({timeframe})")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Candlestick'
    )])

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='orange', width=1), name='Bollinger Upper'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_middle'], line=dict(color='gray', width=1), name='Bollinger Middle'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='orange', width=1), name='Bollinger Lower'))

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # RSI Chart
    st.subheader("📈 RSI Indicator")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name='RSI'))
    fig_rsi.add_shape(type='line', x0=df.index[0], x1=df.index[-1], y0=70, y1=70,
                      line=dict(color='red', dash='dash'))
    fig_rsi.add_shape(type='line', x0=df.index[0], x1=df.index[-1], y0=30, y1=30,
                      line=dict(color='green', dash='dash'))
    st.plotly_chart(fig_rsi, use_container_width=True)

    # Export Options
    st.download_button("📥 Export Chart as HTML", fig.to_html(), file_name=f"{symbol}_chart.html")
    
    # Portfolio Tracking
    st.subheader("📁 Upload Portfolio (CSV or Excel)")
    portfolio_file = st.file_uploader("Upload file with 'Symbol' column", type=['csv', 'xlsx'])
    if portfolio_file:
        if portfolio_file.name.endswith('.csv'):
            portfolio_df = pd.read_csv(portfolio_file)
        else:
            portfolio_df = pd.read_excel(portfolio_file)

        if 'Symbol' not in portfolio_df.columns:
            st.error("CSV/Excel must contain a 'Symbol' column.")
        else:
            portfolio_df['Symbol'] = portfolio_df['Symbol'].str.upper()
            st.dataframe(portfolio_df)

    # Stock Correlation
    st.subheader("🔗 Stock Correlation Analysis")
    symbols_input = st.text_input("Enter comma-separated symbols", "RELIANCE,INFY,TCS,ITC")
    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    if len(symbols) > 1:
        close_prices = pd.DataFrame()
        for sym in symbols:
            data = yf.download(f"{sym}.NS", period="3mo", interval='1d')
            close_prices[sym] = data['Close']
        corr = close_prices.corr()
        st.dataframe(corr.style.background_gradient(cmap='coolwarm'))

except Exception as e:
    st.error(f"❌ Error calculating indicators for {symbol.upper()}: {e}")


















