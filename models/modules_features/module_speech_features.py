import os
import pyphen

import pandas as pd

from typing import List, Optional, Tuple
from pydub import AudioSegment

# Local Modules - Auxiliary
import modules_aux.module_aux                   as module_aux
import modules_aux.module_load                  as module_load
# Local Modules - Abstraction
import modules_abstraction.module_featureset    as module_featureset

# =================================== PRIVATE METHODS ===================================

def compute_number_of_words(trans_info: module_load.TranscriptionInfo) -> int:
    
    word_count = 0
    for trans_info_item in trans_info.get_info_items():
        word_count = word_count + len(trans_info_item.get_words().split())

    return word_count

def compute_number_of_syllables(trans_info: module_load.TranscriptionInfo) -> int:

    dic = pyphen.Pyphen(lang='pt_PT')
    syllables = 0

    for trans_info_item in trans_info.get_info_items():
        for word in trans_info_item.get_words().split():
            word_hyphenated = dic.inserted(word)
            word_syllables = len(word_hyphenated.split('-'))
            syllables = syllables + word_syllables

    return syllables

def compute_duration_track(audio_path: str) -> float:

    audio = AudioSegment.from_file(audio_path)
    return audio.duration_seconds

# =================================== FEATURE SET DEFINITION ===================================

FEATURE_SET_ID : str = 'speech'
class SpeechFeatureSet(module_featureset.FeatureSetAbstraction):

    def __init__(self) -> None:
        super().__init__(FEATURE_SET_ID)

    def develop_basis_df(self):
        if self.basis_dataframe is not None: return
        print(f"🚀 Preparing for '{self.id}' analysis ...")

        # Dataframe to study speech features
        basics_dataframe = self.paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path', 'Audio Path']]
        # Choose audio files from dictionary
        basics_dataframe['Audio File'] = basics_dataframe['Audio Path'].apply(module_aux.compute_file_paths, args=(self.preference_audio_tracks, None))
        basics_dataframe['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(basics_dataframe['Audio Path'], basics_dataframe['Audio File']))))
        # Choose trans files from dictionary
        basics_dataframe['Trans File'] = basics_dataframe['Trans Path'].apply(module_aux.compute_file_paths, args=(self.preference_trans, self.trans_extension))
        basics_dataframe = basics_dataframe.drop(basics_dataframe[basics_dataframe['Trans File'].isnull()].index)
        basics_dataframe['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(basics_dataframe['Trans Path'], basics_dataframe['Trans File']))))
        # Process Transcriptions
        basics_dataframe['Trans Info'] = basics_dataframe['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))
        
        # Save back 'basis dataframe' and 'drop_columns'
        self.basis_dataframe = basics_dataframe
        self.drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

    def develop_static_df(self):
        if self.static_dataframe is not None: return
        if self.basis_dataframe is None: self.develop_basis_df()
        static_dataframe = self.basis_dataframe.copy(deep=True)

        print(f"🚀 Developing '{self.id}' analysis ...")
        static_dataframe['Number Words'] = static_dataframe['Trans Info'].progress_apply(compute_number_of_words).astype(int)
        static_dataframe['Number Syllables'] = static_dataframe['Trans Info'].progress_apply(compute_number_of_syllables).astype(int)
        static_dataframe['Audio Duration (s)'] = static_dataframe['Audio File Path'].progress_apply(compute_duration_track).astype(int)
        static_dataframe['Speaking Rate (words / s)'] = static_dataframe['Number Words'] / (static_dataframe['Audio Duration (s)']).astype(int)
        static_dataframe['Articulation Rate (syllables / s)'] = static_dataframe['Number Syllables'] / (static_dataframe['Audio Duration (s)']).astype(int)
        
        # Save back 'static dataframe'
        self.static_dataframe = static_dataframe
        print(f"✅ Finished processing '{self.id}' analysis!")
    
    def develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        return (train_X, test_X)
