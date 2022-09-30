import os
import argparse
import warnings

import pandas           as pd

from typing             import List
from datetime           import datetime

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

warnings.filterwarnings('ignore', category = DeprecationWarning)

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

# Input Constants
RESULTS_OVERVIEW    : str       = "results.csv"
# Output Constants
EXPORT_DIRECTORY    : str       = "records"
EXECUTION_TIMESTAMP : datetime  = datetime.now()
EXPORT_PATH         : str       = os.path.join(EXPORT_DIRECTORY, EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S"))

GROUP_BY_COLLUMNS   : List[str] = [ 'Features', 'Tasks', 'Genders',	'Data' ]
COLUMN_FEATURES     : str       = 'Features'

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-metrics", nargs='+', required=True, help="key for metrics for which to develop visualizations")
parser.add_argument("-results", nargs='+', required=True, help="paths to results folder to be used in analysis")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Dataframes
dataframes : List[pd.DataFrame] = []
for path_to_results in arguments.results:
    path_to_results_overview = os.path.join(path_to_results, RESULTS_OVERVIEW)
    if not os.path.exists(path_to_results_overview) or not os.path.isfile(path_to_results_overview):
        exit(f"🚨 File '{path_to_results_overview}' does not exist, and should exist")

    dataframe : pd.DataFrame = pd.read_csv(path_to_results_overview)
    dataframes.append(dataframe)

# Union Dataframes
final_overview_dataframe : pd.DataFrame = pd.concat(dataframes)

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)
# Save final dataframe for analysis
final_overview_dataframe.to_csv(os.path.join(EXPORT_PATH, 'final results.csv'))

# Verify if all metric in dataframe
for metric in arguments.metrics:
    if metric not in final_overview_dataframe.columns:
        exit(f"🚨 Metric '{metric}' does not exist in results overview")

for feature_set in final_overview_dataframe[COLUMN_FEATURES].unique():

    feature_set_dataframe = final_overview_dataframe[final_overview_dataframe[COLUMN_FEATURES] == feature_set]
    for metric in arguments.metrics:
        # Compute best of models executed
        best_of_dataframe : pd.DataFrame = feature_set_dataframe.sort_values(metric, ascending=False).drop_duplicates(GROUP_BY_COLLUMNS)
        best_of_dataframe.to_csv(os.path.join(EXPORT_PATH, f'{metric} - {feature_set} - best of results.csv'), index=False)