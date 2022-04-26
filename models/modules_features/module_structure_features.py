import os

import pandas as pd

from typing import List
from functools import reduce

# Local Modules - Features
import modules_features.support.module_lsa                  as module_lsa
import modules_features.support.module_word_graph           as module_word_graph
import modules_features.support.module_vector_unpacking     as module_vector_unpacking
# Local Modules - Auxiliary
import modules_aux.module_aux                               as module_aux
import modules_aux.module_nlp                               as module_nlp
import modules_aux.module_load                              as module_load

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def structure_analysis(paths_df: pd.DataFrame, preference_trans: List[str], trans_extension: str) -> pd.DataFrame:
    print("🚀 Processing 'structure' analysis ...")
    lemmatizer : module_nlp.LemmatizerStanza = module_nlp.LemmatizerStanza()

    # Dataframe to study speech features
    structure_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path']]
    # Choose trans files from dictionary
    structure_df['Trans File'] = structure_df['Trans Path'].apply(module_aux.compute_file_paths, args=(preference_trans, trans_extension))
    structure_df = structure_df.drop(structure_df[structure_df['Trans File'].isnull()].index)
    structure_df['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(structure_df['Trans Path'], structure_df['Trans File']))))
    # Process Transcriptions
    structure_df['Trans Info'] = structure_df['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))
    structure_df['Lemmatized Text'] = structure_df['Trans Info'].apply(lambda trans_info: trans_info.lemmatize_words(lemmatizer))
    structure_df['Lemmatized Filtered Text'] = structure_df['Lemmatized Text'].apply(module_nlp.filter_out_stop_words)

    # Word Graph Features
    word_graph_df = module_word_graph.word_graph_analysis(structure_df.copy(deep=True))
    # LSA Coherence Features
    lsa_df = module_lsa.lsa_analysis(structure_df.copy(deep=True))
    # Vector Unpacking Features
    vector_unpacking_df = module_vector_unpacking.vector_unpacking_analysis(structure_df.copy(deep=True))
    
    # Final Dataframe
    all_structure_dataframes : List[pd.DataFrame] = [word_graph_df, lsa_df, vector_unpacking_df]
    all_structure_df = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), all_structure_dataframes)

    print("✅ Finished processing 'structure' analysis!")
    return all_structure_df