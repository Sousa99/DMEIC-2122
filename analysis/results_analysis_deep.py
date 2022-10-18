import os
import argparse
import warnings

import pandas               as pd
import seaborn              as sns
import matplotlib.pyplot    as plt

from typing             import List, Dict, Any
from datetime           import datetime
from matplotlib.colors  import LinearSegmentedColormap
from seaborn.algorithms import bootstrap

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

warnings.filterwarnings('ignore', category = DeprecationWarning)

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

# Input Constants
RESULTS_OVERVIEW                : str       = "results.csv"
# Output Constants
EXPORT_DIRECTORY                : str       = "records"
EXECUTION_TIMESTAMP             : datetime  = datetime.now()
EXPORT_PATH                     : str       = os.path.join(EXPORT_DIRECTORY, EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S"))

COLUMN_TASKS                    : str       = 'Tasks'
COLUMN_FEATURES                 : str       = 'Features'
COLUMN_REPETITION               : str       = 'Repetition'
COLUMN_FEATURE_IMPORTANCE       : str       = 'Feature Importance'

VALUE_FEATURE_IMPORTANCE_NONE   : str       = 'None'

CMAP_LIST : List[Any] = [(0.839, 0.266, 0.266, 1.0), (1.0, 1.0, 1.0, 1.0), (0.266, 0.839, 0.266, 1.0)]
CMAP : LinearSegmentedColormap = LinearSegmentedColormap.from_list('CustomMap', CMAP_LIST)

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-metrics", nargs='+', required=True, help="key for metrics for which to develop visualizations")
parser.add_argument("-results", required=True, help="paths to results folder to be used in analysis")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Dataframe
path_to_results_overview = os.path.join(arguments.results, RESULTS_OVERVIEW)
if not os.path.exists(path_to_results_overview) or not os.path.isfile(path_to_results_overview):
    exit(f"🚨 File '{path_to_results_overview}' does not exist, and should exist")

dataframe : pd.DataFrame = pd.read_csv(path_to_results_overview)
# Get sub dataframes
dataframe_for_confidence : pd.DataFrame = dataframe[dataframe[COLUMN_FEATURE_IMPORTANCE] == VALUE_FEATURE_IMPORTANCE_NONE]
dataframe_for_feature_study : pd.DataFrame = dataframe[dataframe[COLUMN_FEATURE_IMPORTANCE] != VALUE_FEATURE_IMPORTANCE_NONE]
dataframe_for_feature_study.set_index([COLUMN_TASKS, COLUMN_FEATURE_IMPORTANCE], inplace=True)

# Verify if all metric in dataframe
for metric in arguments.metrics:
    if metric not in dataframe.columns:
        exit(f"🚨 Metric '{metric}' does not exist in results overview")

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

tasks_ndarray = dataframe[COLUMN_TASKS].unique()
tasks_ndarray.sort()
tasks = tasks_ndarray.tolist()

features_studied_ndarray = dataframe[dataframe[COLUMN_FEATURE_IMPORTANCE] != VALUE_FEATURE_IMPORTANCE_NONE][COLUMN_FEATURE_IMPORTANCE].unique()
features_studied = list(filter(lambda feature: not "Max Cossine w/ Cluster" in feature or "Max Cossine w/ Cluster 0" in feature, features_studied_ndarray.tolist()))

sns.set_theme(palette="deep")
sns.set(font_scale = 1.25)

for metric in arguments.metrics:

    # =============================================================== Confidence Study ===============================================================

    plt.clf()
    plt.figure(figsize=(10, 5))
    g = sns.barplot(data=dataframe_for_confidence, x=COLUMN_TASKS, y=metric, order=list(tasks))
    for container in g.containers: g.bar_label(container, fmt='%0.2f', label_type='center')
    plt.tight_layout()
    plt.savefig(os.path.join(EXPORT_PATH, f'confidence study - {metric}.pdf'))

    confidence_overview = dataframe_for_confidence.groupby([COLUMN_TASKS])[metric].aggregate(['mean', 'std'])
    confidence_overview["Confidence Interval"] = dataframe_for_confidence.groupby([COLUMN_TASKS])[metric].aggregate(lambda scores: list(sns.utils.ci(bootstrap(scores.values))))
    confidence_overview["Confidence Interval - Lower"] = confidence_overview["Confidence Interval"].apply(lambda confidence: confidence[0])
    confidence_overview["Confidence Interval - Upper"] = confidence_overview["Confidence Interval"].apply(lambda confidence: confidence[1])
    confidence_overview["Confidence Interval - Average"] = (confidence_overview["Confidence Interval - Upper"] + confidence_overview["Confidence Interval - Lower"]) / 2

    confidence_overview.drop(["mean", "std", "Confidence Interval"], axis=1, inplace=True)
    confidence_overview.to_csv(os.path.join(EXPORT_PATH, f'confidence study - {metric}.csv'))

    confidence_overview_task_index = confidence_overview['Confidence Interval - Average']

    # =============================================================== Feature Importance Study ===============================================================

    final_feature_importance_dict = {}
    for task in tasks:

        final_feature_importance_dict[task] = {}
        for feature_importance in features_studied:

            feature_importance_standard = feature_importance.replace(" Feature Importance", "")

            baseline_value = confidence_overview_task_index[task]
            final_feature_importance_dict[task][feature_importance] = (baseline_value - dataframe_for_feature_study.loc[(task, feature_importance)][metric]) / baseline_value
    
    final_feature_importance_df = pd.DataFrame.from_dict(final_feature_importance_dict, orient='index')
    
    plt.clf()
    plt.figure(figsize=(23, 11))
    g = sns.heatmap(final_feature_importance_df, annot=True, fmt="0.2f", linewidths=1.0, square=True, cmap=CMAP, center=0.0, linecolor=(0.0, 0.0, 0.0), cbar_kws={"orientation": "horizontal", "location": "top", "shrink": 0.5})
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(EXPORT_PATH, f'feature importance study - {metric}.pdf'))