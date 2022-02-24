import argparse
import warnings

import numpy as np
import pandas as pd

from tqdm import tqdm
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
import module_profiling

# =================================== PACKAGES PARAMETERS ===================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=True)
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', category = UserWarning, module = 'opensmile')

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

# =================================== DEBUG CONSTANTS ===================================

DATASET_SAMPLE = 1.0
PIVOT_ON_TASKS = False
RUN_VARIATIONS = True

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
control_paths = control_load['paths'].sample(frac=DATASET_SAMPLE)
# Psychosis Info
psychosis_info = psychosis_load['info']
psychosis_info_columns = list(psychosis_info.columns.values)
psychosis_info['Type'] = CODE_PSYCHOSIS['code']
psychosis_info['Target'] = CODE_PSYCHOSIS['target']
psychosis_info = psychosis_info[['Type', 'Target'] + psychosis_info_columns]
psychosis_paths = psychosis_load['paths'].sample(frac=DATASET_SAMPLE)

# Concat Information
subject_info = pd.concat([control_info, psychosis_info])
subject_paths = pd.concat([control_paths, psychosis_paths])

# Get Features
sound_features_df = module_sound_features.sound_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS)
speech_features_df = module_speech_features.speech_analysis(subject_paths, PREFERENCE_AUDIO_TRACKS, PREFERENCE_TRANS, EXTENSION_TRANS)
# All Features
all_features_df = pd.merge(sound_features_df, speech_features_df, left_index=True, right_index=True, how='outer', suffixes=('', '_duplicate'))
all_features_df = all_features_df.drop(all_features_df.filter(regex='_duplicate$').columns.tolist(), axis=1)

# ===================================== DROP FEATURES =====================================
general_drop_columns = ['Subject', 'Task']
sound_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path']
speech_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

# ============================================ FEATURE SETS ============================================
sound_features = [column for column in sound_features_df.columns.values if column not in sound_drop_columns + general_drop_columns]
speech_features = [column for column in speech_features_df.columns.values if column not in speech_drop_columns + general_drop_columns]
all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + general_drop_columns]

sound_features_info = { 'features': sound_features_df, 'drop_columns': sound_drop_columns, 'feature_columns': sound_features }
speech_features_info = { 'features': speech_features_df, 'drop_columns': speech_drop_columns, 'feature_columns': speech_features }
all_features_info = { 'features': all_features_df, 'drop_columns': all_features_drop_columns, 'feature_columns': all_features }

features_info = { 'Sound': sound_features_info, 'Speech': speech_features_info, 'Sound + Speech': all_features_info }

# ============================================ STUDY FEATURE SETS ============================================
print()
print("🚀 Running datasets profiling ...")
for dataset_key in features_info:

    print("🚀 Running profiling of '{0}' dataset".format(dataset_key))
    module_exporter.change_current_directory(['Data Profiling', dataset_key])
    feature_info = features_info[dataset_key]
    profiler = module_profiling.DatasetProfiling(feature_info['features'], feature_info['drop_columns'],
        feature_info['feature_columns'], general_drop_columns)
    profiler.make_profiling()

# ================================================= VARIATIONS TO STUDY =================================================
variations_results = []
variations_to_test = [
    # ============================================= SVM - SOUND FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Sound',            'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    # ============================================= SVM - SPEECH FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Speech',           'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    # ============================================= SVM - SOUND + SPEECH FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Sound + Speech',   'classifier': 'Support Vector Machine',  'preprocessing': [ 'DROP_ROWS_NAN' ]},
    # ============================================= DT - SOUND FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Sound',            'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    # ============================================= DT - SPEECH FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Speech',           'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    # ============================================= DT - SOUND + SPEECH FEATURES =============================================
    { 'tasks': 'Task 1',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 2',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 3',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 4',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 5',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 6',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Task 7',                        'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Verbal Fluency',                'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Reading + Retelling',           'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
    { 'tasks': 'Description Affective Images',  'features': 'Sound + Speech',   'classifier': 'Decision Tree',   'preprocessing': [ 'DROP_ROWS_NAN' ]},
]

# ================================================= STUDY VARIATIONS =================================================
if not RUN_VARIATIONS: variations_to_test = []
print()
print("🚀 Running solution variations ...")
for variation_info in variations_to_test:

    variation = module_load.Variation(variation_info, features_info)
    print("🚀 Running variation on '{0}'".format(variation.generate_code()))

    dataframe = variation.features
    dataframe_drop_columns = variation.drop_columns
    dataframe_features = variation.feature_columns

    # Filter dataframe by task
    dataframe = dataframe[dataframe['Task'].isin(variation.tasks)]

    # Do profiling of current dataset
    module_exporter.change_current_directory([variation.generate_code(), 'Data Profiling'])
    print("🚀 Running profiling on '{0}'".format(variation.generate_code()))
    profiler = module_profiling.DatasetProfiling(dataframe, variation.drop_columns, variation.feature_columns, general_drop_columns)
    profiler.make_profiling()

    # Drop unwanted columns and pivot on tasks
    print("🚀 Running model on '{0}'".format(variation.generate_code()))
    module_exporter.change_current_directory([variation.generate_code(), 'Classifier'])
    dataframe = dataframe.drop(dataframe_drop_columns, axis=1)
    if PIVOT_ON_TASKS: dataframe = module_aux.pivot_on_column(dataframe, ['Subject'], 'Task', dataframe_features, 'on')

    # Separate features and target class
    if PIVOT_ON_TASKS: dataframe_X = dataframe
    else: dataframe_X = dataframe.drop(general_drop_columns, axis=1)
    dataframe_Y = dataframe.reset_index()['Subject'].apply(lambda subject: subject_info.loc[subject]['Target'])
    dataframe_Y.index = dataframe.index

    # Preprocessing
    dataframe_X = variation.preprocesser.preprocess(dataframe_X)

    data_splits = list(module_classifier.leave_one_out(dataframe_X))
    scorer = module_scorer.Scorer(['Psychosis', 'Control'])
    with alive_bar(len(data_splits), title="👉 Running classifier in \'" + variation.generate_code() + "\'") as bar:
        for (train_index, test_index) in data_splits:
            X_train, X_test = dataframe_X.iloc[train_index], dataframe_X.iloc[test_index]
            y_train, y_test = dataframe_Y.iloc[train_index], dataframe_Y.iloc[test_index]

            classifier = variation.classifier()
            y_prd = classifier.make_prediction(X_train, y_train, X_test)
            scorer.add_points(y_test, y_prd)

            # Update Progress Bar
            bar()

    scorer.export_results('results')

    # Update General Scores
    variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 'Features': variation.features_code, 'Tasks': variation.tasks_code }
    for score in scorer.export_metrics(): variation_summary[score['name']] = score['score']
    variations_results.append(variation_summary)

module_exporter.change_current_directory()
# Summary of All Variations
variations_results_df = pd.DataFrame(variations_results)
module_exporter.export_csv(variations_results_df, 'results', False)