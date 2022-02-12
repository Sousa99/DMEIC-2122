import os

import pandas as pd

from typing import List, Dict, TypedDict

# =================================== PRIVATE METHODS ===================================

def load_info_subjects(info_file: str, subjects_code_file_system: str, delimiter: str) -> pd.DataFrame:
    worksheet_name = info_file.split('/')[-1].replace('.xlsx', '')
    dataframe = pd.read_excel(info_file, sheet_name = worksheet_name, index_col = 0)
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
        info_words = " ".join(line_split[3: ])
        info_start = float(line_split[1])
        info_end = float(line_split[2])

        self.start = info_start
        self.end = info_end
        self.words = info_words

    def get_words(self) -> List[str]: self.words

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class TranscriptionInfo():

    def __init__(self, file_path: str):
        self.transcription_info = []

        file = open(file_path, 'r')
        for line in file.readlines():
            self.transcription_info.append(TranscriptionInfoItem(line))
        file.close()

    def get_info_items(self) -> List[TranscriptionInfoItem]: self.transcription_info   

# =================================== PUBLIC METHODS ===================================

LoadedDataset = TypedDict('LoadedDataset', { 'info': pd.DataFrame, 'paths': pd.DataFrame })
def load_dataset(subjects_code_file_system: str, info_file: str, audio_path: str, trans_path: str, tasks: List[str], delimiter: str = '_') -> LoadedDataset:
    info_subjects = load_info_subjects(info_file, subjects_code_file_system, delimiter)
    subject_by_task_paths = subdivide_info_for_task(info_subjects, audio_path, trans_path, tasks, delimiter)
    
    valid_paths = subject_by_task_paths.apply(filter_path_exists, axis=1)
    subject_by_task_paths = subject_by_task_paths[valid_paths]
    return { 'info': info_subjects, 'paths': subject_by_task_paths }