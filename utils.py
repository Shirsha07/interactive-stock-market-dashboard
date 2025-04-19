import pandas as pd
import yfinance as yf
from ta.trend import MACD
from ta.momentum import RSI
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator

# Function to load data from a file (CSV/Excel/Google Sheets)
def load_data_from_file(uploaded_file):
    if uploaded_file.name.endswith("csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(("xls", "xlsx")):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format")

# Function to calculate technical indicators
def calculate_indicators(df):
    # Ensure 'Close' is strictly one-dimensional
    df['Close'] = df['Close'].squeeze()  # Flattening if it's 2D

    # MACD
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # RSI
    rsi = RSI(df['Close'])
    df['RSI'] = rsi.rsi()

    # Bollinger Bands
    bb = BollingerBands(df['Close'])
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    # EMA (20-period)
    ema = EMAIndicator(df['Close'], window=20)
    df['EMA_20'] = ema.ema_indicator()

    # SMA (50-period)
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    return df

# Function to filter stocks in upward trend
def filter_upward_trend(df):
    # Filter stocks based on MACD, RSI, Bollinger Bands, and EMA conditions for upward trend
    upward_trend = df[(df['MACD'] > 0) & (df['RSI'] > 50) & (df['Close'] > df['BB_upper']) & (df['Close'] > df['EMA_20'])]
    return upward_trend

# Function to filter stocks in downward trend
def filter_downward_trend(df):
    # Filter stocks based on MACD, RSI, Bollinger Bands, and EMA conditions for downward trend
    downward_trend = df[(df['MACD'] < 0) & (df['RSI'] < 50) & (df['Close'] < df['BB_lower']) & (df['Close'] < df['EMA_20'])]
    return downward_trend






