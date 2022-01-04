import os
import math
import argparse
import warnings

import numpy                as np
import pandas               as pd
import seaborn              as sns
import matplotlib.pyplot    as plt

from copy                   import deepcopy
from pydub                  import AudioSegment
from typing                 import List
from consolemenu            import SelectionMenu
from pydub.playback         import play
from nltk.metrics.distance  import edit_distance

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-audio",   help="path to audio file")
parser.add_argument("-trans",   help="path to transcription file")
args = parser.parse_args()

requirements = [
    { 'arg': args.audio, 'key': 'audio', 'help': 'path to audio files'},
    { 'arg': args.trans, 'key': 'trans', 'help': 'path to transcriptions file'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def convert_time_to_milliseconds(time: float):

    seconds = math.floor(time)
    milliseconds = (time % 1) * 1000

    return seconds * 1000 + milliseconds

def convert_milliseconds_to_time(time_milliseconds: float):

    seconds = math.floor(time_milliseconds / 1000)
    milliseconds = (time_milliseconds % 1000) / 1000

    return round(seconds + milliseconds, 2)

def map_lines_to_info(lines: List[str]):

    first_line_split_tmp = lines[0].split()
    file =  first_line_split_tmp[0]
    source = first_line_split_tmp[1]

    def map_line(line: str):
        line_split = line.split()
        start_timestamp = convert_time_to_milliseconds(float(line_split[2]))
        duration_timestamp = convert_time_to_milliseconds(float(line_split[3]))
        word = line_split[4]

        return { 'start': start_timestamp, 'duration': duration_timestamp, 'word': word }

    lines_mapped = map(lambda line: map_line(line), lines)
    return { 'file': file, 'source': source, 'lines': list(lines_mapped) }

# =================================== MAIN EXECUTION ===================================

SPLIT_SYMBOL = '_'
AUDIO_EXTENSION = '.wav'
TRANSCRIPTION_EXTENSION = '.ctm'
OUTPUT_SUFFIX = 'Fix'

NOTHING_HEARD_DISPLAY = 'NOTHING'

# =================================== MAIN EXECUTION ===================================

file_possibilities = os.listdir(args.trans)
file_selection_menu = SelectionMenu(file_possibilities, "📄  Select one file as the main template:")

file_selection_menu.show()
file_selection_menu.join()
selected_file_index = file_selection_menu.selected_option
if selected_file_index >= len(file_possibilities): exit(1)

selected_file = file_possibilities[selected_file_index]

FILENAME, _ = os.path.splitext(selected_file)
PATH_TO_AUDIO = os.path.join(args.audio, FILENAME + AUDIO_EXTENSION)
PATH_TO_TRANS = os.path.join(args.trans, FILENAME + TRANSCRIPTION_EXTENSION)
PATH_TO_OUT_TRANS = os.path.join(args.trans, SPLIT_SYMBOL.join(FILENAME.split(SPLIT_SYMBOL)[:-1]) + SPLIT_SYMBOL + OUTPUT_SUFFIX + TRANSCRIPTION_EXTENSION)

# ======================================================================================

# Read Transcription File
transcription_file = open(PATH_TO_TRANS)
transcription_lines = transcription_file.readlines()
transcription_file.close()

# Get Current Info
transcription_info = map_lines_to_info(transcription_lines)
audio = AudioSegment.from_file(PATH_TO_AUDIO)

current_input_line_index = 0
current_start_time = 0
current_time = 0
end_time = len(audio)

# ===================================================== MENU POSSIBILITIES =====================================================
REPEAT_ID = 0
REPEAT = '🔁\t Re-listen'
NEXT_ID = 1
NEXT = '⏭\t Evaluate Next Track'
GO_BACK_ID = 2
GO_BACK = '◀️\t Go Back to Previous State'
CHANGE_ID = 3
CHANGE = '✏️\t Change Word Associated'
JOIN_NEXT_ID = 4
JOIN_NEXT = '🙏\t Join with next timestep'
MENU = [ REPEAT, NEXT, GO_BACK, CHANGE, JOIN_NEXT ]
# ===================================================== MENU POSSIBILITIES =====================================================

memory = []
heard = []
output_lines = []
while current_start_time != end_time and current_input_line_index < len(transcription_info['lines']):

    memory.append({
        'current_start_time': current_start_time, 'current_time': current_time,
        'current_input_line_index': current_input_line_index,
        'heard': deepcopy(heard),
        'output_lines': deepcopy(output_lines),
    })

    current_input_line = transcription_info['lines'][current_input_line_index]
    stop_time, next_line_index = None, None

    # Nothing should be said here
    if current_input_line['start'] > current_time:
        stop_time = current_input_line['start']
        next_line_index = current_input_line_index

    elif current_input_line['start'] <= current_time:
        heard.append(current_input_line['word'])
        stop_time = current_input_line['start'] + current_input_line['duration']
        next_line_index = current_input_line_index + 1

    play(audio[current_start_time : stop_time])
    heard_display = NOTHING_HEARD_DISPLAY
    if len(heard) != 0: heard_display = ' + '.join(heard)
    from_ts = convert_milliseconds_to_time(current_start_time)
    to_ts = convert_milliseconds_to_time(stop_time)

    # Display Menu
    action_menu = SelectionMenu(MENU, "👂 You heard '{0}' ({1:.2f} → {2:.2f}) ...".format(heard_display, from_ts, to_ts))
    action_menu.show()
    action_menu.join()
    selected_action_index = action_menu.selected_option
    if selected_action_index >= len(MENU): exit(1)

    # Deal with action
    if selected_action_index == NEXT_ID:
        output_lines.append({'start': current_start_time, 'duration': stop_time - current_start_time, 'word': '+'.join(heard) })
        heard = []

        current_start_time = stop_time
        current_time = current_start_time
        current_input_line_index = next_line_index

    elif selected_action_index == CHANGE_ID:
        heard = [ str(input("✏️  What is the correct value to be inserted? ")) ]
        output_lines.append({'start': current_start_time, 'duration': stop_time - current_start_time, 'word': '+'.join(heard) })
        heard = []

        current_start_time = stop_time
        current_time = current_start_time
        current_input_line_index = next_line_index

    elif selected_action_index == JOIN_NEXT_ID:
        current_time = stop_time
        current_input_line_index = next_line_index

    elif selected_action_index == GO_BACK_ID:

        if len(memory) < 2: continue
        # Remove just added
        memory.pop()
        # Update to last correct
        memory_item = memory.pop()

        current_start_time = memory_item['current_start_time']
        current_time = memory_item['current_time']
        current_input_line_index = memory_item['current_input_line_index']
        heard = memory_item['heard']
        output_lines = memory_item['output_lines']
        
# Write to Fix File
file = open(PATH_TO_OUT_TRANS, 'w')
for out_line in output_lines:
    if out_line['word'] == '': continue

    infos = [ transcription_info['file'], transcription_info['source'] ]
    infos.append(str(convert_milliseconds_to_time(out_line['start'])))
    infos.append(str(convert_milliseconds_to_time(out_line['duration'])))
    infos.append(out_line['word'])

    file.write(' '.join(infos) + '\n')
file.close()

