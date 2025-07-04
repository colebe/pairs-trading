from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd

def select_pairs(data, variance_threshold=0.95, n_clusters=25):
    """
    Select pairs of stocks based on PCA and agglomerative clustering.

    Parameters:
        data (pd.DataFrame): DataFrame containing historical close prices of stocks (symbols as columns, time as index).
        n_clusters (int): Number of clusters to form.
    Returns:
        Dict [int, List[Tuple[str, str]]]: Dictionary mapping cluster labels to lists of stock symbol pairs for cointegration testing.
    """
    
    # Calculate scaled log returns
    log_returns = np.log(data / data.shift(1)).dropna()
    X = log_returns.T
    scaler = StandardScaler()
    scaled_returns = scaler.fit_transform(X)
    
    # Perform PCA to reduce dimensionality
    pca = PCA(n_components=variance_threshold)
    X = pca.fit_transform(scaled_returns)
    
    # Perform agglomerative clustering
    clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    clustering.fit_predict(X)
    tickers = log_returns.columns
    label_dict = {i: [] for i in range(n_clusters)}
    for i, label in enumerate(clustering.labels_):
        label_dict[label].append(tickers[i])
    
    # Get two most similar tickers from each cluster with more than 1 ticker
    similar_tickers = {}
    for label, tickers in label_dict.items():
        if len(tickers) > 1:
            # Calculate pairwise correlation matrix for tickers in the cluster
            cluster_data = data[tickers]
            corr_matrix = cluster_data.corr()
            
            # Get the two most similar tickers based on correlation
            most_similar = corr_matrix.unstack().sort_values(ascending=False)
            most_similar = most_similar[most_similar < 1]  # Exclude self-correlations
            top_pairs = most_similar.head(2).index.tolist()
            
            similar_tickers[label] = top_pairs
    
    return similar_tickers
