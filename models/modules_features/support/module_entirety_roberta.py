from pyexpat import model
from typing                                 import List, Optional, Tuple

import pandas                               as pd

# Local Modules - Auxiliary
import modules_aux.module_aux               as module_aux
import modules_aux.module_exporter          as module_exporter
import modules_aux.module_transformers      as module_transformers

# =================================== CONSTANTS DEFINITIONS ===================================

DEFAULT_VALUE                       : float     = 0
NUMBER_OF_WORDS_PER_BAG             : int       = 15
PERCENTAGE_OF_MOST_FREQUENT_WORDS   : float     = 0.95
NUMBER_WORDS_FOR_CLUSTERING         : int       = 50
NUMBER_CLUSTERS_TO_TEST             : List[int] = [ x for x in range(3, 11) ]

# =================================== PRIVATE METHODS ===================================



# =================================== PUBLIC METHODS ===================================

def entirety_roberta_analysis(basis_df: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'entirety roberta' analysis ...")
    return basis_df

def entirety_roberta_analysis_dynamic(train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:

    train_texts     : pd.Series = train_X['Text'].apply(lambda list_of_words: ' '.join(list_of_words))
    train_labels    : pd.Series = train_Y

    module_exporter.push_current_directory('Entirety Roberta Model')
    output_dir      : str   = module_exporter.get_current_path()
    module_exporter.pop_current_directory()
    module_exporter.push_current_directory('Entirety Roberta Logs')
    logging_dir      : str  = module_exporter.get_current_path()
    module_exporter.pop_current_directory()

    training_args           = module_transformers.get_training_args(output_dir, logging_dir)
    tokenizer, model_base   = module_transformers.get_xlm_roberta_large()

    model   : module_transformers.TransformerModel  = module_transformers.TransformerModel(tokenizer, model_base)
    
    model.train(train_texts, train_labels, training_args)
    model.load_saved_model()

    train_return = model.predict(train_texts)
    train_return.columns = list(map(lambda column: 'Entirety RoBERTa' + ' - ' + column, train_return.columns.to_list()))
    train_X = module_aux.join_dataframes(train_X, train_return)

    if test_X is not None:
        test_texts  : pd.Series = test_X['Text'].apply(lambda list_of_words: ' '.join(list_of_words))
        test_return = model.predict(test_texts)
        test_return.columns = list(map(lambda column: 'Entirety RoBERTa' + ' - ' + column, test_return.columns.to_list()))
        test_X = module_aux.join_dataframes(test_X, test_return)
    
    del training_args, tokenizer, model_base, model
    return (train_X, test_X)