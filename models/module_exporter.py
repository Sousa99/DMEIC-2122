import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime
from typing import List, Optional, Tuple, TypedDict

EXPORT_DIRECTORY = '../results/'
EXECUTION_TIMESTAMP = datetime.now()
EXPORT_CSV_EXTENSION = '.csv'
EXPORT_IMAGE_EXTENSION = '.png'

MAIN_DIR = False
CURRENT_MODEL_DIRECTORY = 'TEMP MODEL'

# =================================== PRIVATE FUNCTIONS ===================================

def compute_path(filename: str, extension: str) -> str:

    timestampStr = EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S")
    if MAIN_DIR: directory_path = os.path.join(EXPORT_DIRECTORY, timestampStr)
    else: directory_path = os.path.join(EXPORT_DIRECTORY, timestampStr, CURRENT_MODEL_DIRECTORY)
    filename_full = filename + extension

    if not os.path.exists(directory_path): os.makedirs(directory_path)
    return os.path.join(directory_path, filename_full)

# =================================== PUBLIC FUNCTIONS - CHANGE GLOBAL PARAMETERS ===================================

def change_current_sub_directory(model_directory: str):
    global CURRENT_MODEL_DIRECTORY, MAIN_DIR
    CURRENT_MODEL_DIRECTORY = model_directory
    MAIN_DIR = False

def change_to_main_directory():
    global MAIN_DIR
    MAIN_DIR = True

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

    x_values = []
    y_values = []
    for stat in metrics:
        x_values.append(stat['name'])
        y_values.append(stat['score'])

    bar_chart(filename, x_values, y_values, x_label='Metrics', y_label='Score', y_lim=(0, 1))

# =================================== PUBLIC FUNCTIONS - GENERAL METHODS ===================================

def bar_chart(filename: str, x_values: List[str], y_values: List[int], figsize: Tuple[int] = (10, 4),
    label_bars: bool = True, x_label: Optional[str] = None, y_label: Optional[str] = None,
    x_lim: Optional[Tuple[float, float]] = None, y_lim: Optional[Tuple[float, float]] = None) -> None:

    complete_path = compute_path(filename, EXPORT_IMAGE_EXTENSION)

    plt.figure(figsize=figsize)
    bars = sns.barplot(x=x_values, y=y_values)
    
    if label_bars: bars.bar_label(bars.containers[0], fmt='%.2f')

    if x_label: plt.xlabel(x_label)
    if y_label: plt.ylabel(y_label)
    if x_lim: plt.xlim(x_lim[0], x_lim[1])
    if y_lim: plt.ylim(y_lim[0], y_lim[1])

    plt.savefig(complete_path)
    plt.close('all')