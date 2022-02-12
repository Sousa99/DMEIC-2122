import os
import pyphen

import pandas as pd

from typing import List
from numpy import number
from pydub import AudioSegment

# Local Modules
import module_load

# =================================== PRIVATE METHODS ===================================

def compute_file_paths(trans_path: str, extension_preference_order: List[str], extension: str) -> str:

    _, _, files_full = list(os.walk(trans_path))[0]
    if extension != None: files_full = filter(lambda file: os.path.splitext(file)[1] == extension, files_full)
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    if len(files) == 0: return None
    return files[0][0]

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

# =================================== PUBLIC METHODS ===================================

def speech_analysis(paths_df: pd.DataFrame, preference_audio_tracks: List[str], preference_trans: List[str], trans_extension: str) -> pd.DataFrame:

    # Dataframe to study speech features
    speech_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path', 'Audio Path']]
    # Choose audio files from dictionary
    speech_df['Audio File'] = speech_df['Audio Path'].apply(compute_file_paths, args=(preference_audio_tracks, None))
    speech_df['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(speech_df['Audio Path'], speech_df['Audio File']))))
    # Choose trans files from dictionary
    speech_df['Trans File'] = speech_df['Trans Path'].apply(compute_file_paths, args=(preference_trans, trans_extension))
    speech_df = speech_df.drop(speech_df[speech_df['Trans File'].isnull()].index)
    speech_df['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(speech_df['Trans Path'], speech_df['Trans File']))))
    # Process Transcriptions
    speech_df['Trans Info'] = speech_df['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))

    # Speaking Rate
    speech_df['Number Words'] = speech_df['Trans Info'].apply(compute_number_of_words)
    speech_df['Number Syllables'] = speech_df['Trans Info'].apply(compute_number_of_syllables)
    speech_df['Audio Duration (s)'] = speech_df['Audio File Path'].apply(compute_duration_track)
    speech_df['Speaking Rate (words / s)'] = speech_df['Number Words'] / (speech_df['Audio Duration (s)'])
    speech_df['Articulation Rate (syllables / s)'] = speech_df['Number Syllables'] / (speech_df['Audio Duration (s)'])

    return speech_df