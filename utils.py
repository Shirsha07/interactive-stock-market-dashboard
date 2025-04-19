import pandas as pd
from ta.trend import MACD
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
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate all indicators
def calculate_indicators(data):
    # Ensure 'Close' column is strictly one-dimensional
    data['Close'] = data['Close'].squeeze()  # Flattening if it's 2D (i.e., shape (n, 1))

    # MACD
    macd_indicator = MACD(data['Close'])
    data['MACD'] = macd_indicator.macd()
    data['MACD_signal'] = macd_indicator.macd_signal()

    # Manually calculate RSI
    data['RSI'] = calculate_rsi(data['Close'])

    # Bollinger Bands
    bb_indicator = BollingerBands(data['Close'])
    data['BB_upper'] = bb_indicator.bollinger_hband()
    data['BB_lower'] = bb_indicator.bollinger_lband()

    # EMA (20-period)
    ema_indicator = EMAIndicator(data['Close'], window=20)
    data['EMA_20'] = ema_indicator.ema_indicator()

    # SMA (50-period)
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    return data
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






