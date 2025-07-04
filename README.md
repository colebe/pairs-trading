![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

# Pairs Trading Backtester

## Overview
This is a Python framework for identifying, testing, and visualizing cointegrated stock pairs mean-reversion based pairs trading. It is focused on intraday trading, since exploratory analysis ([backtesting](notebooks/backtesting.ipynb)) showed that that yielded better results. It uses historical price data from [`yfinance`](https://github.com/ranaroussi/yfinance) to identify possible pairs, and evaluates performance with metrics like Sharpe ratio, cumulative returns, and drawdowns.

## Methodology
### Pair Selection
The program starts by creating a list of viable pairs. To do this, I used Principal Component Analysis (PCA) and agglomerative clustering. I first tried K-Means clustering, but that tended to create mega-clusters with sometimes over 100 tickers. I found that agglomerative clustering works better, as it prioritizes grouping the most similar stocks first. The fact that it is slower than K-means does not matter as the dataset used is relatively small because yfinance only provides intraday data for the past week. The program then selects the two most correlated stocks in each cluster.

After creating the list of viable pairs, the program runs the Engle-Granger test for cointegration on each pair. All pairs with a p-value (chance of the time series behaving as it has purely by chance, given no cointegration) below the given threshold (I use .01) are selected as the most viable pairs.

### Backtesting

Each cointegrated pair is evaluated using a simple mean-reversion strategy based on the z-score of the price spread. Entry signals are generated when the z-score crosses predefined thresholds (e.g., ±2.0), and positions are closed when the spread reverts toward the mean (e.g. z between -0.5 and 0.5).

The backtester can account for trading costs including slippage and fees, and tracks cumulative PnL, equity curve, and daily returns. Trades are simulated using the hedge ratio (beta) estimated during the cointegration phase. Key performance metrics reported include:
- Sharpe Ratio
- Maximum Drawdown
- Total Return
- Number of Trades

The strategy supports both daily (`1d`) and intraday (`1m`) intervals. Backtests can be run separately for training and testing periods to reduce lookahead bias.


## How to Use
### Installation
Install required packages using pip
```bash
pip install -r requirements.txt
```
Or install locally for CLI support
```bash
pip install -e .
```
### Command Line
If installed locally:
```bash
pairs-trader --traindates 2020-01-01 2021-01-01 --testdates 2023-01-01 2023-07-01 --traininterval 1d --testinterval 1d
```
Otherwise, run with Python directly:
```bash
python main.py --traindates 2018-01-01 2020-12-31 --testdates 2023-01-01 2025-07-01 --traininterval 1d --testinterval 1d
```

## Limitations
- **Survivorship Bias**: The pair selection logic uses stocks from the current S&P500, which means that there can be survivorship bias in stock selection (i.e. stocks of companies that have gone bankrupt are not listed). This may lead to an overestimate of profitability in backtesting.

- **Data Limitations** Intraday data from yfinance is only available for the past week, limiting the ability to work with high-frequency strategies.

## Next Steps

I would like to experiment with more strategies to hopefully find ways to improve performance. For one, I would like to implement rolling hedge ratios instead of using the one established during trading.

I plan to extend this project to a statistical arbitrage backtester. You can find that project at [colebe/stat-arb](https://github.com/colebe/stat-arb) when it is complete.
