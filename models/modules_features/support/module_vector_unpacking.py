import sys

from typing                             import Any, Dict, Iterable, List

import pandas                           as pd
import numpy                            as np

# Local Modules - Auxiliary
import modules_aux.module_nlp           as module_nlp
import modules_aux.module_keras         as module_keras
# Local Modules - Corpora
import modules_corpora.module_gensim    as module_gensim

NDArray = Iterable

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = -1.0
NUMBER_OF_WORDS_PER_BAG : int = 30
NUMBER_OF_EPHOCS : int = 5000

# =================================== PRIVATE METHODS ===================================

def create_models(groups_of_embeddings: List[List[NDArray[np.float64]]], sentence_embeddings: List[NDArray[np.float64]]) -> List[module_keras.NeuralNetworkRezaii]:

    models_list : List[module_keras.NeuralNetworkRezaii] = []
    for (group_of_embeddings, sentence_embedding) in zip(groups_of_embeddings, sentence_embeddings):
        matrix_embeddings : NDArray[np.float64] = module_nlp.convert_embeddings_to_matrix(group_of_embeddings)
        model : module_keras.NeuralNetworkRezaii = module_keras.NeuralNetworkRezaii(matrix_embeddings, sentence_embedding, ephocs=NUMBER_OF_EPHOCS)
        models_list.append(model)

    return models_list

def train_models(models: List[module_keras.NeuralNetworkRezaii]) -> pd.Series:
    
    number_models : int = len(models)
    dictionary_fixed : Dict[str, Any] = {}

    for model in models:
        model_result : Dict[str, Any] = model.train_model()
        for result_key in model_result:
            result : Any = model_result[result_key]
            code : str =  'Vector Unpacking - avg ' + result_key

            if code not in dictionary_fixed: dictionary_fixed[code] = 0
            dictionary_fixed[code] = dictionary_fixed[code] + result / number_models

    result_series = pd.Series(dictionary_fixed)
    return result_series

def create_and_train_models(groups_of_embeddings: List[List[NDArray[np.float64]]], sentence_embeddings: List[NDArray[np.float64]]) -> pd.Series:
    
    models_list : List[module_keras.NeuralNetworkRezaii] = create_models(groups_of_embeddings, sentence_embeddings)
    result_trained_models : pd.Series = train_models(models_list)
    return result_trained_models

# =================================== PUBLIC METHODS ===================================

def vector_unpacking_analysis(basis_dataframe: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'vector unpacking' analysis ...")
    word2vec_model = module_gensim.ModelWord2Vec()

    # Preparation for Vector Unpacking features
    basis_dataframe['Vector Unpacking - Word Groups'] = basis_dataframe['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    basis_dataframe['Vector Unpacking - Embedding per Word Groups'] = basis_dataframe['Vector Unpacking - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, word2vec_model))
    basis_dataframe['Vector Unpacking - Embedding Groups'] = basis_dataframe['Vector Unpacking - Embedding per Word Groups'].progress_apply(module_nlp.sum_normalize_embedding_per_group)
    # Vector Unpacking features
    rezaii_model_df : pd.DataFrame = basis_dataframe.progress_apply(lambda row: create_and_train_models(row['Vector Unpacking - Embedding per Word Groups'], row['Vector Unpacking - Embedding Groups']), axis=1)
    basis_dataframe = basis_dataframe.merge(rezaii_model_df.fillna(DEFAULT_VALUE, inplace=False), left_index=True, right_index=True)
    
    del word2vec_model
    return basis_dataframe