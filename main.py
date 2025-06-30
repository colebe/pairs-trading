import argparse
from loader import get_data
from cointegration import engle_granger
from backtesting import backtest, zscore

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbols', nargs=2, required=True)
    parser.add_argument('--traindates', nargs=2, required=True)
    parser.add_argument('--testdates', nargs=2, required=True)
    parser.add_argument('--interval', default='1d')
    args = parser.parse_args()
    
    symbol1, symbol2 = args.symbols
    train_start_date = args.traindates[0]
    train_end_date = args.traindates[1]
    test_start_date = args.testdates[0]
    test_end_date = args.testdates[1]
    time_interval = args.interval

    
    ...
    
if __name__ == "__main__":
    main()