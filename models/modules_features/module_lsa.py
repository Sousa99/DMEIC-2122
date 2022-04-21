import numpy        as np
import pandas       as pd

from typing import List, Optional
from numpy.typing import NDArray

# Local Modules - Auxiliary
import modules_corpora.module_gensim    as module_gensim

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = 0.0
NUMBER_OF_WORDS_PER_BAG : int = 5

# =================================== PRIVATE METHODS ===================================

def subdivide_transcription_words(words: List[str]) -> List[List[str]]:
    # Bag of Words Approach
    groups_of_words : List[List[str]] = [words[x : x + NUMBER_OF_WORDS_PER_BAG ] for x in range(0, len(words), NUMBER_OF_WORDS_PER_BAG)]
    return groups_of_words

def convert_words_to_embeddings(group_of_words: List[str], model: module_gensim.ModelCorpora) -> List[NDArray[np.float64]]:
    embeddings : List[Optional[NDArray[np.float64]]] = list(map(lambda word: model.get_word_embedding(word), group_of_words))
    embeddings_filtered : List[NDArray[np.float64]] = list(filter(lambda embedding: embedding is not None, embeddings))
    return embeddings_filtered

def convert_groups_of_words_to_embeddings(groups_of_words: List[List[str]], model: module_gensim.ModelCorpora) -> List[List[NDArray[np.float64]]]:
    embeddings_per_group : List[List[NDArray[np.float64]]] = list(map(lambda group_of_words: convert_words_to_embeddings(group_of_words, model), groups_of_words))
    embeddings_per_group_filtered : List[List[NDArray[np.float64]]] = list(filter(lambda group_of_embeddings: len(group_of_embeddings) != 0, embeddings_per_group))
    return embeddings_per_group_filtered

def average_embedding_per_group(groups_of_embeddings: List[List[NDArray[np.float64]]]) -> List[NDArray[np.float64]]:
    avg_embedding_per_group : List[NDArray[np.float64]] = list(map(lambda group_of_embedding: np.mean(np.array(group_of_embedding), axis=0), groups_of_embeddings))
    return avg_embedding_per_group

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
    print("🚀 Processing 'LSA' analysis ...")
    lsa_model = module_gensim.ModelLSA()

    # Preparation for LSA Coherence computation
    structure_df['LSA - Word Groups'] = structure_df['Lemmatized Filtered Text'].progress_apply(subdivide_transcription_words)
    structure_df['LSA - Embedding per Word Groups'] = structure_df['LSA - Word Groups'].progress_apply(lambda groups_of_words: convert_groups_of_words_to_embeddings(groups_of_words, lsa_model))
    structure_df['LSA - Embedding Groups'] = structure_df['LSA - Embedding per Word Groups'].progress_apply(average_embedding_per_group)
    # LSA Coherence scores
    structure_df['LSA - First Order Coherence'] = structure_df['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 1)).astype(float)
    structure_df['LSA - Second Order Coherence'] = structure_df['LSA - Embedding Groups'].progress_apply(lambda embeddings: compute_coherence_score(embeddings, 2)).astype(float)
    
    return structure_df