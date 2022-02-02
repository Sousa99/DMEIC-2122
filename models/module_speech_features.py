import os
import pyphen

import pandas as pd

from pydub import AudioSegment

# =================================== PRIVATE METHODS ===================================

def compute_file_paths(trans_path, extension_preference_order, extension):

    _, _, files_full = list(os.walk(trans_path))[0]
    if extension != None: files_full = filter(lambda file: os.path.splitext(file)[1] == extension, files_full)
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    if len(files) == 0: return None
    return files[0][0]

def compute_number_of_words(file_path):
    
    # FIXME: Take into account file structure
    file = open(file_path, 'r')
    words_per_line = map(lambda line: len(line.split()), file.readlines())
    file.close()
    return sum(words_per_line)

def compute_number_of_syllables(file_path):

    dic = pyphen.Pyphen(lang='pt_PT')
    syllables = 0

    file = open(file_path, 'r')
    for line in file.readlines():
        for word in line.split():
            word_hyphenated = dic.inserted(word)
            word_syllables = len(word_hyphenated.split('-'))
            syllables = syllables + word_syllables
    file.close()

    return syllables

def compute_duration_track(audio_path):

    audio = AudioSegment.from_file(audio_path)
    return audio.duration_seconds

# =================================== PUBLIC METHODS ===================================

def speech_analysis(paths_df, preference_audio_tracks, preference_trans, trans_extension):

    # Dataframe to study speech features
    speech_df = paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path', 'Audio Path']]
    # Choose audio files from dictionary
    speech_df['Audio File'] = speech_df['Audio Path'].apply(compute_file_paths, args=(preference_audio_tracks, None))
    speech_df['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(speech_df['Audio Path'], speech_df['Audio File']))))
    # Choose trans files from dictionary
    speech_df['Trans File'] = speech_df['Trans Path'].apply(compute_file_paths, args=(preference_trans, trans_extension))
    speech_df = speech_df.drop(speech_df[speech_df['Trans File'].isnull()].index)
    speech_df['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(speech_df['Trans Path'], speech_df['Trans File']))))
    
    # Speaking Rate
    speech_df['Number Words'] = speech_df['Trans File Path'].apply(compute_number_of_words)
    speech_df['Number Syllables'] = speech_df['Trans File Path'].apply(compute_number_of_syllables)
    speech_df['Audio Duration (s)'] = speech_df['Audio File Path'].apply(compute_duration_track)
    speech_df['Speaking Rate (words / s)'] = speech_df['Number Words'] / (speech_df['Audio Duration (s)'])
    speech_df['Articulation Rate (syllables / s)'] = speech_df['Number Syllables'] / (speech_df['Audio Duration (s)'])

    return speech_df