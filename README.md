# Pairs Trading Backtester
This project uses cointegration analysis and z-scoring to backtest mean-reverting **pairs trading strategies**. It uses historical price data from `yfinance`, and evaluates performance with metrics like Sharpe ratio, cumulative returns, and drawdowns.

## Overview


## Methodology
I used the Engle-Granger Test to test for cointegration between two stock prices, with the Augmented Dickey-Fuller test to test for stationarity. For price selection, I used Principal Component Analysis (PCA) and K-means clustering.

## Example Results

## Limitations
The pair selection logic uses stocks from the current S&P500, which means that there is survivorship bias in stock selection (i.e. stocks of companies that have gone bankrupt are not listed). This may lead to an overestimate of profitability.

## Next Steps
I plan to extend this project to a statistical arbitrage backtester. You can find that project at [text](https://github.com/colebe/stat-arb-backtesting) when it is complete.