import os
import argparse
import warnings

from tqdm import tqdm
from typing import Any, Dict, List, Tuple

import pandas as pd

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-files",   nargs="+",  help="path to folder with uncut audios")
args = parser.parse_args()

if ( not args.files ):
    print("🙏 Please provide 'files' of path to files to check")
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================


# =================================== MAIN EXECUTION ===================================

ids_used : Dict[str, Dict[str, int]] = {}
# Iteratively iterate each file
for file_path in tqdm(args.files, desc="🚀 Processing files", leave=False):

    # Get Filename
    base = os.path.basename(file_path)
    filename, _ = os.path.splitext(base)

    # Read Excel
    dataframe_read = pd.read_excel(file_path, sheet_name = filename, index_col = 0, engine = 'openpyxl')
    participants_ids : List[str] = list(dataframe_read.index)
    
    # Add Participants to info
    for participant_id in participants_ids:

        participant_id = participant_id.strip()
        # Properly setup dictionary
        if participant_id not in ids_used: ids_used[participant_id] = {}
        if filename not in ids_used[participant_id]: ids_used[participant_id][filename] = 0
        # Increment counter
        ids_used[participant_id][filename] = ids_used[participant_id][filename] + 1

conflicts_between : List[Tuple[str, Tuple[str]]] = []
conflicts_in : List[Tuple[str, str, int]] = []
# Find conflicts
for participant_id in ids_used:

    # Conflicts between various files
    if len(ids_used[participant_id]) > 1:
        conflict = (participant_id, tuple(ids_used[participant_id].keys()))
        conflicts_between.append(conflict)
    
    # Conflicts in a single file
    for file in ids_used[participant_id]:
        if ids_used[participant_id][file] > 1:
            conflict = (participant_id, file, ids_used[participant_id][file])
            conflicts_in.append(conflict)

# Display conflicts
if len(conflicts_between) == 0 and len(conflicts_in) == 0: print("✔️  No conflicts were detected for the given files")
else:
    
    for conflict in conflicts_in:
        participant_id, file, count = conflict
        print(f"❌  Participant '{participant_id}' mentioned '{count}' times in file '{file}'")
    for conflict in conflicts_between:
        participant_id, files = conflict
        print(f"❌  Conflict with participant '{participant_id}' mentioned in files '{files}'")