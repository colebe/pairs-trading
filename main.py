import argparse
import numpy as np
import matplotlib.pyplot as plt
from src.loader import get_sp500_symbols
from src.pair_selection import select_pairs
from src.cointegration import engle_granger
from src.backtesting import backtest, zscore, simulate_trading
from src.plotting import plot_spread_and_signals

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--traindates', nargs=2, required=True)
    parser.add_argument('--testdates', nargs=2, required=True)
    parser.add_argument('--traininterval', type=str, default='1d')
    parser.add_argument('--testinterval', type=str, default='1d')

    args = parser.parse_args()
    
    start_train, end_train = args.traindates
    start_test, end_test = args.testdates
    traininterval = args.traininterval
    testinterval = args.testinterval

    # Find pairs
    print(f"Finding pairs for training period: {start_train} to {end_train} with interval {traininterval}")
    sp500_data = get_sp500_symbols(start_train, end_train, traininterval, nan_threshold=0.9)
    pairs = select_pairs(sp500_data, n_clusters=25)
    print(f"Found {len(pairs)} pairs for cointegration testing.")
    
    cointegration_results = {}
    for label, pairs in pairs.items():
        ticker1, ticker2 = pairs[0]
        result = engle_granger(np.log(sp500_data[ticker1]), np.log(sp500_data[ticker2]))
        cointegration_results[(ticker1, ticker2)] = result

    # Print cointegration results
    print("\nCointegrated pairs:")
    beta_values = {}
    for (ticker1, ticker2), result in sorted(cointegration_results.items(), key=lambda x: x[1]):
        adf_statistic, p_value, critical_values, beta = result
        beta_values[(ticker1, ticker2)] = beta
        if p_value < 0.05:
            print(f"{ticker1} & {ticker2} (ADF: {adf_statistic:.4f}, p-value: {p_value:.4f})")
    
    # Backtest pairs
    print(f"\nBacktesting pairs for test period: {start_test} to {end_test} with interval {testinterval}")
    test_data = get_sp500_symbols(start_test, end_test, testinterval, nan_threshold=0.9)
    backtest_results = {}
    for (ticker1, ticker2), result in cointegration_results.items():
        if result[1] < 0.05:
            # Try except since some pairs may not have enough data in the test period
            try:
                beta = beta_values[(ticker1, ticker2)]
                spread = np.log(test_data[ticker2]) - beta * np.log(test_data[ticker1])
                signals = backtest(spread, zscore_window=20, entry_threshold=1.25, exit_threshold=0.25)
                backtest_results[(ticker1, ticker2)] = signals
            except KeyError as e:
                print(f"Data for {ticker1} or {ticker2} not available in test period: {e}")
    
    # Compute returns and Sharpe ratio
    for (ticker1, ticker2), signals in backtest_results.items():
        results, trades, performance = simulate_trading(signals, test_data, ticker1, ticker2, beta=beta_values[(ticker1, ticker2)], slippage=0, fees=0)
        print(f"Performance for {ticker1} & {ticker2}:")
        for key, value in performance.items():
            print(f"  {key}: {value}")
        print("------------------------------")

    # Plot results for the first pair
    first_pair = next(iter(backtest_results))
    ticker1, ticker2 = first_pair
    signals = backtest_results[first_pair]
    spread = np.log(test_data[ticker1]) - np.log(test_data[ticker2])
    plot_spread_and_signals(spread, signals, title=f"Spread and Signals for {ticker1} & {ticker2}")
        
if __name__ == "__main__":
    main()