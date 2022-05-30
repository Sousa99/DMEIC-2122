from typing                                 import List, Optional

import pandas                               as pd

# Local Modules - Corpora
import modules_corpora.module_sentilex      as module_sentilex

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE   : float = 0.0

# =================================== PRIVATE METHODS ===================================

def process_sentilex_multiple_words(words: List[str], model: module_sentilex.ModelSentiLex) -> List[float]:
    scores                      : List[Optional[int]]   = list(map(lambda word: model.get_word_valence(word), words))
    scores_filtered             : List[int]             = list(filter(lambda score: score is not None, scores))
    scores_filtered_converted   : List[float]           = list(map(lambda score: float(score), scores_filtered))

    return scores_filtered_converted

# =================================== PUBLIC METHODS ===================================

def sentilex_analysis(basis_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'sentilex' analysis ...")
    model_sentilex : module_sentilex.ModelSentiLex = module_sentilex.ModelSentiLex()

    # Extract SentiLex features
    basis_df['SentiLex - Extracted Scores'] = basis_df['Lemmatized Filtered Text'].progress_apply(lambda words: process_sentilex_multiple_words(words, model_sentilex))
    basis_df['SentiLex - avg Score']        = basis_df['SentiLex - Extracted Scores'].progress_apply(lambda scores: sum(scores, DEFAULT_VALUE) / len(scores) if len(scores) != 0 else DEFAULT_VALUE).astype(float)
    basis_df['SentiLex - number Scores']    = basis_df['SentiLex - Extracted Scores'].progress_apply(lambda scores: len(scores)).astype(int)

    del model_sentilex
    return basis_df