import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from utils import calculate_indicators, filter_upward_trend, filter_downward_trend, load_data_from_file
from io import StringIO

# Function to create candlestick chart with overlays
def create_candlestick_chart(df, stock_symbol):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        name='Candlesticks')])

    # Add moving averages (EMA, SMA) as overlays
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], mode='lines', name='EMA 20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='blue')))
    
    # Add RSI and Bollinger Bands overlays
    fig.update_layout(title=f"Stock Price and Indicators for {stock_symbol}",
                      xaxis_title='Date',
                      yaxis_title='Price (USD)',
                      template='plotly_dark')
    return fig

# Upload CSV/Excel/Google Sheets
st.title("Interactive Stock Market Dashboard")

uploaded_file = st.file_uploader("Upload your CSV/Excel/Google Sheet file", type=["csv", "xlsx", "xls"])
if uploaded_file is not None:
    df = load_data_from_file(uploaded_file)
    df = calculate_indicators(df)  # Calculate indicators like MACD, RSI, Bollinger Bands
    stock_symbol = df.columns[0]  # Assuming the first column is the stock symbol

    # Display charts with overlays
    candlestick_chart = create_candlestick_chart(df, stock_symbol)
    st.plotly_chart(candlestick_chart)

    # Filter and display upward and downward trends
    upward_stocks = filter_upward_trend(df)
    downward_stocks = filter_downward_trend(df)

    st.subheader("Upward Trend Stocks")
    st.write(upward_stocks)

    st.subheader("Downward Trend Stocks")
    st.write(downward_stocks)

    # Export options
    export_choice = st.selectbox("Export Options", ["Export as PNG", "Export as HTML"])
    if export_choice == "Export as PNG":
        fig.write_image("candlestick_chart.png")
        st.download_button("Download PNG", "candlestick_chart.png")
    elif export_choice == "Export as HTML":
        fig.write_html("candlestick_chart.html")
        st.download_button("Download HTML", "candlestick_chart.html")

else:
    st.warning("Please upload a CSV/Excel file.")

