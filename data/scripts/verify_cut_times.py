import re
import os
import math
import json
import time
import argparse

import pandas   as pd

from pydub              import AudioSegment
from typing             import Any, Dict, List, Optional, Tuple, Union
from consolemenu        import SelectionMenu, MenuFormatBuilder
from pydub.playback     import play

# =================================== IGNORE CERTAIN ERRORS ===================================

# ======================================= FLAGS PARSING =======================================

parser = argparse.ArgumentParser()
parser.add_argument("-times_path", required=True, help="path to cut times")
parser.add_argument("-group_id", required=True, help="group characther id")
parser.add_argument("-recordings_path", required=False, help="path to recordings")
parser.add_argument("-alteration_path", required=False, help="path to file where processed tracks are stored")
parser.add_argument("-old_format", required=False, action='store_true', default=False, help="path to various curring times")
args = parser.parse_args()

# =================================== CONSTANTS DEFINITIONS ===================================

BLACKLISTED_ROWS : List[str] = ['template']
AUTO_INDENT_WORDS : List[Tuple[str, int]] = [ (' {', 1), ('"Task1"', 0), ('"Task2"', 0), ('"Task3"', 0),
    ('"Task4"', 0), ('"Task5"', 0), ('"Task6"', 0), ('"Task7"', 0), (' }', 1)]
TASKS : List[str] = ["Task1", "Task2", "Task3", "Task4", "Task5", "Task6", "Task7"]

CONSTANT_MILLISECONDS_INTERVAL : int = 2000
CONSTANT_SECONDS_BETWEEN_WAIT : int = 1

CONSTANT_ANSWER_ACCEPT : str = '🟢 Yes'
CONSTANT_ANSWER_REJECT : str = '🔴 No'

def constant_question_verify_subject(subject: str) -> str:
    return f'📄 Do you wish to verify subject \'{subject}\':'
def constant_question_audio_file() -> str:
    return f'📄 What audio file do you wish to listen to:'
def constant_question_change_fulcrum(current_time: str) -> str:
    return f'📄 Do you wish to change the current fulcrum point (milliseconds) currently \'{current_time}\'? '

def constant_statement_processing_subject_task(subject: str, task: str, stage: str) -> str:
    return f'📄 Processing subject \'{subject}\' on \'{task}\' and stage \'{stage}\'...'

# ===================================== CLASS DEFINITIONS =====================================

# ==================================== AUXILIARY FUNCTIONS ====================================

def read_cut_times(file_path: str, blacklist_rows: List[str]) -> pd.DataFrame:
    dataframe = pd.read_json(file_path, orient='index', precise_float=True)
    dataframe = dataframe.drop(blacklist_rows)

    return dataframe

def convert_df_old_format(old_df: pd.DataFrame) -> pd.DataFrame:
    def map_optional_list_to_mandatory(old_list: Union[str, List[float], List[List[float]]]) -> List[List[float]]:
        if isinstance(old_list, str) or (isinstance(old_list, list) and len(old_list) == 0): return [[]]
        elif isinstance(old_list[0], float): return [old_list]
        elif isinstance(old_list[0], int): return [ map(lambda elem: float(elem), old_list) ]
        else: return old_list

    def map_old_timestamp(old_ts: float) -> str:
        minutes = math.floor(old_ts / 1)
        seconds = round((old_ts - minutes) * 100)

        return f'{minutes}.{seconds:02}.000'

    def map_old_timeinterval(old_time_intervals: List[List[float]]) -> List[List[str]]:
        new_intervals : List[List[str]] = []
        for old_interval in old_time_intervals:
            new_interval = list(map(lambda timestamp: map_old_timestamp(timestamp), old_interval))
            new_intervals.append(new_interval)

        return new_intervals

    new_df = old_df.copy(deep=True)
    new_df = new_df.applymap(lambda cell: map_optional_list_to_mandatory(cell))
    new_df = new_df.applymap(lambda cell: map_old_timeinterval(cell))

    return new_df

def write_new_format(cut_times_df: pd.DataFrame, save_path: str, texts_to_ident: List[Tuple[str, int]]) -> None:
    result = cut_times_df.to_json(orient="index")
    parsed = json.loads(result)
    json_dumped = json.dumps(parsed, indent=4)

    json_dumped = re.sub('\s{8,}', ' ', json_dumped)
    json_dumped = re.sub('\[\s\[', '[[', json_dumped)
    json_dumped = re.sub('\]\s\]', ']]', json_dumped)
    json_dumped = re.sub('\s{5,}}', ' }', json_dumped)

    json_dumped_lines = json_dumped.split('\n')

    def space_text_to_common(text_indent: Tuple[str, int], lines: List[str], multiple: int) -> List[str]:
        max_index = 0
        for line in lines:
            index = line.find(text_indent[0])
            index_fixed = index + text_indent[1]
            if index != -1 and index_fixed > max_index: max_index = index_fixed
        index_indented = multiple * math.ceil(max_index / multiple)

        new_lines : List[str] = []
        for line in lines:
            current_index = line.find(text_indent[0])
            if current_index == -1:
                new_lines.append(line)
                continue

            current_index_fixed = current_index + text_indent[1]
            index_difference = index_indented - current_index_fixed
            
            line_start = line[:current_index_fixed]
            line_end = line[current_index_fixed:]
            extra_spaces = ''
            for _ in range(index_difference):
                extra_spaces = extra_spaces + ' '

            new_line = line_start + extra_spaces + line_end
            new_lines.append(new_line)

        return new_lines

    for text_to_ident in texts_to_ident:
        json_dumped_lines = space_text_to_common(text_to_ident, json_dumped_lines, 4)

    save_file = open(save_path, 'w')
    save_file.write('\n'.join(json_dumped_lines))
    save_file.close()

def convert_time_milliseconds(time: str) -> int:
    time_split : List[str] = time.split('.')

    minutes = int(time_split[0])
    seconds = int(time_split[1])
    milliseconds = int(time_split[2])

    return ((minutes * 60) + seconds) * 1000 + milliseconds

def convert_time_str(time_milliseconds: int) -> str:
    time_seconds : int = math.floor(time_milliseconds / 1000)
    time_minutes : int = math.floor(time_seconds / 60)

    milliseconds : int = time_milliseconds - time_seconds * 1000
    seconds : int = time_seconds - time_minutes * 60

    return f'{time_minutes}.{seconds:02}.{milliseconds:03}'

def selection_menu(valid_selections: List[str], menu_title: str) -> None:

    selection_menu = SelectionMenu(valid_selections, menu_title)
    selection_menu.formatter = MenuFormatBuilder()
    selection_menu.show()
    selection_index = selection_menu.selected_option
    if selection_index >= len(valid_selections): exit(1)

    return valid_selections[selection_index]

def verify_cut_time(audio_file_path: str, fulcrum_milliseconds: int) -> int:
    audio = AudioSegment.from_file(audio_file_path)

    changes : bool = True
    time_change : int = 0
    while changes:

        # Play before, wait, play after
        play(audio[fulcrum_milliseconds + time_change - CONSTANT_MILLISECONDS_INTERVAL : fulcrum_milliseconds + time_change])
        time.sleep(CONSTANT_SECONDS_BETWEEN_WAIT)
        play(audio[fulcrum_milliseconds + time_change : fulcrum_milliseconds + time_change + CONSTANT_MILLISECONDS_INTERVAL])
        
        print()
        current_time_str = convert_time_str(fulcrum_milliseconds + time_change)
        answer = input(constant_question_change_fulcrum(current_time_str))
        if answer == '': changes = False
        else:
            try: time_change = time_change + int(answer)
            except Exception as e: pass

        print()

    return time_change

def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

# ====================================== TESTS DEFINITION ======================================

# ===================================== MAIN FUNCTIONALITY =====================================

# Load cut times
if not os.path.exists(args.times_path) or not os.path.isfile(args.times_path):
    raise Exception(f"🚨 Cut time path '{args.times_path}' does not correspond to a valid file")
print(f"🚀 Processing cut times file '{args.times_path}' into dataframe")
cut_times_pandas = read_cut_times(args.times_path, [])

# Convert from old format into new format
if args.old_format:
    print(f"🚀 Converting cut times file '{args.times_path}' into new format")
    cut_times_pandas = convert_df_old_format(cut_times_pandas)
    print(f"🚀 Saving cut times file '{args.times_path}' in new format")
    write_new_format(cut_times_pandas, args.times_path, AUTO_INDENT_WORDS)

# Listen to and verify recordings cut times
if args.recordings_path:
    for row_index, row in cut_times_pandas.iterrows():
        choice = selection_menu([CONSTANT_ANSWER_ACCEPT, CONSTANT_ANSWER_REJECT], constant_question_verify_subject(row_index))
        if choice == CONSTANT_ANSWER_REJECT: continue

        subject_audio_path : str = os.path.join(args.recordings_path, row_index)
        audio_filenames : List[str] = os.listdir(subject_audio_path)
        audio_filename = selection_menu(audio_filenames, constant_question_verify_subject(row_index))
        audio_file_path = os.path.join(subject_audio_path, audio_filename)

        for column_index, interval in row.iteritems():


            start_milliseconds : int = convert_time_milliseconds(interval[0][0])
            duration_milliseconds : int = convert_time_milliseconds(interval[-1][-1])
            end_milliseconds : int = start_milliseconds + duration_milliseconds

            print(constant_statement_processing_subject_task(row_index, column_index, 'beginning'))
            start_change_milliseconds : int = verify_cut_time(audio_file_path, start_milliseconds)
            clear_screen()
            print(constant_statement_processing_subject_task(row_index, column_index, 'ending'))
            end_change_milliseconds : int = verify_cut_time(audio_file_path, end_milliseconds)
            clear_screen()

            new_interval = interval
            new_interval[0][0] = convert_time_str(start_milliseconds + start_change_milliseconds)
            new_interval[-1][-1] = convert_time_str(end_milliseconds - end_change_milliseconds)
            cut_times_pandas.loc[row_index].at[column_index] = new_interval
            write_new_format(cut_times_pandas, args.times_path, AUTO_INDENT_WORDS)