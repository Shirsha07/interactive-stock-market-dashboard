import yfinance as yf
import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def calculate_indicators(data):
    # Ensure Close is a Series, not DataFrame
    close = data["Close"].squeeze()

    # MACD
    macd = MACD(close).macd().squeeze()
    data["MACD"] = macd

    # RSI
    rsi = RSIIndicator(close).rsi().squeeze()
    data["RSI"] = rsi

    # EMA
    ema = EMAIndicator(close, window=20).ema_indicator().squeeze()
    data["EMA20"] = ema

    # Bollinger Bands
    bb = BollingerBands(close)
    data["BB_upper"] = bb.bollinger_hband().squeeze()
    data["BB_lower"] = bb.bollinger_lband().squeeze()

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


