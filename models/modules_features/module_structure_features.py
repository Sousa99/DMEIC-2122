import os

import pandas as pd
import networkx as nx

from typing import List

# Local Modules - Features
import modules_features.module_word_graph   as module_word_graph
# Local Modules - Auxiliary
import modules_aux.module_aux   as module_aux
import modules_aux.module_load  as module_load

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def structure_analysis(paths_df: pd.DataFrame, preference_trans: List[str], trans_extension: str) -> pd.DataFrame:
    print("🚀 Processing 'structure' analysis ...")

    # Dataframe to study speech features
    structure_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path']]
    # Choose trans files from dictionary
    structure_df['Trans File'] = structure_df['Trans Path'].apply(module_aux.compute_file_paths, args=(preference_trans, trans_extension))
    structure_df = structure_df.drop(structure_df[structure_df['Trans File'].isnull()].index)
    structure_df['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(structure_df['Trans Path'], structure_df['Trans File']))))
    # Process Transcriptions
    structure_df['Trans Info'] = structure_df['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))

    # Word Graph Features
    structure_df = module_word_graph.word_graph_analysis(structure_df)

    print("✅ Finished processing 'structure' analysis!")
    return structure_df