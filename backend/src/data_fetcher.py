import yfinance as yf
import pandas as pd

def fetch_stock_data(company_ticker, period='1y', interval='1d'):
  
    try:
        stock = yf.Ticker(company_ticker)
        data = stock.history(period=period, interval=interval)
        print(data  )
        if data.empty:
            raise ValueError(f"No data returned for ticker '{company_ticker}'")
        data.reset_index(inplace=True)  # Make date a column
        return data
    except Exception as e:
        print(f"❌ Error fetching data for {company_ticker}: {e}")
        return None
