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
parser.add_argument("-dataframe_best_of_automatic", required=True, help="path to the best of dataframe with automatic transcriptions")
parser.add_argument("-dataframe_best_of_manual", required=True, help="path to the best of dataframe with manual transcriptions")
parser.add_argument("-metric", required=True, help="metric to be selected for graphs")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Registry
dataframe_automatic = pd.read_csv(arguments.dataframe_best_of_automatic)
dataframe_automatic = dataframe_automatic.drop(dataframe_automatic.columns.difference(['Tasks','Data', arguments.metric]), axis=1)
dataframe_automatic = dataframe_automatic[dataframe_automatic['Data'] == "V2 Complex"]
dataframe_automatic = dataframe_automatic.drop(["Data"], axis=1)
dataframe_automatic["Transcriptions"] = "Automatic Transcriptions"

dataframe_manual = pd.read_csv(arguments.dataframe_best_of_manual)
dataframe_manual = dataframe_manual.drop(dataframe_manual.columns.difference(['Tasks','Data', arguments.metric]), axis=1)
dataframe_manual = dataframe_manual[dataframe_manual['Data'] == "V2 Complex"]
dataframe_manual = dataframe_manual.drop(["Data"], axis=1)
dataframe_manual["Transcriptions"] = "Manual Transcriptions"

final_dataframe = pd.concat([dataframe_automatic, dataframe_manual], axis=0)

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
g = sns.barplot(data=final_dataframe, x="Tasks", y=arguments.metric, hue="Transcriptions", order=tasks)
for container in g.containers: g.bar_label(container, fmt='%0.2f', fontsize=19, fontweight="bold")
plt.legend(loc='lower center', fontsize=19)
plt.xticks(fontsize=18)
plt.xlabel("Tasks", fontsize=19)
plt.yticks(fontsize=18)
plt.ylabel(arguments.metric, fontsize=19)
plt.tight_layout()
plt.savefig(os.path.join(EXPORT_PATH, 'transcription study.pdf'))