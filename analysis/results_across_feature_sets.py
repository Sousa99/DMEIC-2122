import os
import argparse
import warnings

import numpy                as np
import pandas               as pd
import seaborn              as sns
import matplotlib.pyplot    as plt

from typing             import Dict, List
from datetime           import datetime

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

warnings.filterwarnings('ignore', category = DeprecationWarning)

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

# Output Constants
EXPORT_DIRECTORY    : str       = "records"
EXECUTION_TIMESTAMP : datetime  = datetime.now()
EXPORT_PATH         : str       = os.path.join(EXPORT_DIRECTORY, EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S"))

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-dataframe_best_of_baseline", required=True, help="path to the speech and sound dataframe")
parser.add_argument("-dataframe_best_of_focus", required=True, help="path to the structure/coherence and content dataframe")
parser.add_argument("-metric", required=True, help="metric to be selected for graphs")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Registry
dataframe_baseline  = pd.read_csv(arguments.dataframe_best_of_baseline)
dataframe_baseline  = dataframe_baseline.drop(dataframe_baseline.columns.difference(['Tasks','Data', arguments.metric]), axis=1)
dataframe_baseline  = dataframe_baseline[dataframe_baseline['Data'] == "V2 Complex"]
dataframe_baseline  = dataframe_baseline.drop(["Data"], axis=1)
dataframe_baseline["Study"] = "Speech and Sound"

dataframe_focus = pd.read_csv(arguments.dataframe_best_of_focus)
dataframe_focus = dataframe_focus.drop(dataframe_focus.columns.difference(['Tasks','Data', arguments.metric]), axis=1)
dataframe_focus = dataframe_focus[dataframe_focus['Data'] == "V2 Complex"]
dataframe_focus = dataframe_focus.drop(["Data"], axis=1)
dataframe_focus["Study"] = "Structure/Coherence and Content"

final_dataframe = pd.concat([dataframe_baseline, dataframe_focus], axis=0)

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

tasks_ndarray = final_dataframe["Tasks"].unique()
tasks_ndarray.sort()
tasks = tasks_ndarray.tolist()

sns.set_theme(palette="deep")

plt.clf()
sns.set(font_scale = 1.25)
plt.figure(figsize=(18, 7))
g = sns.barplot(data=final_dataframe, x="Tasks", y=arguments.metric, hue="Study", order=tasks)
for container in g.containers: g.bar_label(container, fmt='%0.2f', fontsize=19, fontweight="bold")
plt.legend(loc='lower center', fontsize=19)
plt.xticks(fontsize=18)
plt.xlabel("Tasks", fontsize=19)
plt.yticks(fontsize=18)
plt.ylabel(arguments.metric, fontsize=19)
plt.tight_layout()
plt.savefig(os.path.join(EXPORT_PATH, 'feature set study.pdf'))