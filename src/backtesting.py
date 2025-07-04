import pandas as pd
import numpy as np
def zscore(series, window=60):
    """
    Calculate the z-score of a series. Uses rolling mean and standard deviation over a 60-period window to avoid lookahead bias.
    
    Parameters:
        series (pd.Series): The input series to calculate the z-score for.
    
    Returns:
        float: The z-score of the series.
    """
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    z = (series - rolling_mean) / rolling_std
    return z

def backtest(spread, entry_threshold=2.0, exit_threshold=0.5, zscore_window=60):
    """
    Backtest a pairs trading strategy based on the spread z-score.
    
    Parameters:
        spread (pd.Series): The spread series.
        entry_threshold (float): The z-score threshold for opening a position.
        exit_threshold (float): The z-score threshold for closing a position.
    
    Returns:
        pd.DataFrame: A DataFrame with the backtest results.
    """
    signals = pd.DataFrame(index=spread.index, columns=['zscore', 'long_entry', 'short_entry', 'exit'])
    signals['zscore'] = zscore(spread, window=zscore_window)
    signals['long_entry'] = signals['zscore'] < -entry_threshold
    signals['short_entry'] = signals['zscore'] > entry_threshold
    signals['exit'] = (signals['zscore'] > -exit_threshold) & (signals['zscore'] < exit_threshold)
    
    return signals

def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """
    Calculate the Sharpe ratio of a series of returns.
    
    Parameters:
        returns (pd.Series): The series of returns.
        risk_free_rate (float): The risk-free rate of return.
        periods_per_year (int): The number of periods per year (e.g., 252 for daily returns).

    Returns:
        float: The Sharpe ratio.
    """
    excess_returns = returns - risk_free_rate / periods_per_year
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year) if np.std(excess_returns) != 0 else 0

def max_drawdown(equity_curve):
    """
    Calculate the maximum drawdown of an equity curve.
    Parameters:
        equity_curve (pd.Series): The equity curve series.
    Returns:
        float: The maximum drawdown (most negative drop from peak).
    """
    peak = equity_curve.cummax()
    drawdown = equity_curve - peak
    return drawdown.min()  # Most negative drop from peak

def simulate_trading(signals, close, symbol1, symbol2, beta, slippage=0.0005, fees=0.0005, interval='1d'):
    """
    Simulate trading based on generated signals.

    Parameters:
        signals (pd.DataFrame): DataFrame with 'long_entry', 'short_entry', 'exit' columns.
        close (pd.DataFrame): DataFrame with close prices for both symbols.
        symbol1 (str): First symbol.
        symbol2 (str): Second symbol.
        beta (float): Hedge ratio (beta) for the pair.
        slippage (float): Slippage percentage for entry/exit prices.
        fees (float): Percentage fees for trading.
    Returns:
        tuple: (results DataFrame, trades DataFrame, performance metrics dict)
    """
    # Determine appropriate periods per year
    periods_per_year = {
        '1d': 252,
        '1h': 252 * 6.5,  # 6.5 trading hours/day
        '1m': 252 * 390,  # 390 minutes/day
    }.get(interval, 252)

    # Determine rolling window size for z-score
    zscore_window = {
        '1d': 60,
        '1h': 130,
        '1m': 390,  # 1 trading day worth of 1m data
    }.get(interval, 60)

    # Recalculate z-score with adjusted window
    spread = np.log(close[symbol1]) - beta * np.log(close[symbol2])
    signals = backtest(spread, zscore_window=zscore_window)

    in_trade = False
    entry_type = None
    entry_price_x = entry_price_y = 0
    entry_index = None
    trade_pnls = []
    equity_curve = []
    cumulative_pnl = 0

    for i in range(1, len(signals)):
        price_x = close[symbol1].iloc[i]
        price_y = close[symbol2].iloc[i]

        if not in_trade:
            if signals['long_entry'].iloc[i]:
                in_trade = True
                entry_type = 'long'
                entry_price_x = price_x * (1 - slippage)
                entry_price_y = price_y * (1 + slippage)
                entry_index = i
            elif signals['short_entry'].iloc[i]:
                in_trade = True
                entry_type = 'short'
                entry_price_x = price_x * (1 + slippage)
                entry_price_y = price_y * (1 - slippage)
                entry_index = i

        elif in_trade and signals['exit'].iloc[i]:
            exit_price_x = price_x * (1 - slippage if entry_type == 'long' else 1 + slippage)
            exit_price_y = price_y * (1 + slippage if entry_type == 'long' else 1 - slippage)

            ret_x = (exit_price_x - entry_price_x) / entry_price_x
            ret_y = (exit_price_y - entry_price_y) / entry_price_y

            if entry_type == 'long':
                pnl = ret_y - beta * ret_x
            else:
                pnl = -ret_y + beta * ret_x

            net_pnl = pnl - (4 * fees)
            cumulative_pnl += net_pnl

            trade_pnls.append({
                'entry_type': entry_type,
                'entry_index': entry_index,
                'exit_index': i,
                'gross_return': pnl,
                'fees': 4 * fees,
                'net_return': net_pnl
            })

            in_trade = False
            entry_type = None

        equity_curve.append(cumulative_pnl)

    results = signals.copy()
    results['equity'] = pd.Series(equity_curve, index=signals.index[:len(equity_curve)])
    results['equity'] = results['equity'].ffill()
    results['returns'] = results['equity'].diff().fillna(0)

    trades_df = pd.DataFrame(trade_pnls)
    sharpe = sharpe_ratio(results['returns'], periods_per_year=periods_per_year)
    drawdown = max_drawdown(results['equity'])

    performance = {
        'sharpe_ratio': sharpe,
        'max_drawdown': drawdown,
        'total_return': results['equity'].iloc[-1] if not results['equity'].empty else 0,
        'num_trades': len(trades_df)
    }

    return results, trades_df, performance