import os
from typing import List
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime

# Local Modules
from module_scorer import ExportMetric

EXPORT_DIRECTORY = '../results/'
EXECUTION_TIMESTAMP = datetime.now()
EXPORT_CSV_EXTENSION = '.csv'
EXPORT_IMAGE_EXTENSION = '.png'

# =================================== PRIVATE FUNCTIONS ===================================

def calculate_file_prefix() -> str:

    timestampStr = EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S")
    return timestampStr + ' - '

# =================================== PUBLIC FUNCTIONS ===================================

def export_csv(dataframe: pd.Dataframe, filename: str = 'temp'):

    complete_path = os.path.join(EXPORT_DIRECTORY, calculate_file_prefix() + filename + EXPORT_CSV_EXTENSION)
    dataframe.to_csv(complete_path)

def export_confusion_matrix(confusion_matrix: np.ndarray, categories: List[str], filename: str = 'temp'):

    complete_path = os.path.join(EXPORT_DIRECTORY, calculate_file_prefix() + filename + EXPORT_IMAGE_EXTENSION)
    y_label = 'True Label'
    x_label = 'Predicted Label'

    plt.figure()
    sns.heatmap(confusion_matrix, annot=True, cmap='Blues', xticklabels=categories, yticklabels=categories)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(complete_path)

def export_metrics_bar_graph(metrics: List[ExportMetric], filename: str = 'temp'):

    complete_path = os.path.join(EXPORT_DIRECTORY, calculate_file_prefix() + filename + EXPORT_IMAGE_EXTENSION)
    y_label = 'Score'
    x_label = 'Metrics'

    x_values = []
    y_values = []
    for stat in metrics:
        x_values.append(stat['name'])
        y_values.append(stat['score'])

    plt.figure(figsize=(10, 4))
    bars = sns.barplot(x=x_values, y=y_values)
    bars.bar_label(bars.containers[0], fmt='%.2f')
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.ylim(0, 1)
    plt.savefig(complete_path)