from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

app = FastAPI() 

def calculate_rsi(data, column='Close', window=14):
    delta = data[column].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.get("/stock/{ticker}")
def get_stock_data(ticker: str):
    data = yf.download(ticker, interval='1d', start='2023-10-01', end='2024-10-31')
    data.index = pd.to_datetime(data.index)
    data = data.asfreq('B').ffill()

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

    return data[['Close', 'MACD', 'Signal_Line', 'RSI', 'Action']].tail(10).to_dict()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend!"}



@app.get("/forecast/{ticker}")
def get_forecast(ticker: str):
    data = yf.download(ticker, interval='1d', start='2023-10-01', end='2024-10-31')
    data.index = pd.to_datetime(data.index)
    data = data.asfreq('B').ffill()
    
    arima_model = ARIMA(data['Close'], order=(2,1,2))
    arima_result = arima_model.fit()
    forecast_steps = 60
    forecast = arima_result.forecast(steps=forecast_steps)
    
    forecast_start_date = data.index[-1]
    forecast_dates = pd.date_range(start=forecast_start_date, periods=forecast_steps + 1, freq='D')[1:]
    forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecasted_Close': forecast})
    forecast_df['Smoothed_Close'] = forecast_df['Forecasted_Close'].rolling(window=10).mean()

    return forecast_df.tail(30).to_dict()

