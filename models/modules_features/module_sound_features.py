import os

import pandas as pd

from typing import List

# Local Modules - Features
import modules_features.module_gemaps   as module_gemaps
# Local Modules - Auxiliary
import modules_aux.module_aux           as module_aux

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def sound_analysis(paths_df: pd.DataFrame, preference_audio_tracks: List[str]):
    print("🚀 Processing 'sound' analysis ...")

    # Dataframe to study sound features
    sound_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Audio Path']]
    # Choose audio files from dictionary
    sound_df['Audio File'] = sound_df['Audio Path'].apply(module_aux.compute_file_paths, args=(preference_audio_tracks,))
    sound_df['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(sound_df['Audio Path'], sound_df['Audio File']))))
    
    # GeMAPS features
    gemaps_extractor = module_gemaps.GeMAPSAnalyzer(module_gemaps.FeatureSet.eGeMAPSv02)
    sound_df = sound_df.merge(sound_df['Audio File Path'].progress_apply(lambda file: gemaps_extractor.process_file(file)), left_index=True, right_index=True)
    
    print("✅ Finished processing 'sound' analysis!")
    return sound_df