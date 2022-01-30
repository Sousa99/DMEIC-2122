import argparse
import warnings

import pandas as pd

# Local Modules
import module_load
import module_sound_features

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-info_controls",   help="path to info file from controls")
parser.add_argument("-info_psychosis",   help="path to info file from psychosis")
parser.add_argument("-audio_controls",   help="path to audio segments from controls")
parser.add_argument("-audio_psychosis",   help="path to audio segments from psychosis")
parser.add_argument("-trans_controls",   help="path to transcription files from controls")
parser.add_argument("-trans_psychosis",   help="path to transcription files from psychosis")
args = parser.parse_args()

requirements = [
    { 'arg': args.info_controls, 'key': 'info_controls', 'help': 'path to info file from controls'},
    { 'arg': args.info_psychosis, 'key': 'info_psychosis', 'help': 'path to info file from psychosis'},
    { 'arg': args.audio_controls, 'key': 'audio_controls', 'help': 'path to audio segments from controls'},
    { 'arg': args.audio_psychosis, 'key': 'audio_psychosis', 'help': 'path to audio segments from psychosis'},
    { 'arg': args.trans_controls, 'key': 'trans_controls', 'help': 'path to transcriptions files from controls'},
    { 'arg': args.trans_psychosis, 'key': 'trans_psychosis', 'help': 'path to transcriptions files from psychosis'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== EXECUTION CONSTANTS ===================================

TASKS = [ {'code': 1, 'name': 'Task 1'},  {'code': 2, 'name': 'Task 2'},  {'code': 3, 'name': 'Task 3'}, 
    {'code': 4, 'name': 'Task 4'}, {'code': 5, 'name': 'Task 5'}, {'code': 6, 'name': 'Task 6'}, {'code': 7, 'name': 'Task 7'}]

CODE_CONTROL = { 'code': 'Control', 'file_system': 'c' }
CODE_PSYCHOSIS = { 'code': 'Psychosis', 'file_system': 'p' }

PREFERENCE_AUDIO_TRACKS = ['Tr1', 'Tr2', 'Tr3', 'Tr4', 'LR']

# =================================== MAIN EXECUTION ===================================

# Load Datasets and Paths
control_load = module_load.load_dataset(CODE_CONTROL['file_system'],
    args.info_controls, args.audio_controls, args.trans_controls, TASKS)
psychosis_load = module_load.load_dataset(CODE_PSYCHOSIS['file_system'],
    args.info_psychosis, args.audio_psychosis, args.trans_psychosis, TASKS)

# Control Info
control_info = control_load['info']
control_info_columns = list(control_info.columns.values)
control_info['Type'] = CODE_CONTROL['code']
control_info = control_info[['Type'] + control_info_columns]
control_paths = control_load['paths']
# Psychosis Info
psychosis_info = psychosis_load['info']
psychosis_info_columns = list(psychosis_info.columns.values)
psychosis_info['Type'] = CODE_PSYCHOSIS['code']
psychosis_info = psychosis_info[['Type'] + psychosis_info_columns]
psychosis_paths = psychosis_load['paths']

# Concat Information
subject_info = pd.concat([control_info, psychosis_info])
subject_paths = pd.concat([control_paths, psychosis_paths])

# Get Features
sound_features_df = module_sound_features.sound_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS)

print(sound_features_df)