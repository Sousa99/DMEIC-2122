from typing                             import Any, Dict, List, Optional, Tuple

import pandas                           as pd
import numpy                            as np
import numpy.typing                     as npt

# Local Modules - Auxiliary
import modules_aux.module_nlp           as module_nlp
# Local Modules - Corpora
import modules_corpora.module_gensim    as module_gensim

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = -1.0
NUMBER_OF_WORDS_PER_BAG : int = 15
PERCENTAGE_OF_MOST_FREQUENT_WORDS : float = 0.95

# =================================== PRIVATE METHODS ===================================

def get_top_words(model: module_gensim.ModelWord2Vec, percentage: float) -> List[str]:
    number_of_words     : int = round(model.get_vocab_size() * percentage)
    model_vocab_words   : List[str] = model.get_vocab_by_frequency()

    most_frequent_words : List[str] = model_vocab_words[:number_of_words]
    return most_frequent_words

# =================================== PUBLIC METHODS ===================================

def lca_analysis(basis_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'Latent Content Analysis' analysis ...")
    word2vec_model = module_gensim.ModelWord2Vec()

    # Preparation for LCA features
    basis_df['LCA - Word Groups'] = basis_df['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    basis_df['LCA - Embedding per Word Groups'] = basis_df['LCA - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, word2vec_model))
    basis_df['LCA - Embedding Groups'] = basis_df['LCA - Embedding per Word Groups'].progress_apply(module_nlp.sum_normalize_embedding_per_group)
    
    return basis_df

def lca_analysis_dynamic(train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    word2vec_model = module_gensim.ModelWord2Vec()
    model_frequent_words : List[str] = get_top_words(word2vec_model, PERCENTAGE_OF_MOST_FREQUENT_WORDS)

    # LCA features

    exit()
    
    return basis_df