import os

import pandas as pd

from typing import List

# Local Modules
import module_gemaps

# =================================== PRIVATE METHODS ===================================

def compute_file_paths(audio_path: str, extension_preference_order: List[str]):

    _, _, files_full = list(os.walk(audio_path))[0]
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    return files[0][0]

# =================================== PUBLIC METHODS ===================================

def sound_analysis(paths_df: pd.DataFrame, preference_audio_tracks: List[str]):

    # Dataframe to study sound features
    sound_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Audio Path']]
    # Choose audio files from dictionary
    sound_df['Audio File'] = sound_df['Audio Path'].apply(compute_file_paths, args=(preference_audio_tracks,))
    sound_df['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(sound_df['Audio Path'], sound_df['Audio File']))))
    
    # GeMAPS features
    gemaps_extractor = module_gemaps.GeMAPSAnalyzer(module_gemaps.FeatureSet.eGeMAPSv02)
    sound_df = sound_df.merge(sound_df['Audio File Path'].apply(lambda file: gemaps_extractor.process_file(file)), left_index=True, right_index=True)
    
    return sound_df