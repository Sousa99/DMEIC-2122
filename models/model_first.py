import argparse
import warnings

import pandas as pd

# Local Modules
import module_load
import module_sound_features
import module_speech_features
import module_classifier
import module_scorer

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

CODE_CONTROL = { 'code': 'Control', 'target': False, 'file_system': 'c' }
CODE_PSYCHOSIS = { 'code': 'Psychosis', 'target': True, 'file_system': 'p' }

PREFERENCE_AUDIO_TRACKS = ['Tr1', 'Tr2', 'Tr3', 'Tr4', 'LR']
PREFERENCE_TRANS = ['Fix', 'Tr1', 'Tr2', 'Tr3', 'Tr4', 'LR']
EXTENSION_TRANS = '.ctm'

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
control_info['Target'] = CODE_CONTROL['target']
control_info = control_info[['Type', 'Target'] + control_info_columns]
control_paths = control_load['paths']
# Psychosis Info
psychosis_info = psychosis_load['info']
psychosis_info_columns = list(psychosis_info.columns.values)
psychosis_info['Type'] = CODE_PSYCHOSIS['code']
psychosis_info['Target'] = CODE_PSYCHOSIS['target']
psychosis_info = psychosis_info[['Type', 'Target'] + psychosis_info_columns]
psychosis_paths = psychosis_load['paths']

# Concat Information
subject_info = pd.concat([control_info, psychosis_info])
subject_paths = pd.concat([control_paths, psychosis_paths])

# Get Features
#sound_features_df = module_sound_features.sound_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS)
speech_features_df = module_speech_features.speech_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS, PREFERENCE_TRANS, EXTENSION_TRANS)
# All Features
#all_features = pd.merge(sound_features_df, speech_features_df, left_index=True, right_index=True, how='outer')

# ===================================== DROP FEATURES =====================================
speech_drop_columns = ['Subject', 'Task', 'Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path']

# ===================================== ONLY SPEECH FEATURES =====================================
speech_features_X = speech_features_df.drop(speech_drop_columns, axis=1)
speech_features_Y = speech_features_df['Subject'].apply(lambda subject: subject_info.loc[subject]['Target'])

speech_splits = module_classifier.leave_one_out(speech_features_X)
scorer = module_scorer.Scorer()
for train_index, test_index in speech_splits:
    X_train, X_test = speech_features_X.iloc[train_index], speech_features_X.iloc[test_index]
    y_train, y_test = speech_features_Y.iloc[train_index], speech_features_Y.iloc[test_index]

    classifier = module_classifier.DecisionTree()
    y_prd = classifier.make_prediction(X_train, y_train, X_test)
    scorer.add_points(y_test, y_prd)

print(scorer.export_results())
    
