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
    macd = MACD(close).macd()
    data["MACD"] = pd.Series(macd.values.ravel(), index=data.index)

    # RSI
    rsi = RSIIndicator(close).rsi()
    data["RSI"] = pd.Series(rsi.values.ravel(), index=data.index)

    # EMA 20
    ema = EMAIndicator(close, window=20).ema_indicator()
    data["EMA20"] = pd.Series(ema.values.ravel(), index=data.index)

    # Bollinger Bands
    bb = BollingerBands(close)
    upper = bb.bollinger_hband()
    lower = bb.bollinger_lband()
    data["BB_upper"] = pd.Series(upper.values.ravel(), index=data.index)
    data["BB_lower"] = pd.Series(lower.values.ravel(), index=data.index)

    return data

def filter_upward_trending_stocks(data):
    # Align all operands by reindexing to data.index just in case
    close = data["Close"].reindex(data.index)
    macd = data["MACD"].reindex(data.index)
    rsi = data["RSI"].reindex(data.index)
    bb_upper = data["BB_upper"].reindex(data.index)
    ema20 = data["EMA20"].reindex(data.index)

    return data[
        (macd > 0) &
        (rsi > 50) &
        (close >= bb_upper) &
        (close > ema20)
    ]

def filter_downward_trending_stocks(data):
    close = data["Close"].reindex(data.index)
    macd = data["MACD"].reindex(data.index)
    rsi = data["RSI"].reindex(data.index)
    bb_lower = data["BB_lower"].reindex(data.index)
    ema20 = data["EMA20"].reindex(data.index)

    return data[
        (macd < 0) &
        (rsi < 50) &
        (close <= bb_lower) &
        (close < ema20)
    ]




