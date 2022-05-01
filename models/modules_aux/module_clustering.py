import math
import warnings
import sklearn.cluster
import sklearn.metrics
import sklearn.manifold

from typing                             import Dict, List, Optional, Tuple

import numpy                            as np
import pandas                           as pd
import numpy.typing                     as npt

# Local Modules - Auxiliary
import modules_aux.module_nlp           as module_nlp

# =================================== DOWNLOADS FOR LANGUAGE PROCESSING ===================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()

stanza.download('pt')
print()
'''
# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', module = 'sklearn')

# =================================== PRIVATE FUNCTIONS ===================================

def compute_mse(X: npt.NDArray[np.float64], labels: npt.NDArray[np.float64], centroids: npt.NDArray[np.float64]) -> float:
    n = len(X)
    centroid_per_record = [centroids[labels[i]] for i in range(n)]
    partial = X - centroid_per_record
    partial = list(partial * partial)
    partial = [sum(el) for el in partial]
    partial = sum(partial)
    return math.sqrt(partial / n)

def compute_mae(X: npt.NDArray[np.float64], labels: npt.NDArray[np.float64], centroids: npt.NDArray[np.float64]) -> float:
    n = len(X)
    centroid_per_record = [centroids[labels[i]] for i in range(n)]
    partial = abs(X - centroid_per_record)
    partial = [sum(el) for el in partial]
    partial = sum(partial)
    return partial / n

def predict_clustering(data: pd.DataFrame, number_clusters: int) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    cluster_model   : sklearn.cluster.KMeans    = sklearn.cluster.KMeans(n_clusters=number_clusters)
    prediction      : npt.NDArray[np.float64]   = cluster_model.fit_predict(data)

    return (prediction, cluster_model.cluster_centers_)

def compute_cluster_scores(data: pd.DataFrame, prediction: npt.NDArray[np.float64], cluster_centers: npt.NDArray[np.float64]) -> Dict[str, float]:

    mse             : float                     = compute_mse(data, prediction, cluster_centers)
    mae             : float                     = compute_mae(data, prediction, cluster_centers)
    silhouette      : float                     = sklearn.metrics.silhouette_score(data, prediction)

    return { 'mse': mse, 'mae': mae, 'silhouette': silhouette }

def test_multiple_clusters(data: pd.DataFrame, numbers_clusters: List[int]) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:

    best_result : Optional[Tuple[float, Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]]] = None
    for number_clusters in numbers_clusters:
        prediction, centers = predict_clustering(data, number_clusters)
        scores = compute_cluster_scores(data, prediction, centers)

        if best_result is None or scores['silhouette'] > best_result[0]:
            best_result = (scores['silhouette'], (prediction, centers))

    return best_result[1]

# =================================== PUBLIC FUNCTIONS ===================================

def cluster_word_embeddings(embeddings: List[npt.NDArray[np.float64]], numbers_clusters: List[int]) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:

    embeddings_as_data  : pd.DataFrame  = module_nlp.convert_embeddings_to_matrix(embeddings)

    prediction, cluster_centers = test_multiple_clusters(embeddings_as_data, numbers_clusters)
    return (prediction, cluster_centers)

def reduce_data_dimensionality_to(words: List[str], embeddings: List[npt.NDArray[np.float64]],
    predicted_clusters: npt.NDArray[np.float64], centers: npt.NDArray[np.float64], reduced_columns: List[str]) -> pd.DataFrame:

    embeddings_as_data  : pd.DataFrame          = pd.DataFrame(module_nlp.convert_embeddings_to_matrix(embeddings))
    centers_as_data     : pd.DataFrame          = pd.DataFrame(centers)
    entire_data         : pd.DataFrame          = pd.concat([embeddings_as_data, centers_as_data])

    mds_model           : sklearn.manifold.TSNE = sklearn.manifold.TSNE(n_components=len(reduced_columns), init='pca', perplexity=10, learning_rate='auto')
    reduced_data        : pd.DataFrame          = pd.DataFrame(mds_model.fit_transform(entire_data), columns = reduced_columns)

    reduced_data.index          = words + [ f'Center {index}' for index in range(len(centers)) ]
    reduced_data['Cluster']     = pd.Series(predicted_clusters.tolist() + [ index for index in range(len(centers)) ], index=reduced_data.index)
    reduced_data['Type']        = pd.Series([ 'point' for _ in range(len(words)) ] + [ 'center' for _ in range(len(centers)) ], index=reduced_data.index)
    return reduced_data

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================