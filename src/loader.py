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

def get_sp500_symbols(start_date, end_date, interval='1d', nan_threshold=0.9):
    """
    Get the current S&P 500 symbols.
    
    Parameters:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        interval (str): Data interval (e.g., '1d', '1m').
        nan_threshold (float): Threshold for dropping columns with too many NaNs.

    Returns:
        pd.DataFrame: DataFrame containing historical close prices of S&P 500 companies.
    """
    # Fetch S&P 500 companies from Wikipedia
    # Note: This will fetch the current list of S&P 500 companies which may not be the same as the list during the specified date range.
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    tickers = sp500['Symbol'].tolist()
    # Handle tickers with periods (e.g., BRK.B) for yfinance
    tickers = [t.replace('.', '-') for t in tickers]
    # Download historical data for tickers
    data = yf.download(tickers, start=start_date, end=end_date, interval=interval, auto_adjust=True)["Close"]
    # Filter out tickers with insufficient data
    clean_data = data.dropna(axis=1, thresh=int(nan_threshold * len(data)))
    if interval == "1m":
        # Define trading hours in UTC (13:30 to 20:00) and generate valid weekdays only
        full_days = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B' = business days (Mon–Fri)
        full_index = pd.DatetimeIndex([])
        for day in full_days[:-1]:  # Exclude the last day since it's not inclusive
            trading_day_minutes = pd.date_range(
                start=day.strftime('%Y-%m-%d') + ' 13:30',
                end=day.strftime('%Y-%m-%d') + ' 20:00',
                freq='1min',
                tz='UTC'
            )
            full_index = full_index.append(trading_day_minutes)

        # Reindex to include all valid trading minutes
        clean_data = clean_data.reindex(full_index)

    # Forward and backward fill for small gaps
    clean_data.ffill(inplace=True, limit=2)
    clean_data.bfill(inplace=True, limit=2)
    clean_data.dropna(inplace=True, axis=1, how='any')  # Drop columns with all NaN values
    return clean_data