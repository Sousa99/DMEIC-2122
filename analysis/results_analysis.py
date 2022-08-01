import os
import argparse
import warnings

import numpy                as np
import pandas               as pd
import seaborn              as sns
import matplotlib.pyplot    as plt

from typing             import List
from datetime           import datetime
from matplotlib.patches import PathPatch

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

warnings.filterwarnings('ignore', category = DeprecationWarning)

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

# Input Constants
RESULTS_OVERVIEW    : str       = "results.csv"
# Output Constants
EXPORT_DIRECTORY    : str       = "records"
EXECUTION_TIMESTAMP : datetime  = datetime.now()
EXPORT_PATH         : str       = os.path.join(EXPORT_DIRECTORY, EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S"))

# Execution Constants
EXECUTION_PLANS = [ { 'id': 'Feature Study - V1 Simple', 'key_to_study': 'Features', 'filter': [ { 'key': 'Data', 'values': ['V1 Simple'] } ] },
    { 'id': 'Feature Study - V2 Simple', 'key_to_study': 'Features', 'filter': [ { 'key': 'Data', 'values': ['V1 Simple', 'V2 Simple'] } ] },
    { 'id': 'Feature Study', 'key_to_study': 'Features', 'filter': [] },
    { 'id': 'Data Expansion Study', 'key_to_study': 'Data', 'filter': [] } ]

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-metrics", nargs='+', required=True, help="key for metrics for which to develop visualizations")
parser.add_argument("-results", nargs='+', required=True, help="paths to results folder to be used in analysis")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

# Code from: https://stackoverflow.com/questions/31498850/set-space-between-boxplots-in-python-graphs-generated-nested-box-plots-with-seab
def adjust_box_widths(g, fac):
    for c in g.axes.get_children():

        if isinstance(c, PathPatch):
            # getting current width of box:
            p = c.get_path()
            verts = p.vertices
            verts_sub = verts[:-1]
            xmin = np.min(verts_sub[:,0])
            xmax = np.max(verts_sub[:,0])
            xmid = 0.5*(xmin+xmax)
            xhalf = 0.5*(xmax - xmin)

            # setting new width of box
            xmin_new = xmid-fac*xhalf
            xmax_new = xmid+fac*xhalf
            verts_sub[verts_sub[:,0] == xmin,0] = xmin_new
            verts_sub[verts_sub[:,0] == xmax,0] = xmax_new

            # setting new width of median line
            for l in g.axes.lines:
                if np.all(l.get_xdata() == [xmin,xmax]):
                    l.set_xdata([xmin_new,xmax_new])

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

# Verify if all metric in dataframe
for metric in arguments.metrics:
    if metric not in final_overview_dataframe.columns:
        exit(f"🚨 Metric '{metric}' does not exist in results overview")

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)
# Save final dataframe for analysis
final_overview_dataframe.to_csv(os.path.join(EXPORT_PATH, 'final_results.csv'))

# Iterate Metric for which to export graphs
for plan in EXECUTION_PLANS:

    filtered_dataframe = final_overview_dataframe.copy(deep=True)
    for filter_value in plan['filter']:
        filtered_dataframe = filtered_dataframe[filtered_dataframe[filter_value['key']].isin(filter_value['values'])]

    for metric in arguments.metrics:

        plt.clf()
        sns.set(font_scale = 1)
        plt.figure(figsize=(10, 4))
        g = sns.boxplot(y=metric, x=plan['key_to_study'], data=filtered_dataframe, saturation=0.65)
        adjust_box_widths(g, 0.9)
        plt.savefig(os.path.join(EXPORT_PATH, f"{plan['id']} - {metric} - results.png"))

        plt.clf()
        sns.set(font_scale = 1)
        plt.figure(figsize=(15, 4))
        g = sns.boxplot(x='Tasks', y=metric, hue=plan['key_to_study'], data=filtered_dataframe, saturation=0.65)
        adjust_box_widths(g, 0.9)
        plt.savefig(os.path.join(EXPORT_PATH, f"{plan['id']} - {metric} - results by task.png"))

        plt.clf()
        sns.set(font_scale = 1)
        plt.figure(figsize=(15, 4))
        g = sns.boxplot(x='Classifier', y=metric, hue=plan['key_to_study'], data=filtered_dataframe, saturation=0.55)
        adjust_box_widths(g, 0.9)
        plt.savefig(os.path.join(EXPORT_PATH, f"{plan['id']} - {metric} - results by classifier.png"))

        #plt.clf()
        #sns.set(font_scale = 1)
        #g = sns.catplot(x='Tasks', y=metric, hue=plan['key_to_study'], row='Classifier', kind="box", data=filtered_dataframe, saturation=0.65)
        #plt.savefig(os.path.join(EXPORT_PATH, f"{plan['id']} - {metric} - results by classifier and task.png"))