import os
import math
import argparse

from tqdm import tqdm
from typing import List
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

def read_times(file_path: str, blacklist_rows: List[str]) -> pd.DataFrame:
    dataframe = pd.read_json(file_path, orient='index')
    dataframe = dataframe.drop(blacklist_rows)

    return dataframe

def convert_time(time: float) -> int:

    minutes = math.floor(time)
    seconds = (time % 1) * 100

    return ((minutes * 60) + seconds) * 1000

# =================================== MAIN EXECUTION ===================================

BLACKLISTED_ROWS = ['template']
TASKS = ["Task1", "Task2", "Task3", "Task4", "Task5", "Task6", "Task7"]

# Get Cut Times
cut_times_dataframe = read_times(args.times, BLACKLISTED_ROWS)

if not os.path.exists(args.output) and os.path.isdir(args.output):
    # Create directory
    os.mkdir(args.output)

# Iteratively iterate each row
for index_value, (index, row) in tqdm(list(enumerate(cut_times_dataframe.iterrows())), desc="🚀 Processing subjects", leave=True):
    current_folder = args.tag + '_' + index
    current_subject_path = os.path.join(args.output, current_folder)
    if os.path.exists(current_subject_path): continue

    tqdm.write("🔊 Processed '{0}'".format(current_folder))
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

                start = convert_time(time_interval[0])
                end = convert_time(time_interval[1])

                if start > end: exit(f"🚨 End of track comes before start for subject '{current_folder}' and task '{index}'")
                
                sub_audio = AudioSegment.from_file(audio_file['file'])
                sub_audio = sub_audio[start : end]
                final_audio = final_audio + sub_audio

            final_audio_export_path = os.path.join(current_task_path, current_sub_folder + audio_file['export_suf'] + audio_file['ext'])
            final_audio.export(final_audio_export_path, format=audio_file['ext'].replace('.', ''))