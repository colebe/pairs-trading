import pandas as pd
import numpy as np
def zscore(series):
    """
    Calculate the z-score of a series. Uses rolling mean and standard deviation over a 60-period window to avoid lookahead bias.
    
    Args:
        series (pd.Series): The input series to calculate the z-score for.
    
    Returns:
        float: The z-score of the series.
    """
    rolling_mean = series.rolling(window=60).mean()
    rolling_std = series.rolling(window=60).std()
    zscore = (series - rolling_mean) / rolling_std
    return zscore

def backtest(spread, entry_threshold=2.0, exit_threshold=0.5):
    """
    Backtest a pairs trading strategy based on the spread z-score.
    
    Args:
        spread (pd.Series): The spread series.
        entry_threshold (float): The z-score threshold for opening a position.
        exit_threshold (float): The z-score threshold for closing a position.
    
    Returns:
        pd.DataFrame: A DataFrame with the backtest results.
    """
    signals = pd.DataFrame(index=pd.RangeIndex(len(spread)), columns=['zscore', 'long_entry', 'short_entry', 'exit'])
    signals['zscore'] = zscore(spread)
    signals['long_entry'] = signals['zscore'] < -entry_threshold
    signals['short_entry'] = signals['zscore'] > entry_threshold
    signals['exit'] = (signals['zscore'] > -exit_threshold) & (signals['zscore'] < exit_threshold)
    
    return signals