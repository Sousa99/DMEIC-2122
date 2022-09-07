import pandas                               as pd

# Local Modules - Auxiliary
import modules_aux.module_transformers      as module_transformers

# =================================== CONSTANTS DEFINITIONS ===================================

VALENCE_ROBERTA_MODEL_PATH  : str   = '../models_support/exports/web_scraping/results/valence_roberta'

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def valence_roberta_analysis(basis_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'valence roberta' analysis ...")

    tokenizer, _   = module_transformers.get_xlm_roberta_base(1)
    model = module_transformers.TransformerModel(tokenizer, None, VALENCE_ROBERTA_MODEL_PATH)

    texts = basis_df['Text'].apply(lambda list_of_words: ' '.join(list_of_words))
    results_series = model.predict(texts).iloc[:, 0]

    basis_df['Valence RoBERTa Score'] = results_series
    return basis_df