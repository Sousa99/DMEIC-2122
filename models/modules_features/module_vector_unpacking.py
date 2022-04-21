import pandas       as pd

# Local Modules - Auxiliary
import modules_aux.module_nlp           as module_nlp
# Local Modules - Corpora
import modules_corpora.module_gensim    as module_gensim

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE : float = 0.0
NUMBER_OF_WORDS_PER_BAG : int = 30

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def vector_unpacking_analysis(structure_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'Vector Unpacking' analysis ...")
    word2vec_model = module_gensim.ModelWord2Vec()

    # Preparation for Vector Unpacking features
    structure_df['Vector Unpacking - Word Groups'] = structure_df['Lemmatized Filtered Text'].progress_apply(lambda words: module_nlp.subdivide_bags_of_words(words, NUMBER_OF_WORDS_PER_BAG))
    structure_df['Vector Unpacking - Embedding per Word Groups'] = structure_df['Vector Unpacking - Word Groups'].progress_apply(lambda groups_of_words: module_nlp.convert_groups_of_words_to_embeddings(groups_of_words, word2vec_model))
    structure_df['Vector Unpacking - Embedding Groups'] = structure_df['Vector Unpacking - Embedding per Word Groups'].progress_apply(module_nlp.average_embedding_per_group)
    # Vector Unpacking features
    
    return structure_df