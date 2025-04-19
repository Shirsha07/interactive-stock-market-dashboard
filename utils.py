import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go
import streamlit as st

def calculate_indicators(data):
    data["EMA20"] = EMAIndicator(data["Close"], window=20).ema_indicator()
    data["RSI"] = RSIIndicator(data["Close"]).rsi()
    macd = MACD(data["Close"])
    data["MACD"] = macd.macd_diff()
    bb = BollingerBands(data["Close"])
    data["BB_High"] = bb.bollinger_hband()
    data["BB_Low"] = bb.bollinger_lband()
    return data

def filter_nifty200_stocks():
    nifty200 = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
        "ICICIBANK.NS", "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS"
    ]
    uptrend = []

    for ticker in nifty200:
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if df.empty: continue
            df = calculate_indicators(df)
            latest = df.iloc[-1]

            if (
                latest["MACD"] > 0 and
                latest["RSI"] > 50 and
                latest["Close"] >= latest["BB_High"] and
                latest["Close"] > latest["EMA20"]
            ):
                uptrend.append({
                    "Symbol": ticker,
                    "MACD": round(latest["MACD"], 2),
                    "RSI": round(latest["RSI"], 2),
                    "Close": round(latest["Close"], 2),
                    "EMA20": round(latest["EMA20"], 2),
                    "Upper BB": round(latest["BB_High"], 2)
                })

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue

    return pd.DataFrame(uptrend)

def plot_candlestick(df, ticker, ma_days):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candlesticks"))
    for ma in ma_days:
        ema = EMAIndicator(df["Close"], window=ma).ema_indicator()
        fig.add_trace(go.Scatter(x=df.index, y=ema, name=f"EMA {ma}"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_High"], name="Upper Band", line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Low"], name="Lower Band", line=dict(color='blue')))
    fig.update_layout(title=ticker, xaxis_rangeslider_visible=False)
    return fig

def plot_returns(df):
    df["Daily Return"] = df["Close"].pct_change()
    df["Cumulative Return"] = (1 + df["Daily Return"]).cumprod()
    fig1 = go.Figure([go.Scatter(x=df.index, y=df["Daily Return"], mode='lines', name='Daily Return')])
    fig1.update_layout(title="Daily Returns", xaxis_title="Date", yaxis_title="Daily Return")
    fig2 = go.Figure([go.Scatter(x=df.index, y=df["Cumulative Return"], mode='lines', name='Cumulative Return')])
    fig2.update_layout(title="Cumulative Returns", xaxis_title="Date", yaxis_title="Cumulative Return")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

def load_uploaded_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return pd.DataFrame()
