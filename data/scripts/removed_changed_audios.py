import os
import shutil
import argparse

import pandas   as pd

from typing     import Dict, List, Tuple

# =================================== IGNORE CERTAIN ERRORS ===================================

# =================================== CONSTANTS DEFINITIONS ===================================

HIERARCHY_FULL              : str = 'full'
HIERARCHY_TRANSCRIPTIONS    : str = 'transcriptions'

# ======================================= FLAGS PARSING =======================================

parser = argparse.ArgumentParser()
parser.add_argument("-alteration_path", required=True, help="path to file where processed tracks are stored")
parser.add_argument("-target_folder", required=True, help="path to folder which has folders/files to be removed")
parser.add_argument("-hierarchy", required=True, choices=[HIERARCHY_FULL, HIERARCHY_TRANSCRIPTIONS], help='type of hierarchy folder where processed tracks are stored')
parser.add_argument("-non_commit", required=False, action='store_true', default=False, help="flag set as true when no changes are to be carried out")
args = parser.parse_args()

# =================================== CONSTANTS DEFINITIONS ===================================

GROUPS_CONVERSION   : Dict[str, str]    = { 'c': 'controls', 'p': 'psychosis', 'b': 'bipolars' }
JOIN_SYMBOL         : str               = '_'

# ===================================== CLASS DEFINITIONS =====================================

# ==================================== AUXILIARY FUNCTIONS ====================================

# ===================================== MAIN FUNCTIONALITY =====================================

if not os.path.exists(args.alteration_path) or not os.path.isfile(args.alteration_path):
    print(f"🚨 File \'{args.alteration_path}\' given as 'alteration_path' does not exist")

alterations_df = pd.read_csv(args.alteration_path, sep='\t', index_col=[0, 1, 2])
alterations_index : List[Tuple[str, str, int]] = alterations_df.index.to_list()
to_remove_paths : List[str] = []

# Full Hierarchy
if args.hierarchy == HIERARCHY_FULL:
    for group_id, subject_id, task_number in alterations_index:
        group_entire : str = GROUPS_CONVERSION[group_id]
        subject_folder : str = JOIN_SYMBOL.join([group_id, subject_id])
        task_folder : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_number)])

        target_path : str = os.path.join(args.target_folder, group_entire, subject_folder, task_folder)
        to_remove_paths.append(target_path)

# Transcriptions Hierarchy
elif args.hierarchy == HIERARCHY_TRANSCRIPTIONS:

    all_existent_folders : List[str] = []
    for group_entire in GROUPS_CONVERSION.values():
        target_path : str = os.path.join(args.target_folder, group_entire, 'exp_tribus')
        subfolders_existent = os.listdir(target_path)

        all_existent_folders.extend(subfolders_existent)

    for group_id, subject_id, task_number in alterations_index:
        group_entire : str = GROUPS_CONVERSION[group_id]
        task_folder : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_number)])

        valids_existent : List[str] = list(filter(lambda existent: existent.startswith(task_folder), all_existent_folders))
        for valid_existent in valids_existent:
            target_path : str = os.path.join(args.target_folder, group_entire, 'exp_tribus', valids_existent)
            to_remove_paths.append(target_path)

# Execute removal or log
for to_remove_path in to_remove_paths:

    if args.non_commit: print(f"🔵 If committed the folder \'{to_remove_path}\' and its' contents would be removed")
    else:
        shutil.rmtree(to_remove_path)
        print(f"🟢 Folder \'{to_remove_path}\' and its' contents were removed")