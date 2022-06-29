import sys

from typing                                 import Any, Dict, Iterable, List, Optional, Tuple
from functools                              import reduce

import pandas                               as pd
import numpy                                as np

# Local Modules - Auxiliary
import modules_aux.module_aux               as module_aux
import modules_aux.module_nlp               as module_nlp
import modules_aux.module_exporter          as module_exporter
import modules_aux.module_clustering        as module_clustering
# Local Modules - Corpora
import modules_corpora.module_gensim        as module_gensim
import modules_corpora.module_gensim_util   as module_gensim_util

NDArray = Iterable

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE                       : float     = 0
NUMBER_OF_WORDS_PER_BAG             : int       = 15
PERCENTAGE_OF_MOST_FREQUENT_WORDS   : float     = 0.95
NUMBER_WORDS_FOR_CLUSTERING         : int       = 50
NUMBER_CLUSTERS_TO_TEST             : List[int] = [ x for x in range(3, 11) ]

# =================================== PRIVATE METHODS ===================================

def get_top_words(model: module_gensim.ModelWord2Vec, percentage: float, blacklist_top_words: List[str] = []) -> List[str]:
    number_of_words     : int = round(model.get_vocab_size() * percentage)
    model_vocab_words   : List[str] = model.get_vocab_by_frequency()

    most_frequent_words : List[str] = list(filter(lambda item: item not in blacklist_top_words, model_vocab_words))
    most_frequent_words : List[str] = most_frequent_words[:number_of_words]
    return most_frequent_words

def get_max_cossine_similarity_with_word(sentence_embeddings: List[NDArray[np.float64]], word_embedding: NDArray[np.float64]) -> Optional[float]:

    max_cossine : Optional[float] = None
    for sentece_embedding in sentence_embeddings:
        cossine_score = module_nlp.embeddings_cossine_similarity(sentece_embedding, word_embedding)
        if max_cossine is None or max_cossine < cossine_score:
            max_cossine = cossine_score

    return max_cossine

def get_max_cossine_similarity_freq_words(sentence_embeddings: List[NDArray[np.float64]], most_frequent_words: List[Tuple[str, NDArray[np.float64]]]) -> Dict[str, float]:
    max_cossine_dictionary : Dict[str, float] = {}
    for (frequent_word, frequent_embedding) in most_frequent_words:
        max_cossine = get_max_cossine_similarity_with_word(sentence_embeddings, frequent_embedding)
        if max_cossine is not None:
            max_cossine_dictionary[frequent_word] = max_cossine

    return max_cossine_dictionary

# =================================== PUBLIC METHODS ===================================

def lca_analysis(basis_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'latent content analysis' analysis ...")
    word2vec_model = module_gensim.ModelWord2Vec()
    model_frequent_words : List[str] = get_top_words(word2vec_model, PERCENTAGE_OF_MOST_FREQUENT_WORDS, ['Target'])
    model_frequent_word_embeddings : List[Tuple[str, NDArray]] = list(map(lambda word: (word, module_nlp.convert_word_to_embedding(word, word2vec_model)), model_frequent_words))
    
    # Preparation for LCA features
    basis_df['LCA - Word Groups'] = basis_df['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    basis_df['LCA - Embedding per Word Groups'] = basis_df['LCA - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, word2vec_model))
    basis_df['LCA - Embedding Groups'] = basis_df['LCA - Embedding per Word Groups'].progress_apply(module_nlp.sum_normalize_embedding_per_group)
    basis_df['LCA - Max Cossine w/ Frequent Words'] = basis_df['LCA - Embedding Groups'].progress_apply(lambda sentence_embeddings: get_max_cossine_similarity_freq_words(sentence_embeddings, model_frequent_word_embeddings))

    drop_columns : List[str] = ['LCA - Word Groups', 'LCA - Embedding per Word Groups']
    basis_df = basis_df.drop(drop_columns, axis=1, errors='ignore')

    del word2vec_model
    return basis_df

def lca_analysis_dynamic(train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    train_full_df : pd.DataFrame = module_aux.join_dataframes(train_X, train_Y.to_frame('Target'))

    word2vec_model = module_gensim.ModelWord2Vec()

    lca_cossines_matrix = train_full_df[['Target', 'LCA - Max Cossine w/ Frequent Words']].copy()
    lca_cossines_matrix = pd.concat([lca_cossines_matrix.drop(['LCA - Max Cossine w/ Frequent Words'], axis=1),
        lca_cossines_matrix['LCA - Max Cossine w/ Frequent Words'].apply(pd.Series)], axis=1)
    grouped_by_lca_cossines : pd.DataFrame = lca_cossines_matrix.groupby('Target').mean().transpose()

    # Achieved grouped by target dataframe
    grouped_by_df : pd.DataFrame = train_full_df.groupby('Target')['Lemmatized Filtered Text'].apply(list).to_frame('Lemmatized Filtered Documents')
    grouped_by_df['Lemmatized Filtered Text'] = grouped_by_df['Lemmatized Filtered Documents'].apply(lambda documents: reduce(lambda d1, d2: d1 + d2, documents))

    # Achieve tdidf model
    list_of_documents   : List[List[str]]               = grouped_by_df['Lemmatized Filtered Text'].to_list()
    tdidf_model         : module_gensim_util.ModelTDIDF = module_gensim_util.ModelTDIDF(list_of_documents)

    # Define variation for cluster creation
    clusters_to_study   : Dict[str, Any]                = [
        { 'code':   'target',       'full_code':    'Target',       'target_column':    True,   'non_target_column':    False   },
        { 'code':   'non-target',   'full_code':    'Non-Target',   'target_column':    False,  'non_target_column':    True    },
    ]

    for cluster_to_study in clusters_to_study:

        # Achieve tdidf model
        tdidf_document      : Dict[str, float]              = tdidf_model.process_document(grouped_by_df.loc[cluster_to_study['target_column'], 'Lemmatized Filtered Text'])

        # Select words based on scores
        word_importance             : pd.Series = grouped_by_lca_cossines.progress_apply(lambda row: row[cluster_to_study['target_column']] / row[cluster_to_study['non_target_column']], axis=1).sort_values(ascending=False)
        word_importance_tdidf       : pd.Series = grouped_by_lca_cossines.progress_apply(lambda row: tdidf_document[row.name] * (row[cluster_to_study['target_column']] / row[cluster_to_study['non_target_column']]) if row.name in tdidf_document else 0.0, axis=1).sort_values(ascending=False)
        list_of_words_sorted        : List[str] = list(filter(lambda word: word2vec_model.word_in_model(word), word_importance_tdidf.index))

        selected_words              : List[str]                     = list_of_words_sorted[:NUMBER_WORDS_FOR_CLUSTERING]
        selected_words_embeddings   : List[NDArray[np.float64]] = list(map(lambda word: module_nlp.convert_word_to_embedding(word, word2vec_model), selected_words))
        
        # Predict Clusters and Reduce Dimensionality
        predicted_clusters, cluster_centers = module_clustering.cluster_word_embeddings(selected_words_embeddings, NUMBER_CLUSTERS_TO_TEST)
        reduced_dimensionality = module_clustering.reduce_data_dimensionality_to(selected_words, selected_words_embeddings,
            predicted_clusters, cluster_centers, [ "Feature 1", "Feature 2" ])

        # Plot and Save achieved Clusters
        module_exporter.export_scatter_clusters(f"content - lca - {cluster_to_study['code']} - train - achieved clusters", reduced_dimensionality, 'Feature 1', 'Feature 2',
            hue_key='Cluster', style_key='Type', hide_labels=('Type', 'center'), figsize=(10, 6),
            legend_placement='upper left', margins={ 'bottom': None, 'left': 0.1, 'top': None, 'right': 0.85 })

        # LCA features applied to train
        for index, cluster_center in enumerate(cluster_centers):
            column_name : str   = f'LCA - Max Cossine w/ Cluster {index}'
            train_X[column_name] = train_X['LCA - Embedding Groups'].progress_apply(lambda sentence_embeddings: get_max_cossine_similarity_with_word(sentence_embeddings, cluster_center)).astype(float)
            train_X[column_name].fillna(DEFAULT_VALUE, inplace=True)
        
        # LCA features applied to test
        if test_X is not None:
            for index, cluster_center in enumerate(cluster_centers):
                column_name : str   = f"LCA - Max Cossine w/ Cluster {index} for {cluster_to_study['full_code']}"
                test_X[column_name] = test_X['LCA - Embedding Groups'].progress_apply(lambda sentence_embeddings: get_max_cossine_similarity_with_word(sentence_embeddings, cluster_center)).astype(float)
                test_X[column_name].fillna(DEFAULT_VALUE, inplace=True)

    del word2vec_model
    return (train_X, test_X)
