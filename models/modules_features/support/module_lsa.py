import sys

import pandas       as pd
import numpy        as np

from typing         import List

if sys.version_info[0] == 3 and sys.version_info[1] >= 8: from numpy.typing   import NDArray
else: NDArray = List

# Local Modules - Auxiliary
import modules_aux.module_nlp    as module_nlp
# Local Modules - Corpora
import modules_corpora.module_gensim    as module_gensim

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = 0.0
NUMBER_OF_WORDS_PER_BAG : int = 5

# =================================== PRIVATE METHODS ===================================

def compute_coherence_score(embeddings: List[NDArray[np.float64]], group_jump: int) -> float:
    current_scores : List[float] = []
    for index in range(0, len(embeddings) - group_jump, 1):
        embedding_1 : NDArray[np.float64] = embeddings[index]
        embedding_2 : NDArray[np.float64] = embeddings[index + group_jump]
        cossine_score : float = module_nlp.embeddings_cossine_similarity(embedding_1, embedding_2)
        if (type(cossine_score) == int or type(cossine_score) == float) and not np.isnan(cossine_score):
            current_scores.append(cossine_score)

    if len(current_scores) == 0: return DEFAULT_VALUE
    return sum(current_scores) / len(current_scores)

# =================================== PUBLIC METHODS ===================================

def lsa_analysis(basis_dataframe: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'latent semantic analysis' analysis ...")
    lsa_model = module_gensim.ModelLSA()

    # Preparation for LSA Coherence computation
    basis_dataframe['LSA - Word Groups'] = basis_dataframe['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    basis_dataframe['LSA - Embedding per Word Groups'] = basis_dataframe['LSA - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, lsa_model))
    basis_dataframe['LSA - Embedding Groups'] = basis_dataframe['LSA - Embedding per Word Groups'].progress_apply(module_nlp.average_embedding_per_group)
    # LSA Coherence scores
    basis_dataframe['LSA - First Order Coherence'] = basis_dataframe['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 1)).astype(float)
    basis_dataframe['LSA - Second Order Coherence'] = basis_dataframe['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 2)).astype(float)
    
    return basis_dataframe
