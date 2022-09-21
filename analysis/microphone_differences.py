import os
import argparse
import warnings

import numpy                as np
import pandas               as pd
import seaborn              as sns
import matplotlib.pyplot    as plt

from tqdm                   import tqdm
from typing                 import List
from nltk.metrics.distance  import edit_distance

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",                help="prefix of saved files")
parser.add_argument("-controls_trans",      help="controls transcriptions path")
parser.add_argument("-psychosis_trans",     help="psychosis transcriptions path")
parser.add_argument("-bipolars_trans",      help="bipolars transcriptions path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_trans, 'key': 'controls_trans', 'help': 'path to controls\' transcriptions'},
    { 'arg': args.psychosis_trans, 'key': 'psychosis_trans', 'help': 'path to psychosis\' transcriptions'},
    { 'arg': args.bipolars_trans, 'key': 'bipolars_trans', 'help': 'path to bipolars\' transcriptions'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def get_task_info(folder: str):
    SEPARATOR = '_'
    folder_split = folder.split(SEPARATOR)

    info = {
        'folder':       folder,
        'tag':          folder_split[0],
        'id':           folder_split[1],
        'full_id':      folder_split[0] + SEPARATOR + folder_split[1],
        'task':         folder_split[2]
    }

    return info

def get_file_info(file: str):
    SEPARATOR = '_'
    filename, file_extension = os.path.splitext(file)
    filename_split = filename.split(SEPARATOR)

    info = {
        'file':         file,
        'extension':    file_extension,
        'tag':          filename_split[0],
        'id':           filename_split[1],
        'full_id':      filename_split[0] + SEPARATOR + filename_split[1],
        'task':         filename_split[2],
        'microphone':   filename_split[3] if len(filename_split) >= 4 else 'Unknown' ,
    }

    return info

def parse_ctm_file(file_path: str):

    def convert_time_milliseconds(time: str) -> int:
        time_split : List[str] = time.split('.')

        minutes = int(time_split[0])
        seconds = int(time_split[1])
        milliseconds = int(time_split[2])

        return ((minutes * 60) + seconds) * 1000 + milliseconds

    def convert_line_to_info(line: str):
        line_splitted = line.split()
        return {
            'word':             line_splitted[4],
            'start_timestamp':  convert_time_milliseconds(line_splitted[2]),
            'duration':         convert_time_milliseconds(line_splitted[3]),
        }
    
    # Read transcription lines
    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()

    # Convert each line to its info
    lines_converted = map(lambda line: convert_line_to_info(line), lines)
    return list(lines_converted)

def distance_to_similarity(distance: float, max_distance: float):
    return 1 - (distance / max_distance)

def convert_microphone_nomenclature(microphone: str):

    if microphone == 'Tr1': return 'Tr'
    if microphone == 'Tr2': return 'Tr'
    if microphone == 'Tr3': return 'Tr'
    if microphone == 'Tr4': return 'Tr'
    return microphone

# =================================== MAIN EXECUTION ===================================

FOCUS_EXTENSION = '.ctm'
FOCUS_EXTENSION_PARSING_FUNCTION = parse_ctm_file

# ======================================================================================

similarities = []

for type, transcription_path in zip(['Controls', 'Psychosis', 'Bipolars'], [args.controls_trans, args.psychosis_trans, args.bipolars_trans]): 

    subjects_dirs = os.listdir(transcription_path)
    number_of_subjects = len(subjects_dirs)
    for index_value, subject in tqdm(list(enumerate(subjects_dirs)), desc="🚀 Processing subjects", leave=True):
        subject_path = os.path.join(transcription_path, subject)

        for task in os.listdir(subject_path):
            task_info = get_task_info(task)
            task_path = os.path.join(subject_path, task_info['folder'])
                
            # Retrieve transcription relevant information
            various_transcriptions = {}
            for file in os.listdir(task_path):
                file_info = get_file_info(file)
                file_full_path = os.path.join(task_path, file_info['file'])

                # Focused only on transcription files by word
                if file_info['extension'] != FOCUS_EXTENSION: continue

                transcription_info = FOCUS_EXTENSION_PARSING_FUNCTION(file_full_path)
                transcribed_words = list(map(lambda info: info['word'], transcription_info))
                various_transcriptions[file_info['microphone']] = transcribed_words

            # Compute Similarities
            entry = {'subject_id': task_info['full_id'], 'task': task_info['task']}
            transcription_keys = list(various_transcriptions.keys())
            transcription_keys.sort()
            for first in range(len(transcription_keys)):
                first_key = transcription_keys[first]
                first_key_converted = convert_microphone_nomenclature(first_key)

                for second in range(first + 1, len(transcription_keys)):
                    second_key = transcription_keys[second]
                    second_key_converted = convert_microphone_nomenclature(second_key)

                    first_transcription = various_transcriptions[first_key] 
                    second_transcription = various_transcriptions[second_key] 
                    distance = edit_distance(first_transcription, second_transcription)
                    similarity = distance_to_similarity(distance, max(len(first_transcription), len(second_transcription)))

                    entry[first_key_converted + ' / ' + second_key_converted] = similarity

            similarities.append(entry)
        
# Create Dataframe with obtained similarities
dataframe_similarities = pd.DataFrame(similarities)
dataframe_similarities.set_index(keys=['subject_id', 'task'], inplace=True)

print()

print("Exporting 'microphone distances' plots ...")
sns.set_theme(palette="deep")

plt.clf()
sns.boxplot(data=dataframe_similarities)
sns.swarmplot(data=dataframe_similarities, color=".25")
plt.savefig(args.save + ' - distances by microphone.pdf')