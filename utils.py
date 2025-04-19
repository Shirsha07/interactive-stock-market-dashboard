import yfinance as yf
import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def calculate_indicators(data):
    close = data["Close"]
    
    # MACD
    macd_raw = MACD(close).macd()
    data["MACD"] = pd.Series(macd_raw.values.ravel(), index=data.index)

    # RSI
    rsi_raw = RSIIndicator(close).rsi()
    data["RSI"] = pd.Series(rsi_raw.values.ravel(), index=data.index)

    # EMA
    ema_raw = EMAIndicator(close, window=20).ema_indicator()
    data["EMA20"] = pd.Series(ema_raw.values.ravel(), index=data.index)

    # Bollinger Bands
    bb = BollingerBands(close)
    upper_band = bb.bollinger_hband()
    lower_band = bb.bollinger_lband()
    data["BB_upper"] = pd.Series(upper_band.values.ravel(), index=data.index)
    data["BB_lower"] = pd.Series(lower_band.values.ravel(), index=data.index)

    return data

def filter_upward_trending_stocks(data):
    return data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Close"] >= data["BB_upper"]) &
        (data["Close"] > data["EMA20"])
    ]

def filter_downward_trending_stocks(data):
    return data[
        (data["MACD"] < 0) &
        (data["RSI"] < 50) &
        (data["Close"] <= data["BB_lower"]) &
        (data["Close"] < data["EMA20"])
    ]



