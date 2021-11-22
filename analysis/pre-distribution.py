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

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",        help="prefix of saved files")
parser.add_argument("-controls",    help="controls recordings path")
parser.add_argument("-psychosis",   help="psychosis recordings path")
args = parser.parse_args()

if ( not args.controls or not args.psychosis or not args.save ):
    print("🙏 Please provide a 'save' file prefix, and a 'control' and 'psychosis' recordings path")
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
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

def retrieveDurationInformation(recordings_path: str, type: str, tasks: List[str], processing_key: str):
    information = []
    subjects_dirs = os.listdir(recordings_path)
    number_of_subjects = len(subjects_dirs)

    printProgressBar(0, number_of_subjects, prefix = 'Processing ' + processing_key + ':', suffix = 'Complete', length = 50)
    for index_value, current_subject in enumerate(subjects_dirs):

        entry = { 'id': current_subject, 'type': type }
        for task in tasks: entry[task] = 0

        current_subject_path = os.path.join(recordings_path, current_subject)
        for current_subject_task in os.listdir(current_subject_path):

            current_task_index = int(current_subject_task.replace(current_subject + '_', '')) - 1
            current_task = tasks[current_task_index]
            current_task_subject_path = os.path.join(current_subject_path, current_subject_task)

            audio_files = os.listdir(current_task_subject_path)
            if len(audio_files) == 0: continue

            total_time = 0
            for file in audio_files:

                audio_path = os.path.join(current_task_subject_path, file)
                audio = AudioSegment.from_file(audio_path)
                total_time = total_time + audio.duration_seconds

            entry[current_task] = total_time / len(audio_files)

        information.append(entry)
        printProgressBar(index_value + 1, number_of_subjects, prefix = 'Processing ' + processing_key + ':', suffix = 'Complete', length = 50)

    return information


# =================================== MAIN EXECUTION ===================================

SAVE_PATH = "./records/"

TASKS = [ "Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7" ]

PLOT_ROWS = 2
PLOT_COLUMNS_TASK = math.ceil(len(TASKS) / PLOT_ROWS)

# ======================================================================================

# Retrieve Control Data
controls_information = retrieveDurationInformation(args.controls, "Controls", TASKS, 'Controls')
# Retrieve Psychosis Data
psychosis_information = retrieveDurationInformation(args.psychosis, "Psychosis", TASKS, 'Psychosis')

# Merge information into dataframe
information = controls_information + psychosis_information
duration_df = pd.DataFrame(information)
for index, task in enumerate(TASKS):
    plt.clf()
    sns.histplot(duration_df, x=task, hue="type")
    plt.savefig(SAVE_PATH + args.save + ' - ' + task + ' - duration.png')