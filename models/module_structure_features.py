import os

import pandas as pd
import networkx as nx

from tqdm import tqdm
from typing import List, Optional, Set

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

def compute_word_graph(trans_info: module_load.TranscriptionInfo) -> nx.MultiDiGraph:

    word_graph = nx.MultiDiGraph()
    last_word : Optional[str] = None
    for transcription_line in trans_info.get_info_items():
        words : List[str] = transcription_line.get_words().split()
        for next_word in words:
            if last_word is not None:
                word_graph.add_edge(last_word, next_word)
            last_word = next_word

    return word_graph

def compute_weakly_connected_components(graph: nx.MultiDiGraph) -> List[Set[str]]:
    generator = nx.weakly_connected_components(graph)
    weakly_connected_components = list(generator)
    return weakly_connected_components
def compute_strong_connected_components(graph: nx.MultiDiGraph) -> List[Set[str]]:
    generator = nx.strongly_connected_components(graph)
    strong_connected_components = list(generator)
    return strong_connected_components

def compute_number_of_nodes(graph: nx.MultiDiGraph) -> int: return graph.number_of_nodes()
def compute_number_of_edges(graph: nx.MultiDiGraph) -> int: return graph.number_of_edges()
def compute_connected_components_nodes_min(connected_components: List[Set[str]]):
    if len(connected_components) == 0: return 0
    return len(min(connected_components, key = lambda nodes_set: len(nodes_set)))
def compute_connected_components_nodes_avg(connected_components: List[Set[str]]):
    if len(connected_components) == 0: return 0
    return sum(len(cc) for cc in connected_components) / len(connected_components)
def compute_connected_components_nodes_max(connected_components: List[Set[str]]):
    if len(connected_components) == 0: return 0
    return len(max(connected_components, key = lambda set: len(set)))

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

    # Features - Word Graph - Acquire Structures
    structure_df['Word Graph'] = structure_df['Trans Info'].progress_apply(compute_word_graph)
    structure_df['Word Graph - WCC'] = structure_df['Word Graph'].progress_apply(compute_weakly_connected_components)
    structure_df['Word Graph - SCC'] = structure_df['Word Graph'].progress_apply(compute_strong_connected_components)
    # Features - Word Graph - Extract Features
    structure_df['Word Graph - #nodes'] = structure_df['Word Graph'].progress_apply(compute_number_of_nodes).astype(int)
    structure_df['Word Graph - #edges'] = structure_df['Word Graph'].progress_apply(compute_number_of_edges).astype(int)
    structure_df['Word Graph - WCC - min #nodes'] = structure_df['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_min).astype(int)
    structure_df['Word Graph - WCC - avg #nodes'] = structure_df['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_avg).astype(float)
    structure_df['Word Graph - WCC - max #nodes'] = structure_df['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_max).astype(int)
    structure_df['Word Graph - SCC - min #nodes'] = structure_df['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_min).astype(int)
    structure_df['Word Graph - SCC - avg #nodes'] = structure_df['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_avg).astype(float)
    structure_df['Word Graph - SCC - max #nodes'] = structure_df['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_max).astype(int)

    # ================================================================ EXPORT GRAPHS ================================================================
    # = module_exporter.change_current_directory(['tmp'])
    # = for subject, task, graph in tqdm(list(zip(structure_df['Subject'], structure_df['Task'], structure_df['Word Graph'])), desc="🎨 Exporting Graphs", leave=True):
    # =     code = subject[0]
    # =     module_exporter.change_current_directory(['tmp', task, code])
    # =     module_exporter.export_word_graph(f'{subject}-{task}', graph, figsize=(30, 12), with_labels=True)

    print("✅ Finished processing 'structure' analysis!")
    return structure_df