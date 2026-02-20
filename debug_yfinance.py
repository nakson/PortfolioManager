import yfinance as yf
import pandas as pd

ticker_list = ['AAPL', '0700.HK', '600519.SS', 'NVDA']
print(f"Tickers: {ticker_list}")

try:
    print("Downloading data...")
    # Using the same call as in app.py
    data = yf.download(ticker_list, period="1d", progress=False)['Close']
    print("\nData Shape:", data.shape)
    print("\nData Head:")
    print(data)
    
    print("\nLast Row (iloc[-1]):")
    current_prices = data.iloc[-1]
    print(current_prices)
    
    print("\nIterating tickers:")
    prices = {}
    for ticker in ticker_list:
        if ticker in current_prices:
            val = current_prices[ticker]
            print(f"{ticker}: {val} (Type: {type(val)})")
            prices[ticker] = val
        else:
            print(f"{ticker}: NOT FOUND in current_prices")

except Exception as e:
    print(f"Error: {e}")
