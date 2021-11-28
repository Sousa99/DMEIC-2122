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
parser.add_argument("-save",        help="prefix of saved files")
parser.add_argument("-controls_data",    help="controls data path")
parser.add_argument("-psychosis_data",   help="psychosis data path")
parser.add_argument("-controls_rec",    help="controls recordings path")
parser.add_argument("-psychosis_rec",   help="psychosis recordings path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_data, 'key': 'controls_data', 'help': 'path to controls\' data'},
    { 'arg': args.psychosis_data, 'key': 'psychosis_data', 'help': 'path to psychosis\' data'},
    { 'arg': args.controls_rec, 'key': 'controls_rec', 'help': 'path to controls\' recordings'},
    { 'arg': args.psychosis_rec, 'key': 'psychosis_rec', 'help': 'path to psychosis\' recordings'},
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

def retrieveDurationInformation(recordings_path: str, df_info, type: str, tasks: List[str], processing_key: str):
    information = []
    subjects_dirs = os.listdir(recordings_path)
    number_of_subjects = len(subjects_dirs)

    printProgressBar(0, number_of_subjects, prefix = 'Processing ' + processing_key + ':', suffix = 'Complete', length = 50)
    for index_value, current_subject in enumerate(subjects_dirs):

        current_subject_path = os.path.join(recordings_path, current_subject)
        current_subject_id = current_subject.split('_')[1]

        for current_subject_task in os.listdir(current_subject_path):

            current_task_index = int(current_subject_task.replace(current_subject + '_', '')) - 1
            current_task = tasks[current_task_index]
            current_task_subject_path = os.path.join(current_subject_path, current_subject_task)

            entry = { 'id': current_subject, 'type': type, 'task': current_task }

            audio_files = os.listdir(current_task_subject_path)
            if len(audio_files) == 0: continue

            total_time = 0
            for file in audio_files:

                audio_path = os.path.join(current_task_subject_path, file)
                audio = AudioSegment.from_file(audio_path)
                total_time = total_time + audio.duration_seconds

            entry['duration'] = total_time / len(audio_files)
            # Append to entry information from xlsx
            for row, info in zip(df_info.columns, df_info.loc[current_subject_id]):
                entry[row.lower()] = info
            information.append(entry)
        
        printProgressBar(index_value + 1, number_of_subjects, prefix = 'Processing ' + processing_key + ':', suffix = 'Complete', length = 50)

    return information


# =================================== MAIN EXECUTION ===================================

TASKS = [ "Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7" ]

# ======================================================================================


# Retrieve Control Data
worksheet_name = args.controls_data.split('/')[-1].replace('.xlsx', '')
dataframe_control = pd.read_excel(args.controls_data, sheet_name = worksheet_name, index_col = 0)
controls_information = retrieveDurationInformation(args.controls_rec, dataframe_control, "Controls", TASKS, 'Controls')
# Retrieve Psychosis Data
worksheet_name = args.psychosis_data.split('/')[-1].replace('.xlsx', '')
dataframe_psychosis = pd.read_excel(args.psychosis_data, sheet_name = worksheet_name, index_col = 0)
psychosis_information = retrieveDurationInformation(args.psychosis_rec, dataframe_psychosis, "Psychosis", TASKS, 'Psychosis')

# Merge information into dataframe
information = controls_information + psychosis_information
task_df = pd.DataFrame(information)
task_df.set_index('id') 
#print(task_df)

sns.set_theme(palette="deep")

plt.clf()
sns.displot(data=task_df, x="duration", col="task", hue='type', multiple='dodge', kde=True, common_bins=False)
plt.savefig(args.save + ' - task duration by type.png')

plt.clf()
sns.displot(data=task_df, x="duration", row="gender", col="task", hue='type', multiple='dodge', kde=True, common_bins=False)
plt.savefig(args.save + ' - task duration by gender.png')

plt.clf()
sns.displot(data=task_df, x="duration", row="schooling", col="task", hue='type', multiple='dodge', kde=True, common_bins=False)
plt.savefig(args.save + ' - task duration by schooling.png')