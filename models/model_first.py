import argparse
import warnings

import numpy as np
import pandas as pd

from alive_progress import alive_bar
from sklearn.impute import SimpleImputer

# Local Modules
import module_load
import module_sound_features
import module_speech_features
import module_classifier
import module_scorer
import module_aux
import module_exporter

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
sound_features_df = module_sound_features.sound_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS)
speech_features_df = module_speech_features.speech_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS, PREFERENCE_TRANS, EXTENSION_TRANS)
# All Features
all_features_df = pd.merge(sound_features_df, speech_features_df, left_index=True, right_index=True, how='outer', suffixes=('', '_duplicate'))
all_features_df = all_features_df.drop(all_features_df.filter(regex='_duplicate$').columns.tolist(), axis=1)

# ===================================== CHOOSE TASKS =====================================
ACTIVE_TASKS = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6', 'Task 7']

# ===================================== DROP FEATURES =====================================
general_drop_columns = ['Subject', 'Task']
sound_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path']
speech_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

# ===================================== FEATURES =====================================
sound_features = [column for column in sound_features_df.columns.values if column not in sound_drop_columns + general_drop_columns]
speech_features = [column for column in speech_features_df.columns.values if column not in speech_drop_columns + general_drop_columns]
all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + general_drop_columns]

# ===================================== DATAFRAME TO USE =====================================
dataframe = all_features_df
dataframe_drop_columns = all_features_drop_columns
dataframe_features = all_features

# Drop unwanted columns and pivot on tasks
dataframe = dataframe[dataframe['Task'].isin(ACTIVE_TASKS)]
dataframe = dataframe.drop(dataframe_drop_columns, axis=1)
dataframe_pivot = module_aux.pivot_on_column(dataframe, ['Subject'], 'Task', dataframe_features, 'on')

# Export dataframe to use
module_exporter.export_csv(dataframe_pivot, 'dataset')

# Sepparate features and target class
dataframe_X = dataframe_pivot
dataframe_Y = dataframe_pivot.reset_index()['Subject'].apply(lambda subject: subject_info.loc[subject]['Target'])
dataframe_Y.index = dataframe_pivot.index

# ===== FIXME: MOVE TO ANOTHER MODULE =====
imp = SimpleImputer(strategy='mean', missing_values=np.nan, copy=True)
dataframe_X = pd.DataFrame(imp.fit_transform(dataframe_X), columns=dataframe_X.columns.values)
# ===== FIXME: MOVE TO ANOTHER MODULE =====

speech_splits = list(module_classifier.leave_one_out(dataframe_X))
scorer = module_scorer.Scorer(['Psychosis', 'Control'])
with alive_bar(len(speech_splits)) as bar:
    for (train_index, test_index) in speech_splits:
        X_train, X_test = dataframe_X.iloc[train_index], dataframe_X.iloc[test_index]
        y_train, y_test = dataframe_Y.iloc[train_index], dataframe_Y.iloc[test_index]

        classifier = module_classifier.SupportVectorMachine()
        y_prd = classifier.make_prediction(X_train, y_train, X_test)
        scorer.add_points(y_test, y_prd)

        # Update Progress Bar
        bar()

scorer.export_results('results')