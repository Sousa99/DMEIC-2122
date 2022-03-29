import os

import pandas as pd
import networkx as nx

from typing import List

import modules_aux.module_load as module_load
# Local Modules - Features
import modules_features.module_word_graph   as module_word_graph
# Local Modules - Auxiliary

# =================================== PRIVATE METHODS ===================================

def compute_file_paths(file_path: str, extension_preference_order: List[str], extension: str):

    _, _, files_full = list(os.walk(file_path))[0]
    if extension != None: files_full = list(filter(lambda file: os.path.splitext(file)[1] == extension, files_full))
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    if len(files) == 0: return None
    return files[0][0]

# =================================== PUBLIC METHODS ===================================

def structure_analysis(paths_df: pd.DataFrame, preference_trans: List[str], trans_extension: str) -> pd.DataFrame:
    print("🚀 Processing 'structure' analysis ...")

    # Dataframe to study speech features
    structure_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path']]
    # Choose trans files from dictionary
    structure_df['Trans File'] = structure_df['Trans Path'].apply(compute_file_paths, args=(preference_trans, trans_extension))
    structure_df = structure_df.drop(structure_df[structure_df['Trans File'].isnull()].index)
    structure_df['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(structure_df['Trans Path'], structure_df['Trans File']))))
    # Process Transcriptions
    structure_df['Trans Info'] = structure_df['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))

    # Word Graph Features
    structure_df = module_word_graph.word_graph_analysis(structure_df)

    print("✅ Finished processing 'structure' analysis!")
    return structure_df