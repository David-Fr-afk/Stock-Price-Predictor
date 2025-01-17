import yfinance as yf
import pandas as pd


def calculate_rsi(data, column='Close', window=14):
    delta = data[column].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


data = yf.download('META', interval='1d', start='2022-01-01', end='2022-12-31')

data_close = data[['Close']]

data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = data['EMA_12'] - data['EMA_26']
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['RSI'] = calculate_rsi(data, column='Close', window=14) 

data['Buy_Signal'] = (data['MACD'] > data['Signal_Line']) & (data['RSI'] < 30)

data['Sell_Signal'] = (data['MACD'] < data['Signal_Line']) & (data['RSI'] > 70)

data['Action'] = data.apply(
    lambda row: 'Buy' if row['Buy_Signal'] 
                else 'Sell' if row['Sell_Signal'] 
                else 'Hold',
    axis=1
)
print(data[['Close', 'MACD', 'Signal_Line', 'RSI', 'Buy_Signal', 'Sell_Signal']].tail())
