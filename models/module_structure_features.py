import os

import pandas as pd
import networkx as nx

from tqdm import tqdm
from typing import List, Optional

# Local Modules
import module_load
import module_exporter

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

def compute_word_graph(trans_info: module_load.TranscriptionInfo) -> nx.DiGraph:

    word_graph = nx.DiGraph()
    last_word : Optional[str] = None
    for transcription_line in trans_info.get_info_items():
        words : List[str] = transcription_line.get_words().split()
        for next_word in words:
            if last_word is not None:
                word_graph.add_edge(last_word, next_word)
            last_word = next_word

    return word_graph

def compute_number_of_nodes(graph: nx.DiGraph) -> int: return graph.number_of_nodes()
def compute_number_of_edges(graph: nx.DiGraph) -> int: return graph.number_of_edges()

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

    # Features - Word Graph
    structure_df['Word Graph'] = structure_df['Trans Info'].progress_apply(compute_word_graph)
    structure_df['Word Graph - Nr Nodes'] = structure_df['Word Graph'].progress_apply(compute_number_of_nodes)
    structure_df['Word Graph - Nr Edges'] = structure_df['Word Graph'].progress_apply(compute_number_of_edges)

    # ================================================================ EXPORT GRAPHS ================================================================
    # = module_exporter.change_current_directory(['tmp'])
    # = for subject, task, graph in tqdm(list(zip(structure_df['Subject'], structure_df['Task'], structure_df['Word Graph'])), desc="🎨 Exporting Graphs", leave=True):
    # =     code = subject[0]
    # =     module_exporter.change_current_directory(['tmp', task, code])
    # =     module_exporter.export_word_graph(f'{subject}-{task}', graph, figsize=(30, 12), with_labels=True)

    print("✅ Finished processing 'structure' analysis!")
    return structure_df