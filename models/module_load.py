import os
import argparse
import warnings

import pandas as pd

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-code_controls",   help="code for subjects in control")
parser.add_argument("-code_psychosis",   help="code for subjects in psychosis")
parser.add_argument("-info_controls",   help="path to info file from controls")
parser.add_argument("-info_psychosis",   help="path to info file from psychosis")
parser.add_argument("-audio_controls",   help="path to audio segments from controls")
parser.add_argument("-audio_psychosis",   help="path to audio segments from psychosis")
parser.add_argument("-trans_controls",   help="path to transcription files from controls")
parser.add_argument("-trans_psychosis",   help="path to transcription files from psychosis")
args = parser.parse_args()

requirements = [
    { 'arg': args.code_controls, 'key': 'code_controls', 'help': 'code for subjects in control'},
    # { 'arg': args.code_psychosis, 'key': 'code_psychosis', 'help': 'code for subjects in psychosis'},
    { 'arg': args.info_controls, 'key': 'info_controls', 'help': 'path to info file from controls'},
    # { 'arg': args.info_psychosis, 'key': 'info_psychosis', 'help': 'path to info file from psychosis'},
    { 'arg': args.audio_controls, 'key': 'audio_controls', 'help': 'path to audio segments from controls'},
    # { 'arg': args.audio_psychosis, 'key': 'audio_psychosis', 'help': 'path to audio segments from psychosis'},
    { 'arg': args.trans_controls, 'key': 'trans_controls', 'help': 'path to transcriptions files from controls'},
    # { 'arg': args.trans_psychosis, 'key': 'trans_psychosis', 'help': 'path to transcriptions files from psychosis'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== PRIVATE METHODS ===================================

def load_info_subjects(info_file):
    worksheet_name = info_file.split('/')[-1].replace('.xlsx', '')
    dataframe = pd.read_excel(info_file, sheet_name = worksheet_name, index_col = 0)
    return dataframe

def subdivide_info_for_task(info, subjects_code, audio_path, trans_path, tasks, delimiter):
    info_by_task_dict = {}

    for subject, row in info.iterrows():
        for task in tasks:

            subject_id = delimiter.join([subjects_code, subject])
            task_id = delimiter.join([subjects_code, subject, str(task['code'])])
            row_dict = row.to_dict()
            # Add Extra Information
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

def load_dataset(subjects_code, info_file, audio_path, trans_path, tasks, delimiter):
    info_subjects = load_info_subjects(info_file)
    info_subject_by_task = subdivide_info_for_task(info_subjects, subjects_code, audio_path, trans_path, tasks, delimiter)

    valid_paths = info_subject_by_task.apply(filter_path_exists, axis=1)
    info_subject_by_task = info_subject_by_task[valid_paths]
    print(info_subject_by_task)

# =================================== PUBLIC METHODS ===================================

def load(tasks, delimiter = '_'):
    load_dataset(args.code_controls, args.info_controls, args.audio_controls, args.trans_controls, tasks, delimiter)

# =================================== TO BE REMOVED ===================================

TASKS = [ {'code': 1, 'name': 'Task 1'},  {'code': 2, 'name': 'Task 2'},  {'code': 3, 'name': 'Task 3'}, 
    {'code': 4, 'name': 'Task 4'}, {'code': 5, 'name': 'Task 5'}, {'code': 6, 'name': 'Task 6'}, {'code': 7, 'name': 'Task 7'}]

load(TASKS)