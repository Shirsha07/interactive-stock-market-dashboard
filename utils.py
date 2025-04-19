import pandas as pd
import yfinance as yf
import ta

def fetch_stock_data(ticker, start, end, interval='1d'):
    df = yf.download(ticker, start=start, end=end, interval=interval)
    df.dropna(inplace=True)
    return df

def calculate_indicators(df):
    # Ensure 'Close' is strictly 1-dimensional
    close = pd.Series(df["Close"].values, index=df.index)

    # MACD
    macd = ta.trend.MACD(close=close)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    # RSI
    rsi = ta.momentum.RSIIndicator(close=close)
    df["RSI"] = rsi.rsi()

    # EMA (20-day)
    ema20 = ta.trend.EMAIndicator(close=close, window=20)
    df["EMA20"] = ema20.ema_indicator()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()

    return df

def filter_upward_trending_stocks(df):
    condition = (
        (df["MACD"] > 0) &
        (df["RSI"] > 50) &
        (df["Close"] >= df["BB_upper"]) &
        (df["Close"] > df["EMA20"])
    )
    return df[condition]

def filter_downward_trending_stocks(df):
    condition = (
        (df["MACD"] < 0) &
        (df["RSI"] < 50) &
        (df["Close"] <= df["BB_lower"]) &
        (df["Close"] < df["EMA20"])
    )
    return df[condition]

