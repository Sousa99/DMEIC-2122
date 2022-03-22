import os

import pandas as pd

from typing import List

# =================================== PRIVATE METHODS ===================================

def compute_file_paths(audio_path: str, extension_preference_order: List[str]):

    _, _, files_full = list(os.walk(audio_path))[0]
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    return files[0][0]

# =================================== PUBLIC METHODS ===================================

def structure_analysis(paths_df: pd.DataFrame, preference_trans: List[str], trans_extension: str) -> pd.DataFrame:
    print("🚀 Processing 'structure' analysis ...")

    return pd.DataFrame()