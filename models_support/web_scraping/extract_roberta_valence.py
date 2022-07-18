import os
import json
import argparse

import pandas   as pd

from tqdm       import tqdm
from typing     import List

# =============================??????????????????????????????????====== PACKAGES PARAMETERS ============??????????????????????????????????=======================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

COLUMN_METADATA         : str       = 'metadata'
COLUMN_TEXT             : str       = 'text'
COLUMN_VALENCE          : str       = 'valence'

LOAD_METADATA_EXTRACT   : List[str] = ['scraper']
LOAD_DROP_COLUMNS       : List[str] = ['metadata']

PREPROCESS_TEXT         : bool      = True

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-files", nargs='+', required=True, help="paths to extracted valence sets")
# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

def preprocess_datafram(dataframe: pd.DataFrame) -> pd.DataFrame:
    for metadata_key in LOAD_METADATA_EXTRACT:
        dataframe[metadata_key] = dataframe[COLUMN_METADATA].progress_apply(lambda metadata: metadata[metadata_key])
    dataframe.drop(LOAD_DROP_COLUMNS, axis=1, errors='ignore', inplace=True)
    return dataframe

def preprocess_text(text: str) -> str:
    if PREPROCESS_TEXT: text = text.lower()
    return text

# ======================================================================== MAIN EXECUTION ========================================================================

# Load various extracted information into dataframes
dataframes : List[pd.DataFrame] = []
for path_to_extracted in arguments.files:
    if not os.path.exists(path_to_extracted) or not os.path.isfile(path_to_extracted):
        exit(f"🚨 File '{path_to_extracted}' does not exist, and should exist")

    file = open(path_to_extracted, 'r')
    information_extracted = json.load(file)
    file.close()

    # Deal with dataframe and quick preprocessing
    dataframe : pd.DataFrame = pd.DataFrame(information_extracted)
    dataframe = preprocess_datafram(dataframe)
    dataframes.append(dataframe)

# Get final dataframe with all the information concatenated
final_dataframe : pd.DataFrame = pd.concat(dataframes)
# Preprocess text
final_dataframe[COLUMN_TEXT] = final_dataframe[COLUMN_TEXT].progress_apply(lambda text: preprocess_text(text))