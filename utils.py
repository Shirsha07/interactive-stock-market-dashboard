import yfinance as yf
import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# Fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Calculate indicators and add them to the dataframe
def calculate_indicators(data):
    close = data["Close"]  

    # MACD (Moving Average Convergence Divergence)
    macd_indicator = MACD(close)
    data["MACD"] = macd_indicator.macd()

    # RSI (Relative Strength Index)
    rsi_indicator = RSIIndicator(close)
    data["RSI"] = rsi_indicator.rsi()

    # EMA (Exponential Moving Average) with a 20-day window
    ema_indicator = EMAIndicator(close, window=20)
    data["EMA20"] = ema_indicator.ema_indicator()

    # Bollinger Bands
    bb_indicator = BollingerBands(close)
    data["BB_upper"] = bb_indicator.bollinger_hband()
    data["BB_lower"] = bb_indicator.bollinger_lband()

    # Ensure all new columns are aligned with the existing dataframe
    data = data.dropna(subset=["MACD", "RSI", "EMA20", "BB_upper", "BB_lower"])

    return data

# Filter stocks with upward trend
def filter_upward_trending_stocks(data):
    return data[
        (data["MACD"] > 0) &
        (data["RSI"] > 50) &
        (data["Close"] >= data["BB_upper"]) &
        (data["Close"] > data["EMA20"])
    ]

# Filter stocks with downward trend
def filter_downward_trending_stocks(data):
    return data[
        (data["MACD"] < 0) &
        (data["RSI"] < 50) &
        (data["Close"] <= data["BB_lower"]) &
        (data["Close"] < data["EMA20"])
    ]

# Example usage
ticker = "AAPL"
start_date = "2020-01-01"
end_date = "2023-01-01"
data = fetch_stock_data(ticker, start_date, end_date)
data_with_indicators = calculate_indicators(data)

# Filter upward trending and downward trending stocks
upward_trends = filter_upward_trending_stocks(data_with_indicators)
downward_trends = filter_downward_trending_stocks(data_with_indicators)

print("Upward Trending Stocks:")
print(upward_trends)

print("Downward Trending Stocks:")
print(downward_trends)





