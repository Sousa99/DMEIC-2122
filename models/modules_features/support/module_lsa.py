import numpy        as np
import pandas       as pd

from typing import List
from numpy.typing import NDArray

# Local Modules - Auxiliary
import modules_aux.module_nlp    as module_nlp
# Local Modules - Corpora
import modules_corpora.module_gensim    as module_gensim

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = 0.0
NUMBER_OF_WORDS_PER_BAG : int = 5

# =================================== PRIVATE METHODS ===================================

def embeddings_cossine_similarity(embedding_1: NDArray[np.float64], embedding_2: NDArray[np.float64]) -> float:
    dot_product : float = np.dot(embedding_1, embedding_2)
    normal_product : float = np.linalg.norm(embedding_1) * np.linalg.norm(embedding_2)
    return dot_product / normal_product

def compute_coherence_score(embeddings: List[NDArray[np.float64]], group_jump: int) -> float:
    current_scores : List[float] = []
    for index in range(0, len(embeddings) - group_jump, 1):
        embedding_1 : NDArray[np.float64] = embeddings[index]
        embedding_2 : NDArray[np.float64] = embeddings[index + group_jump]
        current_scores.append(embeddings_cossine_similarity(embedding_1, embedding_2))

    if len(current_scores) == 0: return DEFAULT_VALUE
    return sum(current_scores) / len(current_scores)

# =================================== PUBLIC METHODS ===================================

def lsa_analysis(structure_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'Latent Semantic Analysis' analysis ...")
    lsa_model = module_gensim.ModelLSA()

    # Preparation for LSA Coherence computation
    structure_df['LSA - Word Groups'] = structure_df['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    structure_df['LSA - Embedding per Word Groups'] = structure_df['LSA - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, lsa_model))
    structure_df['LSA - Embedding Groups'] = structure_df['LSA - Embedding per Word Groups'].progress_apply(module_nlp.average_embedding_per_group)
    # LSA Coherence scores
    structure_df['LSA - First Order Coherence'] = structure_df['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 1)).astype(float)
    structure_df['LSA - Second Order Coherence'] = structure_df['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 2)).astype(float)
    
    return structure_df