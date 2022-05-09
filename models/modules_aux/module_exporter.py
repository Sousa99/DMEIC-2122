import os
import sys
import math
import warnings
import matplotlib

import numpy                as np
import pandas               as pd
import seaborn              as sns
import networkx             as nx
import matplotlib.pyplot    as plt

from tqdm                   import tqdm
from datetime               import datetime
from typing                 import Any, Dict, List, Optional, Tuple

if sys.version_info[0] == 3 and sys.version_info[1] >= 8: from typing import TypedDict
else: from typing_extensions import TypedDict

EXPORT_DIRECTORY = '../results/'
EXECUTION_TIMESTAMP = datetime.now()
EXPORT_CSV_EXTENSION = '.csv'
EXPORT_IMAGE_EXTENSION = '.png'

CURRENT_DIRECTORIES = []

matplotlib.use('Agg')

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== PRIVATE FUNCTIONS ===================================

def compute_path(filename: str, extension: str) -> str:

    filename = filename.replace(' / ', ' ')
    filename = filename.replace('/', '_')

    timestampStr = EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S")
    directory_path = os.path.join(EXPORT_DIRECTORY, timestampStr, *CURRENT_DIRECTORIES)
    filename_full = filename + extension

    if not os.path.exists(directory_path): os.makedirs(directory_path)
    return os.path.join(directory_path, filename_full)

def optimal_grid(number: int) -> Tuple[int, int]:

    square_root = math.sqrt(number)
    square_root_floor = math.floor(square_root)

    rows = square_root_floor - 1
    if rows <= 0: rows = 1

    columns = math.ceil(number / rows)
    return (rows, columns)

# =================================== PUBLIC FUNCTIONS - CHANGE GLOBAL PARAMETERS ===================================

def change_execution_timestamp(timestamp: str):
    global EXECUTION_TIMESTAMP
    EXECUTION_TIMESTAMP = datetime.strptime(timestamp, "%Y.%m.%d %H.%M.%S")

def change_current_directory(current_directories: List[str] = []):
    global CURRENT_DIRECTORIES
    CURRENT_DIRECTORIES = current_directories

def push_current_directory(directory: str):
    global CURRENT_DIRECTORIES
    CURRENT_DIRECTORIES.append(directory)

def pop_current_directory():
    global CURRENT_DIRECTORIES
    CURRENT_DIRECTORIES.pop()

# =================================== PUBLIC FUNCTIONS - SPECIFIC PARAMETERS ===================================

def export_csv(dataframe: pd.DataFrame, filename: str = 'temp', index = True):

    complete_path = compute_path(filename, EXPORT_CSV_EXTENSION)
    dataframe.to_csv(complete_path, index=index)

def export_confusion_matrix(confusion_matrix: np.ndarray, categories: List[str], filename: str = 'temp'):

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)
    y_label = 'True Label'
    x_label = 'Predicted Label'

    plt.figure()
    sns.heatmap(confusion_matrix, annot=True, cmap='Blues', xticklabels=categories, yticklabels=categories)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(complete_path)
    plt.close('all')

ExportMetric = TypedDict("ExportMetric", { 'name': str, 'score': float } )
def export_metrics_bar_graph(metrics: List[ExportMetric], filename: str = 'temp') -> None:

    info = []
    for stat in metrics: info.append({'metric': stat['name'], 'score': stat['score'] })
    bar_chart(filename, pd.DataFrame(info), 'metric', 'score', x_label='Metrics', y_label='Score', y_lim=(0, 1))

# =================================== PUBLIC FUNCTIONS - GENERAL METHODS ===================================

def bar_chart(filename: str, dataframe: pd.DataFrame, x_key: str, y_key: str, figsize: Tuple[int] = (10, 4),
    hue_key: Optional[str] = None, label_bars: bool = True, x_label: Optional[str] = None, y_label: Optional[str] = None,
    x_rot: Optional[float] = None, y_rot: Optional[float] = None, margins: Optional[Dict[str, Optional[float]]] = None,
    x_lim: Optional[Tuple[float, float]] = None, y_lim: Optional[Tuple[float, float]] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=figsize)
    plot = sns.barplot(data=dataframe, x=x_key, y=y_key, hue=hue_key)
    rects = plot.patches
    
    if label_bars:
        for rect, label in zip(rects, dataframe[y_key].values):
            height = rect.get_height()
            label_formatted = "{:.2f}".format(label)
            plot.text(rect.get_x() + rect.get_width() / 2, height, label_formatted, ha="center", va="bottom")

    if x_label: plt.xlabel(x_label)
    if y_label: plt.ylabel(y_label)
    
    if x_lim: plt.xlim(x_lim[0], x_lim[1])
    if y_lim: plt.ylim(y_lim[0], y_lim[1])

    if x_rot: plt.xticks(rotation=x_rot)
    if y_rot: plt.yticks(rotation=y_rot)

    if margins: plt.subplots_adjust(bottom=margins['bottom'], left=margins['left'],
        top=margins['top'], right=margins['right'])

    plt.savefig(complete_path)
    plt.close('all')

def boxplot_for_each(filename: str, dataframe: pd.DataFrame, variables: List[str], hue: Optional[str] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    rows, cols = optimal_grid(len(variables))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5), squeeze=False)

    for variable_index, variable_key in enumerate(variables):

        col_index = variable_index % cols
        row_index = variable_index // cols

        sns.boxplot(data=dataframe, x=hue, y=variable_key, ax=axs[row_index, col_index])

    plt.savefig(complete_path)
    plt.close('all')

def histogram_for_each_numeric(filename: str, dataframe: pd.DataFrame, variables: List[str], hue: Optional[str] = None, kde: bool = True) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    rows, cols = optimal_grid(len(variables))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5), squeeze=False)

    for variable_index, variable_key in enumerate(variables):

        col_index = variable_index % cols
        row_index = variable_index // cols

        sns.histplot(data=dataframe, x=variable_key, hue=hue, kde=kde, ax=axs[row_index, col_index])

    plt.savefig(complete_path)
    plt.close('all')

def histogram_for_each_symbolic(filename: str, dataframe: pd.DataFrame, variables: List[str], hue: Optional[str] = None, kde: bool = True) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    rows, cols = optimal_grid(len(variables))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5), squeeze=False)

    for variable_index, variable_key in enumerate(variables):

        row_index = variable_index // cols
        col_index = variable_index % cols

        sns.countplot(data=dataframe, x=variable_key, hue=hue, ax=axs[row_index, col_index])
        axs[row_index, col_index].set_title("'{0}'".format(variable_key))

    plt.savefig(complete_path)
    plt.close('all')

def dataframe_all_variables_sparsity(filename: str, dataframe: pd.DataFrame, variables: List[str], hue: Optional[str] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)
    
    number_variables = len(variables)
    rows, cols = number_variables - 1, number_variables - 1
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 2.6, rows * 2.6))

    for var1_index in tqdm(range(number_variables), desc="⚙️  Processing Variables in first level", leave = False):
        var1 = variables[var1_index]

        for var2_index in tqdm(range(var1_index + 1, number_variables), desc="⚙️  Processing Variables in second level", leave = False):
            var2 = variables[var2_index]

            sns.scatterplot(data=dataframe, x=var1, y=var2, hue=hue, ax=axs[var1_index, var2_index])
            axs[var1_index, var2_index].set_title("%s x %s"%(var1, var2))
            axs[var1_index, var2_index].set_xlabel(var1)
            axs[var1_index, var2_index].set_ylabel(var2)

    plt.tight_layout()
    plt.savefig(complete_path)
    plt.close('all')

def dataframe_all_variables_sparsity_sep(filename: str, dataframe: pd.DataFrame, variables: List[str],
    hue: Optional[str] = None, figsize: Tuple[int] = (10, 4)) -> None:
    
    number_variables = len(variables)
    for var1_index in tqdm(range(number_variables), desc="⚙️  Processing Variables in first level", leave = False):
        var1 = variables[var1_index]

        for var2_index in tqdm(range(var1_index + 1, number_variables), desc="⚙️  Processing Variables in second level", leave = False):
            var2 = variables[var2_index]

            complete_path = compute_path(filename + ' - ' + f'{var1} x {var2}', EXPORT_IMAGE_EXTENSION)
            plt.figure(figsize=figsize)

            sns.scatterplot(data=dataframe, x=var1, y=var2, hue=hue)
            plt.title("%s x %s"%(var1, var2))
            plt.xlabel(var1)
            plt.ylabel(var2)

            plt.savefig(complete_path)
            plt.close('all')

def heatmap(filename: str, dataframe: pd.DataFrame, figsize: Tuple[int] = (6, 6),
    annot: bool = True, cmap: str = 'Blues', margins: Optional[Dict[str, Optional[float]]] = None,
    x_ticklabels: Optional[List[str]] = False, y_ticklabels: Optional[List[str]] = False) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=(figsize[0] + dataframe.shape[0] * 0.5, figsize[1] + dataframe.shape[1] * 0.5))
    sns.heatmap(abs(dataframe), xticklabels=x_ticklabels, yticklabels=y_ticklabels, annot=annot, cmap=cmap)

    if margins: plt.subplots_adjust(bottom=margins['bottom'], left=margins['left'],
        top=margins['top'], right=margins['right'])
    
    plt.savefig(complete_path)
    plt.close('all')

def multiple_lines_chart(filename: str, dataframe: pd.DataFrame, x_key: str, y_key: str,
    figsize: Tuple[int] = (10, 4), hue_key: Optional[str] = None, style_key: Optional[str] = None,
    x_rot: Optional[float] = None, y_rot: Optional[float] = None, margins: Optional[Dict[str, Optional[float]]] = None,
    x_lim: Optional[Tuple[float, float]] = None, y_lim: Optional[Tuple[float, float]] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=figsize)
    plot = sns.lineplot(data=dataframe, x=x_key, y=y_key, hue=hue_key, style=style_key)

    if x_lim: plt.xlim(x_lim[0], x_lim[1])
    if y_lim: plt.ylim(y_lim[0], y_lim[1])

    if x_rot: plt.xticks(rotation=x_rot)
    if y_rot: plt.yticks(rotation=y_rot)

    if margins: plt.subplots_adjust(bottom=margins['bottom'], left=margins['left'],
        top=margins['top'], right=margins['right'])

    plt.savefig(complete_path)
    plt.close('all')

def export_word_graph(filename: str, graph: nx.DiGraph, weight_edges: Optional[bool] = True,
    figsize: Tuple[int] = (10, 4), with_labels: Optional[bool] = None, node_color : Optional[str] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=figsize)

    pos = nx.spring_layout(graph)
    nx.draw_networkx(graph, pos, with_labels=with_labels, node_color=node_color)
    labels = nx.get_edge_attributes(graph, 'weight')
    if weight_edges: nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    plt.savefig(complete_path)
    plt.close('all')

def export_scatter_clusters(filename: str, dataframe: pd.DataFrame, x_key: str, y_key: str, figsize: Tuple[int] = (10, 4),
    hue_key: Optional[str] = None, style_key: Optional[str] = None, x_label: Optional[str] = None, y_label: Optional[str] = None,
    hide_labels: Optional[Tuple[str, Any]] = None, palette: str = "deep",
    legend_placement: Optional[str] = None, margins: Optional[Dict[str, Optional[float]]] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=figsize)
    plot = sns.scatterplot(data=dataframe, x=x_key, y=y_key, hue=hue_key, style=style_key, palette=palette)

    if x_label: plt.xlabel(x_label)
    if y_label: plt.ylabel(y_label)

    if margins: plt.subplots_adjust(bottom=margins['bottom'], left=margins['left'],
        top=margins['top'], right=margins['right'])

    def label_point(x: pd.Series, y: pd.Series, val: pd.Series, display: pd.Series, ax):
        a = pd.DataFrame.from_dict({'x': x, 'y': y, 'val': val, 'filter': display})
        for _, point in a.iterrows():
            if not point['filter']:
                ax.text(point['x']+ .15, point['y'] + 3.0, str(point['val']), fontsize='small')

    filter_labeling = pd.Series(False, index = dataframe.index)
    if hide_labels is not None: filter_labeling = dataframe[hide_labels[0]] == hide_labels[1]

    label_point(dataframe[x_key], dataframe[y_key], dataframe.index, filter_labeling, plt.gca())
    if legend_placement is not None:
        plt.legend(bbox_to_anchor=(1.02, 1), loc=legend_placement, borderaxespad=0)

    plt.savefig(complete_path)
    plt.close('all')