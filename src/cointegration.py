import numpy as np
from statsmodels.tsa.stattools import adfuller

def engle_granger(series1, series2):
    """
    Perform the Engle-Granger cointegration test on two time series.
    Parameters:
        series1 (pd.Series): First time series.
        series2 (pd.Series): Second time series.
    Returns:
        tuple: (ADF test statistic, p-value, critical values)
    """
    X = series1.to_numpy()
    Y = series2.to_numpy()
    # Add constant term for regression
    X = np.column_stack((np.ones(X.shape[0]), X))
    # Regress Y on X to find beta_hat
    beta_hat = np.linalg.inv(X.T @ X) @ X.T @ Y
    # Calculate the Residuals (spread)
    Y_hat = X @ beta_hat
    spread = Y - Y_hat
    # Perform the ADF test on the spread
    adf_result = adfuller(spread)
    adf_statistic = adf_result[0]
    p_value = adf_result[1]
    critical_values = adf_result[4]
    
    return adf_statistic, p_value, critical_values, beta_hat[1]  # Return beta_hat as well for further use in main