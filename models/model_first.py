import argparse
import warnings

import numpy as np
import pandas as pd

from tqdm import tqdm

# Local Modules
import module_load
import module_sound_features
import module_speech_features
import module_classifier
import module_scorer
import module_exporter
import module_profiling
import module_variations

# =================================== PACKAGES PARAMETERS ===================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=True)
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', category = UserWarning, module = 'opensmile')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
# Required Arguments
parser.add_argument("-info_controls",   help="path to info file from controls")
parser.add_argument("-info_psychosis",  help="path to info file from psychosis")
parser.add_argument("-audio_controls",  help="path to audio segments from controls")
parser.add_argument("-audio_psychosis", help="path to audio segments from psychosis")
parser.add_argument("-trans_controls",  help="path to transcription files from controls")
parser.add_argument("-trans_psychosis", help="path to transcription files from psychosis")
# Optional Arguments
parser.add_argument("-variations_key",  help="key for the generation of variations, by default all are created")
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

VARIATION_TASKS = [ 'Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6', 'Task 7',
    'Verbal Fluency', 'Reading + Retelling', 'Description Affective Images' ]
VARIATION_GENDERS = [ 'Male Gender', 'Female Gender', 'All Genders' ]
VARIATION_CLASSIFIERS = [ 'Naive Bayes', 'Decision Tree', 'Support Vector Machine', 'Random Forest', 'Multi-Layer Perceptron' ]
VARIATION_PREPROCESSING = [ [ 'DROP_ROWS_NAN' ] ]

TARGET_METRIC = 'F1-Measure'

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

    feature_set = feature_info['features'].drop(feature_info['drop_columns'] + general_drop_columns, axis=1)
    target_set = feature_info['features'].reset_index()['Subject'].apply(lambda subject: subject_info.loc[subject]['Target'])
    profiler = module_profiling.DatasetProfiling(feature_set, target_set)
    profiler.make_profiling()

# ================================================= VARIATIONS TO STUDY =================================================

variation_features = list(features_info.keys())
variation_generator = module_variations.VariationGenerator(args.variations_key,
    VARIATION_TASKS, VARIATION_GENDERS, variation_features, VARIATION_CLASSIFIERS, VARIATION_PREPROCESSING)

variations_to_test = variation_generator.generate_variations(features_info)
variations_results = []

# ================================================= STUDY VARIATIONS =================================================
if not RUN_VARIATIONS: variations_to_test = []
print()
print("🚀 Running solution variations ...")
for variation in variations_to_test:

    print("🚀 Running variation '{0}'".format(variation.generate_code()))
    dataframe_X, dataframe_Y = variation.get_treated_dataset(general_drop_columns, subject_info, PIVOT_ON_TASKS)

    # Do profiling of current dataset
    module_exporter.change_current_directory([variation.generate_code(), 'Data Profiling'])
    print("🚀 Running profiling ...")
    profiler = module_profiling.DatasetProfiling(dataframe_X, dataframe_Y)
    profiler.make_profiling()

    # Running the classifier itself
    module_exporter.change_current_directory([variation.generate_code(), 'Classifier'])
    print("🚀 Running model ...")
    data_splits = list(module_classifier.leave_one_out(dataframe_X))
    classifier = variation.classifier(['Psychosis', 'Control'])
    for (train_index, test_index) in tqdm(data_splits, desc="👉 Running classifier:", leave=False):
        X_train, X_test = dataframe_X.iloc[train_index], dataframe_X.iloc[test_index]
        y_train, y_test = dataframe_Y.iloc[train_index], dataframe_Y.iloc[test_index]

        classifier.process_iteration(X_train, y_train, X_test, y_test)
    # Export Classifier Variations Results
    variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 
        'Features': variation.features_code, 'Tasks': variation.tasks_code, 'Genders': variation.genders_code }
    classifier.export_variations_results(variation_summary, TARGET_METRIC)
    # Export Best Classifier Variation Results
    _, best_scorer = classifier.get_best_scorer(TARGET_METRIC)
    best_scorer.export_results('results')

    print("✅ Completed variation")

    # Update General Scores
    best_scorer_key, best_scorer = classifier.get_best_scorer(TARGET_METRIC)
    variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 'Classifier Variation': best_scorer_key,
        'Features': variation.features_code, 'Tasks': variation.tasks_code, 'Genders': variation.genders_code }
    for score in best_scorer.export_metrics(module_scorer.ScorerSet.Test): variation_summary[score['name']] = score['score']
    variations_results.append(variation_summary)

module_exporter.change_current_directory()
# Summary of All Variations
variations_results_df = pd.DataFrame(variations_results)
module_exporter.export_csv(variations_results_df, 'results', False)