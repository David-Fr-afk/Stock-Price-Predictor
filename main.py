import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima


def calculate_rsi(data, column='Close', window=14):
    delta = data[column].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi






data = yf.download('AAPL', interval='1d', start='2022-10-01', end='2024-12-31')
data.index = pd.to_datetime(data.index)
data = data.asfreq('B')
data_close = data[['Close']]


data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = data['EMA_12'] - data['EMA_26']
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['RSI'] = calculate_rsi(data, column='Close', window=14) 
data['MA_20'] = data['Close'].rolling(window=20).mean()

data['Buy_Signal'] = (data['MACD'] > data['Signal_Line']) & (data['RSI'] < 30)

data['Sell_Signal'] = (data['MACD'] < data['Signal_Line']) & (data['RSI'] > 70)

data['Action'] = 'Hold' 
data.loc[data['Buy_Signal'], 'Action'] = 'Buy'
data.loc[data['Sell_Signal'], 'Action'] = 'Sell'

p, d, q = 2, 1, 2  # Just testing with arbitrary values

arima_model = ARIMA(data['Close'], order=(2,1,2))
arima_result = arima_model.fit()

forecast_steps = 60
forecast = arima_result.forecast(steps=forecast_steps)

forecast_dates = pd.date_range(start=data.index[-1], periods=forecast_steps + 1, freq='D')[1:]
forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecasted_Close': forecast})
forecast_df['Smoothed_Close'] = forecast_df['Forecasted_Close'].rolling(window=10).mean()

print("\nLast 5 days of data:")
print(data[['Close', 'MACD', 'Signal_Line', 'RSI', 'Buy_Signal', 'Sell_Signal', 'Action']].tail())

print("\nForecasted Prices for Next 60 Days:")
print(forecast_df.tail(30))  