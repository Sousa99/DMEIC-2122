import os
import math
import shutil
import argparse

from typing import List
from numpy import floor
from pydub import AudioSegment

import pandas as pd

# =================================== IGNORE CERTAIN ERRORS ===================================

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-data",    help="path to folder with uncut audios")
parser.add_argument("-times",   help="file with cut times")
parser.add_argument("-output",  help="path to folder output")
parser.add_argument("-tag",     help="tag to be prefixed to folder")
args = parser.parse_args()

if ( not args.data or not args.times or not args.output or not args.tag):
    print("🙏 Please provide a 'data' folder, 'times' file, 'output' directory and 'tag'")
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def read_times(file_path: str, blacklist_rows: List[str]):
    dataframe = pd.read_json(file_path, orient='index')
    dataframe = dataframe.drop(blacklist_rows)

    return dataframe

def conver_time(time: float):

    minutes = math.floor(time)
    seconds = (time % 1) * 100

    return ((minutes * 60) + seconds) * 1000

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

# =================================== MAIN EXECUTION ===================================

BLACKLISTED_ROWS = ['template']
TASKS = ["Task1", "Task2", "Task3", "Task4", "Task5", "Task6", "Task7"]

# Get Cut Times
cut_times_dataframe = read_times(args.times, BLACKLISTED_ROWS)

# Remove existent output folder
if os.path.exists(args.output) and os.path.isdir(args.output):
    shutil.rmtree(args.output)

# Create directory
os.mkdir(args.output)

number_subjects = cut_times_dataframe.shape[0]
printProgressBar(0, number_subjects, prefix = 'Progress:', suffix = 'Complete', length = 50)
# Iteratively iterate each row
for index_value, (index, row) in enumerate(cut_times_dataframe.iterrows()):
    current_folder = args.tag + '_' + index
    current_subject_path = os.path.join(args.output, current_folder)

    os.mkdir(current_subject_path)

    # Get Audio Files
    audios_directory = os.path.join(args.data, index)
    audio_files = []
    for filename in os.listdir(audios_directory):
        audio_file = os.path.join(audios_directory, filename)
        if '_' in filename:
            suf = filename.split('_')[-1].split('.')[-2]
            audio_files.append({ 'file': audio_file, 'export_suf': '_' + suf, 'ext': os.path.splitext(filename)[-1] })
        else: audio_files.append({ 'file': audio_file, 'export_suf': '', 'ext': os.path.splitext(filename)[-1]})

    # Iterate tasks
    for index, value in row.items():
        current_sub_folder = current_folder + '_' + str(TASKS.index(index) + 1)
        current_task_path = os.path.join(current_subject_path, current_sub_folder)
        os.mkdir(current_task_path)

        # Not successful task
        if value == "": continue
        
        if not isinstance(value[0], list): value = [value]
        for audio_file in audio_files:

            final_audio = AudioSegment.empty()
            for time_interval in value:

                start = conver_time(time_interval[0])
                end = conver_time(time_interval[1])
                
                sub_audio = AudioSegment.from_file(audio_file['file'])
                sub_audio = sub_audio[start : end]
                final_audio = final_audio + sub_audio

            final_audio_export_path = os.path.join(current_task_path, current_sub_folder + audio_file['export_suf'] + audio_file['ext'])
            final_audio.export(final_audio_export_path, format=audio_file['ext'].replace('.', ''))

    # Print Progress
    printProgressBar(index_value + 1, number_subjects, prefix = 'Progress:', suffix = 'Complete', length = 50)