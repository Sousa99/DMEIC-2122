import os

import pandas as pd

# =================================== PRIVATE METHODS ===================================

def load_info_subjects(info_file):
    worksheet_name = info_file.split('/')[-1].replace('.xlsx', '')
    dataframe = pd.read_excel(info_file, sheet_name = worksheet_name, index_col = 0)
    return dataframe

def subdivide_info_for_task(info, subjects_code_file_system, audio_path, trans_path, tasks, delimiter):
    info_by_task_dict = {}

    for subject, _ in info.iterrows():
        for task in tasks:

            subject_id = delimiter.join([subjects_code_file_system, subject])
            task_id = delimiter.join([subjects_code_file_system, subject, str(task['code'])])
            # Add Information
            row_dict = {}
            row_dict['Subject'] = subject
            row_dict['Task'] = task['name']
            row_dict['Audio Path'] = os.path.join(audio_path, subject_id, task_id)
            row_dict['Trans Path'] = os.path.join(trans_path, subject_id, task_id)
            # Add to Info
            info_by_task_dict[task_id] = row_dict

    dataframe_by_task = pd.DataFrame.from_dict(info_by_task_dict, orient='index')
    return dataframe_by_task

def filter_path_exists(row):
    columns = ['Audio Path', 'Trans Path']
    exists = True
    for column in columns:
        if not os.path.exists(row[column]): exists = False

    return exists

# =================================== PUBLIC METHODS ===================================

def load_dataset(subjects_code_file_system, info_file, audio_path, trans_path, tasks, delimiter = '_'):
    info_subjects = load_info_subjects(info_file)
    subject_by_task_paths = subdivide_info_for_task(info_subjects, subjects_code_file_system, audio_path, trans_path, tasks, delimiter)
    
    valid_paths = subject_by_task_paths.apply(filter_path_exists, axis=1)
    subject_by_task_paths = subject_by_task_paths[valid_paths]
    return { 'info': info_subjects, 'paths': subject_by_task_paths }