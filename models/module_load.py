import os

import pandas as pd

from typing import Any, List, Dict, TypedDict

# Local Modules
import module_classifier

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

    def get_words(self) -> List[str]: return self.words

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class TranscriptionInfo():

    def __init__(self, file_path: str):
        self.transcription_info = []

        file = open(file_path, 'r')
        for line in file.readlines():
            self.transcription_info.append(TranscriptionInfoItem(line))
        file.close()

    def get_info_items(self) -> List[TranscriptionInfoItem]: return self.transcription_info   

class Variation():

    def __init__(self, variation_info: Dict[str, str], datasets_infos: Dict[str, Dict[str, Any]]) -> None:
        self.load_features(variation_info['features'], datasets_infos)
        self.load_tasks(variation_info['tasks'])
        self.load_classifier(variation_info['classifier'])

    def load_features(self, key_features: str, dataset_infos: Dict[str, Dict[str, Any]]) -> None:

        if key_features not in dataset_infos: exit("🚨 Code for dataset '{0}' not recognized from '{1}'".format(key_features, list(dataset_infos.keys()))) 

        temp_dataset_info = dataset_infos[key_features]
        self.features_code = key_features
        self.features = temp_dataset_info['features'].copy(deep=True)
        self.drop_columns = temp_dataset_info['drop_columns']
        self.feature_columns = temp_dataset_info['feature_columns']

    def load_tasks(self, key_tasks: str) -> None:

        if key_tasks == 'Task 1': temp_tasks = ['Task 1']
        elif key_tasks == 'Task 2': temp_tasks = ['Task 2']
        elif key_tasks == 'Task 3': temp_tasks = ['Task 3']
        elif key_tasks == 'Task 4': temp_tasks = ['Task 4']
        elif key_tasks == 'Task 5': temp_tasks = ['Task 5']
        elif key_tasks == 'Task 6': temp_tasks = ['Task 6']
        elif key_tasks == 'Task 7': temp_tasks = ['Task 7']

        elif key_tasks == 'Verbal Fluency': temp_tasks = ['Task 1', 'Task 2']
        elif key_tasks == 'Reading + Retelling': temp_tasks = ['Task 3', 'Task 4']
        elif key_tasks == 'Description Affective Images': temp_tasks = ['Task 5', 'Task 6', 'Task 7']
        else: exit("🚨 Code for tasks '{0}' not recognized".format(key_tasks))

        self.tasks_code = key_tasks
        self.tasks = temp_tasks

    def load_classifier(self, key_classifier: str) -> None:
        temp_classifier = module_classifier.convert_key_to_classifier(key_classifier)

        self.classifier_code = key_classifier
        self.classifier_code_small = temp_classifier[0]
        self.classifier = temp_classifier[1]

    def generate_code(self) -> str:
        return ' - '.join([self.classifier_code_small, self.features_code, self.tasks_code])

# =================================== PUBLIC METHODS ===================================

LoadedDataset = TypedDict('LoadedDataset', { 'info': pd.DataFrame, 'paths': pd.DataFrame })
def load_dataset(subjects_code_file_system: str, info_file: str, audio_path: str, trans_path: str, tasks: List[str], delimiter: str = '_') -> LoadedDataset:
    info_subjects = load_info_subjects(info_file, subjects_code_file_system, delimiter)
    subject_by_task_paths = subdivide_info_for_task(info_subjects, audio_path, trans_path, tasks, delimiter)
    
    valid_paths = subject_by_task_paths.apply(filter_path_exists, axis=1)
    subject_by_task_paths = subject_by_task_paths[valid_paths]
    return { 'info': info_subjects, 'paths': subject_by_task_paths }