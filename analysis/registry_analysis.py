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
parser.add_argument("-registry", required=True, help="path to the registry file")

# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ======================================================================== AUX FUNCTIONS ========================================================================

def transform_registry(dataframe: pd.DataFrame, target_key: str, check_exists: bool = True, check_clinic_day: bool = False) -> pd.DataFrame:

    # Definition for plotting
    months  : List[str] = dataframe["Month"].unique()
    days    : List[int] = [ x for x in range(1, 32) ]

    dataframe_reindexed = dataframe.set_index(["Month", "Day"], inplace=False)

    dataframe_dict : Dict[str, Dict[str]] = {}
    for month in months:
        if month not in dataframe_dict:
            dataframe_dict[month] = {}
        for day in days:
            in_dataframe : bool = dataframe_reindexed.index.isin([(month, day)]).any()
            if in_dataframe:
                clinic_day : bool = dataframe_reindexed.loc[(month, day)]["Clinic Day"]
                if not check_clinic_day or clinic_day: dataframe_dict[month][day] = dataframe_reindexed.loc[(month, day)][target_key]
                else: dataframe_dict[month][day] = np.NAN
            elif check_exists: dataframe_dict[month][day] = np.NAN
            else: dataframe_dict[month][day] = 0

    final_dataframe = pd.DataFrame.from_dict(dataframe_dict, orient="index")
    return final_dataframe

# ======================================================================== MAIN EXECUTION ========================================================================

# Get Registry
registry = pd.read_csv(arguments.registry, index_col=0)
registry.index                  = pd.to_datetime(registry.index)
registry["Month"]               = registry.index.month_name()
registry["Week Day"]            = registry.index.day_name()
registry["Day"]                 = registry.index.day
registry["Clinic Day"]          = registry["Clinic Day"] == "x"
registry["Controls"]            = registry["Controls"].replace("-", 0).apply(pd.to_numeric)
registry["Patients"]            = registry["Patients"].replace("-", 0).apply(pd.to_numeric)
registry["Total Recordings"]    = registry["Controls"] + registry["Patients"]

registry_target_patients = transform_registry(registry, "Patients", True, True)

# Create Path for Exports
if not os.path.exists(EXPORT_PATH) or not os.path.isdir(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

sns.set_theme(palette="deep")

plt.clf()
sns.set(font_scale = 1.25)
plt.figure(figsize=(20, 3))
heatmap = sns.heatmap(data=registry_target_patients, cmap="YlGnBu", square=True, annot=True)
plt.tight_layout()
plt.savefig(os.path.join(EXPORT_PATH, 'registry.pdf'))