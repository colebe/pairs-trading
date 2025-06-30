import yfinance as yf
import pandas as pd
import numpy as np

def get_data(symbol1, symbol2, start_date, end_date, time_interval):
    """
    Download stock data for two symbols between specified dates with specified interval.
    
    Parameters:
        symbol1 (str): First stock symbol.
        symbol2 (str): Second stock symbol.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        time_interval (str): Data interval (e.g., '1d', '1m').
        
    Returns:
        np.ndarray: Array containing adjusted close prices of both stocks.
    """
    data = yf.download([symbol1, symbol2], start=start_date, end=end_date, interval=time_interval, auto_adjust=True)
    close = data["Close"].dropna()
    return close.to_numpy()