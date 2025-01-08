import yfinance as yahooFinance

GetFacebookInformation = yahooFinance.Ticker("META")

print(GetFacebookInformation.info)
