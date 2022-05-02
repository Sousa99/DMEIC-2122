import random
import itertools

import pandas as pd
import networkx as nx

from tqdm import tqdm
from typing import Dict, List, Optional, Set, Tuple

# Local Modules - Auxiliary
import modules_aux.module_load as module_load
import modules_aux.module_exporter as module_exporter

# =================================== DEFINITION OF CONSTS ===================================

PRESET_INVALID_VALUE = -1
NUMBER_OF_SHUFFLES_WORD_GRAPH = 10000

# =================================== PRIVATE METHODS ===================================

def create_word_graph(trans_info_items: List[module_load.TranscriptionInfoItem]) -> nx.MultiDiGraph:
    
    word_graph = nx.MultiDiGraph()
    last_word : Optional[str] = None
    for transcription_line in trans_info_items:
        words : List[str] = transcription_line.get_words().split()
        for next_word in words:
            if last_word is not None:
                word_graph.add_edge(last_word, next_word)
            last_word = next_word
    return word_graph

def compute_word_graph(trans_info: module_load.TranscriptionInfo) -> nx.MultiDiGraph:
    return create_word_graph(trans_info.get_info_items())

def convert_multi_graph_to_weighted(multi_graph: nx.MultiDiGraph) -> nx.DiGraph:

    new_graph = nx.DiGraph()
    for from_node, to_node, edge_data in multi_graph.edges(data=True):
        weight = edge_data['weight'] if 'weight' in edge_data else 1.0
        if new_graph.has_edge(from_node, to_node): new_graph[from_node][to_node]['weight'] += weight
        else: new_graph.add_edge(from_node, to_node, weight = weight)

    return new_graph

def compute_weakly_connected_components(graph: nx.MultiDiGraph) -> List[nx.MultiDiGraph]:
    generator = nx.weakly_connected_components(graph)
    weakly_connected_components_list = sorted(generator, key=len, reverse=True)
    weakly_connected_components : List[nx.MultiDiGraph] = list(map(lambda wcc_list: nx.MultiDiGraph(graph.subgraph(wcc_list)), weakly_connected_components_list))
    return weakly_connected_components
def compute_strong_connected_components(graph: nx.MultiDiGraph) -> List[nx.MultiDiGraph]:
    generator = nx.strongly_connected_components(graph)
    strong_connected_components_list = sorted(generator, key=len, reverse=True)
    strong_connected_components : List[nx.MultiDiGraph] = list(map(lambda wcc_list: nx.MultiDiGraph(graph.subgraph(wcc_list)), strong_connected_components_list))
    return strong_connected_components

def get_largest_connected_component(graphs: List[nx.MultiDiGraph]) -> Optional[nx.MultiDiGraph]:
    if len(graphs) == 0: return None
    return sorted(graphs, key=len, reverse=True)[0]

def compute_number_of_nodes(graph: Optional[nx.MultiDiGraph]) -> int:
    if graph is None: return PRESET_INVALID_VALUE
    return graph.number_of_nodes()
def compute_number_of_edges(graph: Optional[nx.MultiDiGraph]) -> int:
    if graph is None: return PRESET_INVALID_VALUE
    return graph.number_of_edges()

def compute_connected_components_nodes_min(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return min(map(lambda cc: compute_number_of_nodes(cc) , connected_components))
def compute_connected_components_nodes_avg(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return sum(compute_number_of_nodes(cc) for cc in connected_components) / len(connected_components)
def compute_connected_components_nodes_max(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return max(map(lambda cc: compute_number_of_nodes(cc) , connected_components))
def compute_connected_components_edges_min(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return min(map(lambda cc: compute_number_of_edges(cc) , connected_components))
def compute_connected_components_edges_avg(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return sum(compute_number_of_edges(cc) for cc in connected_components) / len(connected_components)
def compute_connected_components_edges_max(connected_components: List[nx.MultiDiGraph]):
    if len(connected_components) == 0: return PRESET_INVALID_VALUE
    return max(map(lambda cc: compute_number_of_edges(cc) , connected_components))

def compute_average_total_degree(graph: nx.MultiDiGraph) -> int:
    degrees_by_nodes = graph.degree()
    if len(degrees_by_nodes) == 0: return PRESET_INVALID_VALUE
    return sum(degree for _, degree in degrees_by_nodes) / len(degrees_by_nodes)

def compute_parallel_edges(graph: nx.MultiDiGraph) -> int:

    edges_info : Dict[Tuple[str, str], int] = {}
    for from_node, to_node in graph.edges():
        sorted_nodes = sorted([from_node, to_node])
        info_key = (sorted_nodes[0], sorted_nodes[1])
        if info_key not in edges_info: edges_info[info_key] = 1
        else: edges_info[info_key] = edges_info[info_key] + 1

    return sum(edges_info[key] - 1 for key in edges_info)

def compute_repeated_edges(graph: nx.MultiDiGraph) -> int:

    edges_info : Dict[Tuple[str, str], int] = {}
    for from_node, to_node in graph.edges():
        info_key = (from_node, to_node)
        if info_key not in edges_info: edges_info[info_key] = 1
        else: edges_info[info_key] = edges_info[info_key] + 1

    return sum(edges_info[key] - 1 for key in edges_info)

def compute_diameter(graph: nx.MultiDiGraph) -> int:
    if compute_number_of_nodes(graph) == 0: return PRESET_INVALID_VALUE
    return nx.diameter(graph.to_undirected())

def compute_average_shorthest_path(graph: nx.MultiDiGraph) -> int:
    if compute_number_of_nodes(graph) == 0: return PRESET_INVALID_VALUE
    return nx.average_shortest_path_length(graph)

def compute_average_cluster_coefficient(graph: nx.MultiDiGraph) -> int:
    if compute_number_of_nodes(graph) == 0: return PRESET_INVALID_VALUE
    di_graph = convert_multi_graph_to_weighted(graph)
    return nx.average_clustering(di_graph)

def compute_probability_component(trans_info: module_load.TranscriptionInfo, connected_component: Optional[nx.MultiDiGraph], strongly: bool) -> float:
    if connected_component is None: return PRESET_INVALID_VALUE
    
    count_total : int = 0
    count_specific : int = 0
    connected_components_nodes : Set(str) = set(connected_component.nodes)

    trans_info_items = trans_info.get_info_items()

    # Get Random Permutations
    trans_info_perms = itertools.permutations(trans_info_items)
    trans_info_perms = [ random.sample(trans_info_items, len(trans_info_items))  for _ in range(NUMBER_OF_SHUFFLES_WORD_GRAPH) ]

    for trans_info_perm in trans_info_perms:
        word_graph_perm = create_word_graph(trans_info_perm)
        if strongly: connected_components_perm = compute_strong_connected_components(word_graph_perm)
        else: connected_components_perm = compute_weakly_connected_components(word_graph_perm)

        count_total = count_total + 1
        for connected_component_perm in connected_components_perm:
            connected_components_nodes_perm = set(connected_component_perm.nodes)
            if connected_components_nodes == connected_components_nodes_perm:
                count_specific = count_specific + 1
                break

    return count_specific / count_total


# =================================== PUBLIC METHODS ===================================

def word_graph_analysis(basis_dataframe: pd.DataFrame) -> pd.DataFrame:
    print("🚀 Processing 'word graph' analysis ...")

    # ===================================================== FEATURES - WORD GRAPH - ACQUIRE STRUCTURES =====================================================
    basis_dataframe['Word Graph'] = basis_dataframe['Trans Info'].progress_apply(compute_word_graph)
    basis_dataframe['Word Graph - WCC'] = basis_dataframe['Word Graph'].progress_apply(compute_weakly_connected_components)
    basis_dataframe['Word Graph - SCC'] = basis_dataframe['Word Graph'].progress_apply(compute_strong_connected_components)
    basis_dataframe['Word Graph - LWCC'] = basis_dataframe['Word Graph - WCC'].progress_apply(get_largest_connected_component)
    basis_dataframe['Word Graph - LSCC'] = basis_dataframe['Word Graph - SCC'].progress_apply(get_largest_connected_component)

    # ============================================== FEATURES - WORD GRAPH - EXTRACT FEATURES - MOST IMPORTANT ==============================================
    basis_dataframe['Word Graph - #nodes'] = basis_dataframe['Word Graph'].progress_apply(compute_number_of_nodes).astype(int)
    basis_dataframe['Word Graph - #edges'] = basis_dataframe['Word Graph'].progress_apply(compute_number_of_edges).astype(int)
    basis_dataframe['Word Graph - diameter'] = basis_dataframe['Word Graph'].progress_apply(compute_diameter).astype(int)
    basis_dataframe['Word Graph - #repeated_edges'] = basis_dataframe['Word Graph'].progress_apply(compute_repeated_edges).astype(int)
    basis_dataframe['Word Graph - #parallel_edges'] = basis_dataframe['Word Graph'].progress_apply(compute_parallel_edges).astype(int)
    basis_dataframe['Word Graph - #average_total_degree'] = basis_dataframe['Word Graph'].progress_apply(compute_average_total_degree).astype(int)
    basis_dataframe['Word Graph - #average_shortest_path'] = basis_dataframe['Word Graph'].progress_apply(compute_average_shorthest_path).astype(int)
    basis_dataframe['Word Graph - #average_clustering_coefficient'] = basis_dataframe['Word Graph'].progress_apply(compute_average_cluster_coefficient).astype(float)
    # = basis_dataframe['Word Graph - LWCC - #nodes'] = basis_dataframe['Word Graph - LWCC'].progress_apply(compute_number_of_nodes).astype(int)
    # = basis_dataframe['Word Graph - LWCC - #edges'] = basis_dataframe['Word Graph - LWCC'].progress_apply(compute_number_of_edges).astype(int)
    # = basis_dataframe['Word Graph - LWCC - probability'] = basis_dataframe.progress_apply(lambda row: compute_probability_component(row['Trans Info'], row['Word Graph - LWCC'], False), axis=1)
    basis_dataframe['Word Graph - LSCC - #nodes'] = basis_dataframe['Word Graph - LSCC'].progress_apply(compute_number_of_nodes).astype(int)
    basis_dataframe['Word Graph - LSCC - #edges'] = basis_dataframe['Word Graph - LSCC'].progress_apply(compute_number_of_edges).astype(int)
    basis_dataframe['Word Graph - LSCC - probability'] = basis_dataframe.progress_apply(lambda row: compute_probability_component(row['Trans Info'], row['Word Graph - LSCC'], True), axis=1)
    
    # ============================================== FEATURES - WORD GRAPH - EXTRACT FEATURES - LEAST IMPORTANT ==============================================
    # = basis_dataframe['Word Graph - WCC - min #nodes'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_min).astype(int)
    # = basis_dataframe['Word Graph - WCC - avg #nodes'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_avg).astype(float)
    # = basis_dataframe['Word Graph - WCC - max #nodes'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_nodes_max).astype(int)
    basis_dataframe['Word Graph - SCC - min #nodes'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_min).astype(int)
    basis_dataframe['Word Graph - SCC - avg #nodes'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_avg).astype(float)
    basis_dataframe['Word Graph - SCC - max #nodes'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_nodes_max).astype(int)
    # = basis_dataframe['Word Graph - WCC - min #edges'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_edges_min).astype(int)
    # = basis_dataframe['Word Graph - WCC - avg #edges'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_edges_avg).astype(float)
    # = basis_dataframe['Word Graph - WCC - max #edges'] = basis_dataframe['Word Graph - WCC'].progress_apply(compute_connected_components_edges_max).astype(int)
    basis_dataframe['Word Graph - SCC - min #edges'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_edges_min).astype(int)
    basis_dataframe['Word Graph - SCC - avg #edges'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_edges_avg).astype(float)
    basis_dataframe['Word Graph - SCC - max #edges'] = basis_dataframe['Word Graph - SCC'].progress_apply(compute_connected_components_edges_max).astype(int)

    # ================================================================ EXPORT GRAPHS ================================================================
    # = module_exporter.change_current_directory(['tmp'])
    # = for subject, task, graph in tqdm(list(zip(basis_dataframe['Subject'], basis_dataframe['Task'], basis_dataframe['Word Graph'])), desc="🎨 Exporting Graphs", leave=True):
    # =     code = subject[0]
    # =     module_exporter.change_current_directory(['tmp', task, code])
    # =     module_exporter.export_word_graph(f'{subject}-{task}', convert_multi_graph_to_weighted(graph), figsize=(30, 12), with_labels=True)

    return basis_dataframe
