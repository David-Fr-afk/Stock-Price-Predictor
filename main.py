import yfinance as yf
import pandas as pd

data = yf.download('AAPL', interval='1d', start='2023-01-01', end='2023-12-31')

data_close = data[['Close']]

data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

data['MACD'] = data['EMA_12'] - data['EMA_26']
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean() 

print(data[['Close', 'EMA_12', 'EMA_26', 'MACD', 'Signal_Line']].head())

