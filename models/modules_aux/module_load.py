import os
import sys

import pandas as pd

from typing             import Any, List
from typing_extensions  import TypedDict

# Local Modules - Auxiliary
import modules_aux.module_nlp   as module_nlp

# =================================== PRIVATE METHODS ===================================

def load_info_subjects(info_file: str, subjects_code_file_system: str, delimiter: str) -> pd.DataFrame:
    worksheet_name = info_file.split('/')[-1].replace('.xlsx', '')
    dataframe = pd.read_excel(info_file, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
    dataframe.index = subjects_code_file_system + delimiter + dataframe.index
    return dataframe

def subdivide_info_for_task(info: pd.DataFrame, audio_path: str, trans_path: str, tasks: List[str], delimiter: str) -> pd.DataFrame:
    info_by_task_dict = {}

    for subject, _ in info.iterrows():
        for task in tasks:

            task_id = delimiter.join([subject, str(task['code'])])
            # Add Information
            row_dict = {}
            row_dict['Subject'] = subject
            row_dict['Task'] = task['name']
            row_dict['Audio Path'] = os.path.join(audio_path, subject, task_id)
            row_dict['Trans Path'] = os.path.join(trans_path, subject, task_id)
            # Add to Info
            info_by_task_dict[task_id] = row_dict

    dataframe_by_task = pd.DataFrame.from_dict(info_by_task_dict, orient='index')
    return dataframe_by_task

def filter_path_exists(row: pd.Series) -> bool:
    columns = ['Audio Path', 'Trans Path']
    exists = True
    for column in columns:
        if not os.path.exists(row[column]): exists = False

    return exists

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class TranscriptionInfoItem():

    def __init__(self, info_line: str):
        line_split = info_line.split()
        info_words = " ".join(line_split[4: ])

        def convert_time_milliseconds(time: str) -> int:
            time_split : List[str] = time.split('.')

            minutes = int(time_split[0])
            seconds = int(time_split[1])
            milliseconds = int(time_split[2])

            return ((minutes * 60) + seconds) * 1000 + milliseconds

        info_start = convert_time_milliseconds(line_split[2])
        info_end = convert_time_milliseconds(line_split[3])

        self.start = info_start
        self.end = info_end
        self.words = info_words

    def get_words(self) -> str: return self.words

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class TranscriptionInfo():

    def __init__(self, file_path: str):
        self.transcription_info : List[TranscriptionInfoItem] = []

        file = open(file_path, 'r')
        for line in file.readlines():
            self.transcription_info.append(TranscriptionInfoItem(line.strip()))
        file.close()

    def get_info_items(self) -> List[TranscriptionInfoItem]:
        return self.transcription_info

    def get_words(self) -> List[str]:
        original_words : List[str] = []
        for info_item in self.transcription_info: original_words.extend(info_item.get_words().split())
        return original_words

    def lemmatize_words(self, lemmatizer: module_nlp.Lemmatizer) -> List[str]:
        original_words : List[str] = self.get_words()
        lemmatized_words : List[str] = lemmatizer.process_words(original_words)
        return lemmatized_words

# =================================== PUBLIC METHODS ===================================

def filter_info_dataset(info_subjects: pd.DataFrame) -> pd.DataFrame:
    # Filter By No Repetitions
    info_subjects = info_subjects[info_subjects['Already Recorded Before'] == 'No']
    # Filter By European Portuguese Language
    info_subjects = info_subjects[info_subjects['Language'] == 'European Portuguese']

    return info_subjects

LoadedDataset = TypedDict('LoadedDataset', { 'info': pd.DataFrame, 'paths': pd.DataFrame })
def load_dataset(subjects_code_file_system: str, info_file: str, audio_path: str, trans_path: str, tasks: List[str], delimiter: str = '_') -> LoadedDataset:
    info_subjects = load_info_subjects(info_file, subjects_code_file_system, delimiter)
    info_subjects = filter_info_dataset(info_subjects)

    subject_by_task_paths = subdivide_info_for_task(info_subjects, audio_path, trans_path, tasks, delimiter)
    
    valid_paths = subject_by_task_paths.apply(filter_path_exists, axis=1)
    subject_by_task_paths = subject_by_task_paths[valid_paths]
    return { 'info': info_subjects, 'paths': subject_by_task_paths }