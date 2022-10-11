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
parser.add_argument("-dataframe_best_of", required=True, help="path to the best of dataframe")
parser.add_argument("-metric", required=True, help="metric to be selected for graphs")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Registry
dataframe = pd.read_csv(arguments.dataframe_best_of)
dataframe = dataframe.drop(dataframe.columns.difference(['Tasks','Data', arguments.metric]), axis=1)

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

tasks_ndarray = dataframe["Tasks"].unique()
tasks_ndarray.sort()
tasks = tasks_ndarray.tolist()

sns.set_theme(palette="deep")

plt.clf()
sns.set(font_scale = 1.15)
plt.figure(figsize=(18, 7))
g = sns.barplot(data=dataframe, x="Tasks", y=arguments.metric, hue="Data", order=tasks)
for container in g.containers: g.bar_label(container, fmt='%0.2f')
plt.tight_layout()
plt.savefig(os.path.join(EXPORT_PATH, 'data study.pdf'))