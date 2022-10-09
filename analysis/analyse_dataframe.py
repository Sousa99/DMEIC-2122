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
parser.add_argument("-datasets", nargs='+', required=True, help="path to the dataframes in csv format")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ======================================================================== MAIN EXECUTION ========================================================================

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

for dataset_path in arguments.datasets:

    path_folders : str = os.path.dirname(dataset_path)
    path_folder : str = os.path.basename(path_folders)

    if not os.path.exists(dataset_path) or not os.path.isfile(dataset_path):
        print(f"❌ Dataset for path '{dataset_path}' not found")
        continue

    dataset : pd.DataFrame = pd.read_csv(dataset_path, index_col=0)
    dataset_description : pd.DataFrame = dataset.describe().transpose()

    save_path : str = os.path.join(EXPORT_PATH, f"describe {path_folder}.csv")
    dataset_description.to_csv(save_path)