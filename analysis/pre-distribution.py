import os
import math
import argparse
import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from typing import List
from pydub import AudioSegment

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",            help="prefix of saved files")
parser.add_argument("-controls_data",   help="controls data path")
parser.add_argument("-psychosis_data",  help="psychosis data path")
parser.add_argument("-controls_rec",    help="controls recordings path")
parser.add_argument("-psychosis_rec",   help="psychosis recordings path")
parser.add_argument("-controls_trans",    help="controls transcriptions path")
parser.add_argument("-psychosis_trans",   help="psychosis transcriptions path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_data, 'key': 'controls_data', 'help': 'path to \'controls\' data'},
    { 'arg': args.psychosis_data, 'key': 'psychosis_data', 'help': 'path to \'psychosis\' data'},
    { 'arg': args.controls_rec, 'key': 'controls_rec', 'help': 'path to \'controls\' recordings'},
    { 'arg': args.psychosis_rec, 'key': 'psychosis_rec', 'help': 'path to \'psychosis\' recordings'},
    { 'arg': args.controls_trans, 'key': 'controls_trans', 'help': 'path to \'controls\' transcriptions'},
    { 'arg': args.psychosis_trans, 'key': 'psychosis_trans', 'help': 'path to \'psychosis\' transcriptions'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    By: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def retrieveByTaskInformation(path: str, type: str, tasks: List[str], information_key: str, callback):
    information = []
    subjects_dirs = os.listdir(path)
    number_of_subjects = len(subjects_dirs)

    printProgressBar(0, number_of_subjects, prefix = 'Processing \'' + type + '\' '+ information_key + ':', suffix = 'Complete', length = 50)
    for index_value, current_subject in enumerate(subjects_dirs):

        current_subject_path = os.path.join(path, current_subject)

        for current_subject_task in os.listdir(current_subject_path):

            current_task_index = int(current_subject_task.replace(current_subject + '_', '')) - 1
            current_task = tasks[current_task_index]
            current_task_subject_path = os.path.join(current_subject_path, current_subject_task)

            files_path = list( map(lambda file: os.path.join(current_task_subject_path, file), os.listdir(current_task_subject_path)))
            value = callback(files_path)
            entry = { 'id': current_subject, 'type': type, 'task': current_task, information_key: value }
            information.append(entry)
        
        printProgressBar(index_value + 1, number_of_subjects, prefix = 'Processing \'' + type + '\' '+ information_key + ':', suffix = 'Complete', length = 50)

    return information

def callbackDuration(paths):

    if len(paths) == 0: return 0

    total_time = 0
    for file in paths:
        audio = AudioSegment.from_file(file)
        total_time = total_time + audio.duration_seconds

    return total_time / len(paths)

def callbackWordLength(paths):

    if len(paths) == 0: return 0

    total_words = 0
    for file_path in paths:
        file = open(file_path, 'r')
        total_words = total_words + len(file.read().split())
        file.close()

    return total_words / len(paths)

def mergeTasksInformation(info_df, type: str, tasks: List[str], infos, infos_columns):

    information = {}
    columns = info_df.columns

    # Append to entry information from xlsx
    for index, row in info_df.iterrows():
        for task in tasks:
            entry = { 'id': index, 'type': type }
            for column in columns: entry[column.lower()] = row[column]
            entry['task'] = task
            information[entry['id'] + '_' + entry['task']] = entry

    # Append each infos
    for info_column, info in zip(infos_columns, infos):
        for info_line in info:
            code = info_line['id'].split('_')[1] + '_' + info_line['task']
            if code in information: information[code][info_column] = info_line[info_column]

    return list(information.values())

# =================================== MAIN EXECUTION ===================================

TASKS = [ "Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7" ]

# ======================================================================================

# Retrieve Control Data
worksheet_name = args.controls_data.split('/')[-1].replace('.xlsx', '')
dataframe_control = pd.read_excel(args.controls_data, sheet_name = worksheet_name, index_col = 0)
controls_duration_information = retrieveByTaskInformation(args.controls_rec, "Control", TASKS, 'duration', callbackDuration)
controls_word_count_information = retrieveByTaskInformation(args.controls_trans, "Control", TASKS, 'word count', callbackWordLength)
controls_info = mergeTasksInformation(dataframe_control, 'Control', TASKS, [controls_duration_information, controls_word_count_information], ['duration', 'word count'])
# Retrieve Psychosis Data
worksheet_name = args.psychosis_data.split('/')[-1].replace('.xlsx', '')
dataframe_psychosis = pd.read_excel(args.psychosis_data, sheet_name = worksheet_name, index_col = 0)
psychosis_duration_information = retrieveByTaskInformation(args.psychosis_rec, "Psychosis", TASKS, 'duration', callbackDuration)
psychosis_word_count_information = retrieveByTaskInformation(args.psychosis_trans, "Psychosis", TASKS, 'word count', callbackWordLength)
psychosis_info = mergeTasksInformation(dataframe_psychosis, 'Psychosis', TASKS, [psychosis_duration_information, psychosis_word_count_information], ['duration', 'word count'])

# Merge information into dataframe
full_task_information = controls_info + psychosis_info
task_df = pd.DataFrame(full_task_information)
task_df.set_index('id') 
#print(task_df)

# ================================================================== DURATION ==================================================================

sns.set_theme(palette="deep")

plt.clf()
sns.displot(data=task_df, x="duration", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by type.png')

plt.clf()
sns.displot(data=task_df, x="duration", row="gender", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by gender.png')

plt.clf()
sns.displot(data=task_df, x="duration", row="schooling", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by schooling.png')

# ================================================================== WORD COUNT ==================================================================

sns.set_theme(palette="deep")

plt.clf()
sns.displot(data=task_df, x="word count", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - word count by type.png')