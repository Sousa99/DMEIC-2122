import os
import re
import math
import argparse

from abc                import ABC, abstractmethod
from enum               import Enum
from tqdm               import tqdm
from typing             import Dict, List, Optional
from consolemenu        import MultiSelectMenu, MenuFormatBuilder
from consolemenu.items  import FunctionItem

# =================================== IGNORE CERTAIN ERRORS ===================================

# ======================================= FLAGS PARSING =======================================

parser = argparse.ArgumentParser()
parser.add_argument("-transcriptions",  help="path to transcriptions")
args = parser.parse_args()

if (not args.transcriptions):
    print("🙏 Please provide a 'transcriptions' folder")
    exit(1)

# ===================================== CLASS DEFINITIONS =====================================

class Timestamp():

    TIMESTAMP_REGEX : str = '(\d+).(\d+)'
    def __init__(self, timestamp_str: str) -> None:
        matches = re.findall(self.TIMESTAMP_REGEX, timestamp_str)
        seconds, milliseconds = int(matches[0][0]), int(matches[0][1].rjust(3, '0'))

        self.milliseconds = milliseconds + seconds * 1000

    def format_timestamp(self) -> str:
        seconds = math.floor(self.milliseconds / 1000)
        milliseconds = self.milliseconds - seconds * 1000
        centiseconds = math.floor(milliseconds / 10)

        return f'{seconds}.{centiseconds:02}'

class InfoLine():

    def __init__(self, line: str) -> None:
        info_parts : List[str] = list(filter(lambda split: split != '', line.split()))

        self.file       : Optional[str]         = None if len(info_parts) <= 0 else info_parts[0]
        self.subject    : Optional[str]         = None if len(info_parts) <= 1 else info_parts[1]
        self.start      : Optional[Timestamp]   = None
        self.end        : Optional[Timestamp]   = None
        self.words      : Optional[List[str]]   = None if len(info_parts) <= 4 or info_parts[4] == '' else info_parts[4].split()
    
        if len(info_parts) >= 2:
            try: self.start = Timestamp(info_parts[2])
            except: pass
        if len(info_parts) >= 3:
            try: self.end = Timestamp(info_parts[3])
            except: pass

    def get_file(self) -> Optional[str]: return self.file
    def get_subject(self) -> Optional[str]: return self.subject
    def get_start_timestamp(self) -> Optional[str]: return self.start.format_timestamp() if self.start is not None else None
    def get_end_timestamp(self) -> Optional[str]: return self.end.format_timestamp() if self.end is not None else None
    def get_words(self) -> Optional[str]: return ' '.join(self.words) if self.words is not None else None

class TranscriptionInfo():

    def __init__(self, transcription_file: str) -> None:
        filename_split = transcription_file.split('_')

        self.group : str = self.parse_group(filename_split[0])
        self.subject : str = filename_split[1]
        self.task : str = filename_split[2]
        self.track : str = filename_split[3] if len(filename_split) > 3 else 'Not Specified'

    GROUP_MAPPINGS : Dict[str, str] = { 'c': 'Control', 'p': 'Psychosis', 'b': 'Bipolar'}
    def parse_group(self, group: str) -> str:
        if group in self.GROUP_MAPPINGS: return self.GROUP_MAPPINGS[group]
        else: raise Exception(f'Group mapping for \'{group}\' non-existent')

    def get_group(self) -> str: return self.group
    def get_subject(self) -> str: return self.subject
    def get_task(self) -> str: return self.task
    def get_track(self) -> str: return self.track

class Transcription():

    def __init__(self, filepath: str) -> None:
        file = open(filepath, 'r')
        lines = file.readlines()
        file.close()

        _, filename = os.path.split(filepath)

        self.transcription_info : TranscriptionInfo = TranscriptionInfo(filename)
        self.info_lines : List[InfoLine] = list(map(lambda line: InfoLine(line), lines))

    def get_transcription_info(self) -> TranscriptionInfo: return self.transcription_info
    def get_info_lines(self) -> List[InfoLine]: return self.info_lines

class TranscriptionsTestLevel(Enum):
    WARNING = 1
    ERROR = 2

class TranscriptionsTest(ABC):

    def __init__(self, name: str, level: TranscriptionsTestLevel) -> None:
        super().__init__()
        self.name = name
        self.level = level

    def get_name(self) -> str: return self.name

    @abstractmethod
    def process_transcription(self, transcription: Transcription) -> None:
        pass

    def raise_exception(self, transcription: Transcription, remaining_ats: List[str]) -> None:

        transcription_info : TranscriptionInfo = transcription.get_transcription_info()
        error_ats_message : List[str] = [ f'Group = \'{transcription_info.get_group()}\'', f'Subject = \'{transcription_info.get_subject()}\'',
            f'Task = \'{transcription_info.get_task()}\'', f'Track = \'{transcription_info.get_track()}\'']
        error_ats_message.extend(remaining_ats)
        error_ats_joined = ' : '.join(error_ats_message)

        if self.level == TranscriptionsTestLevel.WARNING: raise Exception(f'🟡 \'{self.name}\' Test Failed @ {error_ats_joined}')
        elif self.level == TranscriptionsTestLevel.ERROR: raise Exception(f'🔴 \'{self.name}\' Test Failed @ {error_ats_joined}')

# ==================================== AUXILIARY FUNCTIONS ====================================

# ====================================== TESTS DEFINITION ======================================

class TranscriptionTestWellFormatted(TranscriptionsTest):
    def __init__(self) -> None:
        super().__init__('Well Formatted', TranscriptionsTestLevel.ERROR)

    def process_transcription(self, transcription: Transcription) -> None:
        for info_line_number, info_line in enumerate(transcription.get_info_lines()):
            if info_line.get_file() is None: self.raise_exception(transcription, info_line_number + 1)
            if info_line.get_subject() is None: self.raise_exception(transcription, info_line_number + 1)
            if info_line.get_start_timestamp() is None: self.raise_exception(transcription, info_line_number + 1)
            if info_line.get_end_timestamp() is None: self.raise_exception(transcription, info_line_number + 1)
            if info_line.get_words() is None: self.raise_exception(transcription, info_line_number + 1)

    def raise_exception(self, transcription: Transcription, line_number: int) -> None:
        raise super().raise_exception(transcription, [f'Line = {line_number}'])

tests_to_be_carried_out : List[TranscriptionsTest] = [ TranscriptionTestWellFormatted() ]

# ===================================== MAIN FUNCTIONALITY =====================================

path_transcriptions : str = args.transcriptions
if not os.path.exists(args.transcriptions) or not os.path.isdir(args.transcriptions):
    raise Exception(f'🚨 Path for transcriptions \'{args.transcriptions}\' not recognized as a valid path')

transcriptions : List[Transcription] = []
transcription_tracks : List[str] = []

for group_folder in tqdm(os.listdir(path_transcriptions), leave=False, desc=f'🚀 Gathering groups'):
    path_transcriptions_group : str = os.path.join(path_transcriptions, group_folder)

    for subject_folder in tqdm(os.listdir(path_transcriptions_group), leave=False, desc=f'🚀 Gathering subjects in group \'{group_folder}\''):
        path_transcriptions_subjects : str = os.path.join(path_transcriptions_group, subject_folder)

        for task_folder in tqdm(os.listdir(path_transcriptions_subjects), leave=False, desc=f'🚀 Gathering tasks in subject \'{subject_folder}\''):
            path_transcriptions_tasks : str = os.path.join(path_transcriptions_subjects, task_folder)

            for track_filename in tqdm(os.listdir(path_transcriptions_tasks), leave=False, desc=f'🚀 Gathering tracks in task \'{task_folder}\''):
                path_transcription_file : str = os.path.join(path_transcriptions_tasks, track_filename)
                new_transcription = Transcription(path_transcription_file)
                new_transcription_info = new_transcription.get_transcription_info()
                new_transcription_track = new_transcription_info.get_track()

                transcriptions.append(new_transcription)
                if new_transcription_track not in transcription_tracks: transcription_tracks.append(new_transcription_track)

selected_groups : List[str] = []
def select_group(track: str) -> None:
    global selected_groups
    selected_groups.append(track)

track_selection_menu = MultiSelectMenu("📄  Select the tracks you wish to verify: ",
    epilogue_text=("Please select one or more entries separated by commas, and/or a range of numbers. For example: 1,2,3 or 1-4 or 1,3-4"))
track_selection_menu.formatter = MenuFormatBuilder()
for transcription_track in transcription_tracks:
    track_selection_menu.append_item(FunctionItem(f'Track {transcription_track}', select_group, args=[transcription_track]))
track_selection_menu.show()

for transcription_test in tests_to_be_carried_out:
    print(f'🚀 Carrying out \'{transcription_test.get_name()}\' transcription test')
    for transcription in transcriptions:
        if transcription.get_transcription_info().get_track() not in selected_groups:
            continue
        try: transcription_test.process_transcription(transcription)
        except Exception as e: print(e)
    print(f'🟢 Carried out \'{transcription_test.get_name()}\' transcription test')
    print()