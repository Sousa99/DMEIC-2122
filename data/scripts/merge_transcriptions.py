import os
import re
import math
import shutil
import argparse

import pandas   as pd

from tqdm               import tqdm
from pydub              import AudioSegment
from typing             import Dict, List, Optional, Tuple
from consolemenu        import ConsoleMenu, MenuFormatBuilder
from pydub.playback     import play
from consolemenu.items  import FunctionItem, SelectionItem

# =================================== IGNORE CERTAIN ERRORS ===================================

# ======================================= FLAGS PARSING =======================================

parser = argparse.ArgumentParser()
parser.add_argument("-alteration_path", required=True, help="path to file where processed tracks are stored")
parser.add_argument("-merge_transcriptions_path", required=True, help="path to transcriptions to be merged in")
parser.add_argument("-new_transcriptions_path", required=True, help="path to transcriptions newly created")
parser.add_argument("-new_audio_path", required=True, help="path to audios already fixed")
args = parser.parse_args()

# =================================== CONSTANTS DEFINITIONS ===================================

TARGET_MERGE_FILE       : str               = 'Fix'
TARGET_NEW_FILE_ORDER   : List[str]         = ['Tr1', 'Tr2', 'Tr3', 'Tr4', 'LR']
TRANSCRIPTION_EXTENSION : str               = 'ctm'

GROUPS_CONVERSION       : Dict[str, str]    = { 'c': 'controls', 'p': 'psychosis', 'b': 'bipolars' }
JOIN_SYMBOL             : str               = '_'

DELAY_MILLISECONDS      : int               = 1000

# ===================================== CLASS DEFINITIONS =====================================

class Timestamp():

    TIMESTAMP_REGEX : str = '(\d+).(\d+)'
    def __init__(self, timestamp_str: str) -> None:
        matches = re.findall(self.TIMESTAMP_REGEX, timestamp_str)
        seconds, milliseconds = int(matches[0][0]), int(matches[0][1].ljust(3, '0'))

        self.milliseconds = milliseconds + seconds * 1000

    def get_milliseconds(self) -> int:
        return self.milliseconds
    def add_milliseconds(self, delay: int) -> None:
        self.milliseconds = self.milliseconds + delay

    def format_timestamp(self) -> str:

        positive_time : bool = True
        if self.milliseconds < 0:
            positive_time = False
            self.milliseconds = - self.milliseconds

        seconds = math.floor(self.milliseconds / 1000)
        milliseconds = self.milliseconds - seconds * 1000
        centiseconds = math.floor(milliseconds / 10)

        if positive_time: return f'{seconds}.{centiseconds:02}'
        else: return f'-{seconds}.{centiseconds:02}'

class InfoLine():

    def __init__(self, line: str) -> None:
        info_parts : List[str] = list(filter(lambda split: split != '', line.split()))

        self.file       : Optional[str]         = None if len(info_parts) <= 0 else info_parts[0]
        self.subject    : Optional[str]         = None if len(info_parts) <= 1 else info_parts[1]
        self.start      : Optional[Timestamp]   = None
        self.duration   : Optional[Timestamp]   = None
        self.word       : Optional[str]         = None if len(info_parts) <= 4 else ' '.join(info_parts[4:])
    
        if len(info_parts) >= 2:
            try: self.start = Timestamp(info_parts[2])
            except: pass
        if len(info_parts) >= 3:
            try: self.duration = Timestamp(info_parts[3])
            except: pass

    def get_file(self) -> Optional[str]: return self.file
    def get_subject(self) -> Optional[str]: return self.subject
    def get_start_timestamp(self) -> Optional[str]: return self.start.format_timestamp() if self.start is not None else None
    def get_duration_timestamp(self) -> Optional[str]: return self.duration.format_timestamp() if self.duration is not None else None
    def get_word(self) -> Optional[str]: return self.word

    def get_start(self) -> Optional[Timestamp]: return self.start if self.start is not None else None
    def get_duration(self) -> Optional[Timestamp]: return self.duration if self.duration is not None else None

    def format_line(self) -> str: return f'{self.file} {self.subject} {self.start.format_timestamp()} {self.duration.format_timestamp()} {self.word}'

class Transcription():

    def __init__(self, filepath: str) -> None:
        file = open(filepath, 'r')
        lines = file.readlines()
        file.close()

        self.filepath : str = filepath
        self.info_lines : List[InfoLine] = list(map(lambda line: InfoLine(line.strip()), lines))

    def get_info_lines(self) -> List[InfoLine]: return self.info_lines
    def set_info_lines(self, info_lines: List[InfoLine]) -> None: self.info_lines = info_lines

    def export_new(self) -> None:
        file = open(self.filepath, 'w')
        for info_line in self.info_lines:
            file.write(info_line.format_line() + '\n')
        file.close()

# ==================================== AUXILIARY FUNCTIONS ====================================

def compute_path(main_path: str, group_id: str, subject_id: str, task_id: str) -> str:
    
    group_folder : str = GROUPS_CONVERSION[group_id]
    subject_folder : str = JOIN_SYMBOL.join([group_id, subject_id])
    task_folder : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_id)])

    return os.path.join(main_path, group_folder, subject_folder, task_folder)

def merge_file(merge_path: str, group_id: str, subject_id: str, task_id: str) -> str:

    group_folder : str = GROUPS_CONVERSION[group_id]
    subject_folder : str = JOIN_SYMBOL.join([group_id, subject_id])
    task_folder : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_id)])

    filename : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_id), TARGET_MERGE_FILE]) + '.' + TRANSCRIPTION_EXTENSION
    return os.path.join(merge_path, group_folder, subject_folder, task_folder, filename)

def new_file(new_path: str, extension: Optional[str], group_id: str, subject_id: str, task_id: str) -> str:

    group_folder : str = GROUPS_CONVERSION[group_id]
    subject_folder : str = JOIN_SYMBOL.join([group_id, subject_id])
    task_folder : str = JOIN_SYMBOL.join([group_id, subject_id, str(task_id)])

    path_to_folder : str = os.path.join(new_path, group_folder, subject_folder, task_folder)
    available_files : List[str] = os.listdir(path_to_folder)
    if extension is not None: available_files = list(filter(lambda file: file.endswith('.' + extension), available_files))
    files : List[Tuple[str, str]] = list(map(lambda file: (file, os.path.splitext(file)[0]), available_files))

    selected_file : Optional[str] = None
    for prefered_extension in TARGET_NEW_FILE_ORDER:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0:
            selected_file = verifies_condition[0][0]
            break
    if selected_file is None:
        selected_file = available_files[0]

    return os.path.join(new_path, group_folder, subject_folder, task_folder, selected_file)

def convert_time_change_milliseconds(time: str) -> int:

    negative : bool = time.strip()[0] == '-'

    if negative: time = time.replace('-', '')
    time_split : List[str] = time.split('.')

    minutes = int(time_split[0])
    seconds = int(time_split[1])
    milliseconds = int(time_split[2])

    if negative: return - (((minutes * 60) + seconds) * 1000 + milliseconds)
    else: return ((minutes * 60) + seconds) * 1000 + milliseconds

def run_selection_menu(row: pd.Series) -> None:
    start_change_str : str = row['change start']
    start_different : bool = convert_time_change_milliseconds(start_change_str) != 0
    end_change_str : str = row['change end']
    end_different : bool = convert_time_change_milliseconds(end_change_str) != 0

    message = f'📄  Please fix the transcription \'start\' (change of {start_change_str}) and \'end\' (change of {end_change_str})'
    if start_different and not end_different: message = f'📄  Please fix the transcription \'start\' (change of {start_change_str})'
    if not start_different and end_different: message = f'📄  Please fix the transcription \'end\' (change of {end_change_str})'

    audio = AudioSegment.from_file(row['audio file'])
    def play_audio(audio, start, end):
        play(audio[max(start, 0) : min(end, len(audio))])

    option_selection_menu = ConsoleMenu(message, show_exit_option=False)
    option_selection_menu.formatter = MenuFormatBuilder()
    if start_different:
        play_end_milliseconds : int = max( - convert_time_change_milliseconds(row['change start']), 0 ) + DELAY_MILLISECONDS
        option_selection_menu.append_item(FunctionItem(f'🛫 Play start of audio', play_audio, args=(audio, 0, play_end_milliseconds)))
    if end_different:
        play_start_milliseconds : int = min( len(audio) - convert_time_change_milliseconds(row['change end']), len(audio) ) - DELAY_MILLISECONDS
        option_selection_menu.append_item(FunctionItem(f'🛬 Play end of audio', play_audio, args=(audio, play_start_milliseconds, len(audio))))
    option_selection_menu.append_item(SelectionItem('🟢 Done with changes', 10))
        
    option_selection_menu.start()
    option_selection_menu.join()

# ===================================== MAIN FUNCTIONALITY =====================================

if not os.path.exists(args.alteration_path) or not os.path.isfile(args.alteration_path):
    print(f"🚨 File \'{args.alteration_path}\' given as 'alteration_path' does not exist")

alterations_df = pd.read_csv(args.alteration_path, sep='\t', index_col=[0, 1, 2])
alterations_df['merge path'] = alterations_df.index.to_series().apply(lambda index: compute_path(args.merge_transcriptions_path, index[0], index[1], index[2]))
alterations_df['new path'] = alterations_df.index.to_series().apply(lambda index: compute_path(args.new_transcriptions_path, index[0], index[1], index[2]))
alterations_df['merge file'] = alterations_df.index.to_series().apply(lambda index: merge_file(args.merge_transcriptions_path, index[0], index[1], index[2]))
alterations_df['new file'] = alterations_df.index.to_series().apply(lambda index: new_file(args.new_transcriptions_path, TRANSCRIPTION_EXTENSION, index[0], index[1], index[2]))
alterations_df['audio file'] = alterations_df.index.to_series().apply(lambda index: new_file(args.new_audio_path, None, index[0], index[1], index[2]))

with tqdm(alterations_df.iterrows(), desc='🚀 Processing changes', leave=True) as progress_iterator:
    for row_index, row in progress_iterator:

        # Copy files from new path to merge path
        for new_filename in os.listdir(row['new path']):
            if not new_filename.endswith('.' + TRANSCRIPTION_EXTENSION):
                continue
            new_filepath : str = os.path.join(row['new path'], new_filename)
            shutil.copy(new_filepath, row['merge path'])

        transcription : Transcription = Transcription(row['merge file'])
        # Move target file start by correct duration
        start_adjustment : int = convert_time_change_milliseconds(row['change start'])
        for info_line in transcription.get_info_lines():
            start_timestamp = info_line.get_start()
            start_timestamp.add_milliseconds(-start_adjustment)
        # Remove target file lines start before 0
        end_time : int = convert_time_change_milliseconds(row['new end time'])
        old_info_lines : List[InfoLine] = transcription.get_info_lines()
        new_info_lines : List[InfoLine] = list(filter(lambda info_line: info_line.get_start().get_milliseconds() >= 0, old_info_lines))
        transcription.set_info_lines(new_info_lines)
        # Remove target file lines end after final time
        end_time : int = convert_time_change_milliseconds(row['new end time']) - convert_time_change_milliseconds(row['new start time'])
        old_info_lines : List[InfoLine] = transcription.get_info_lines()
        new_info_lines : List[InfoLine] = list(filter(lambda info_line: (info_line.get_start().get_milliseconds() + info_line.get_duration().get_milliseconds()) <= end_time, old_info_lines))
        transcription.set_info_lines(new_info_lines)
        # Save back file
        transcription.export_new()

        # Open both files
        os.system(f"code -d {row['merge file']} {row['new file']}")
        
        # Ask what to do
        progress_iterator.clear()
        run_selection_menu(row)
        progress_iterator.refresh()

        # Remove current row from alterations df
        alterations_df.drop(alterations_df.head(1).index, inplace=True)
        alterations_df.drop(columns=['merge path', 'new path', 'merge file', 'new file', 'audio file']).to_csv(args.alteration_path, sep='\t')