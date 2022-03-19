import argparse
import warnings

from tqdm import tqdm
from typing import Any, Dict, List, Tuple

import pandas as pd

# Local Modules
import module_load
import module_scorer
import module_exporter
import module_profiling
import module_classifier
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

GENERAL_DROP_COLUMNS = ['Subject', 'Task']

# =================================== PUBLIC FUNCTIONS ===================================

def get_arguments() -> argparse.Namespace: return args

def get_preference_audio_tracks() -> List[str]: return PREFERENCE_AUDIO_TRACKS
def get_preference_transcriptions() -> List[str]: return PREFERENCE_TRANS
def get_transcription_extension() -> str: return EXTENSION_TRANS
def get_general_drop_columns() -> List[str]: return GENERAL_DROP_COLUMNS

def get_subjects_loads() -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Load Datasets and Paths
    control_load = module_load.load_dataset(CODE_CONTROL['file_system'],
        args.info_controls, args.audio_controls, args.trans_controls, TASKS)
    psychosis_load = module_load.load_dataset(CODE_PSYCHOSIS['file_system'],
        args.info_psychosis, args.audio_psychosis, args.trans_psychosis, TASKS)

    return (control_load, psychosis_load)

def get_subjects_info() -> pd.DataFrame:
    # Get Loads
    control_load, psychosis_load = get_subjects_loads()

    # Control Info
    control_info = control_load['info']
    control_info_columns = list(control_info.columns.values)
    control_info['Type'] = CODE_CONTROL['code']
    control_info['Target'] = CODE_CONTROL['target']
    control_info = control_info[['Type', 'Target'] + control_info_columns]
    # Psychosis Info
    psychosis_info = psychosis_load['info']
    psychosis_info_columns = list(psychosis_info.columns.values)
    psychosis_info['Type'] = CODE_PSYCHOSIS['code']
    psychosis_info['Target'] = CODE_PSYCHOSIS['target']
    psychosis_info = psychosis_info[['Type', 'Target'] + psychosis_info_columns]

    subject_info = pd.concat([control_info, psychosis_info])
    return subject_info

def get_subjects_paths() -> pd.DataFrame:
    # Get Loads
    control_load, psychosis_load = get_subjects_loads()

    # Control Info
    control_paths = control_load['paths'].sample(frac=DATASET_SAMPLE)
    # Psychosis Info
    psychosis_paths = psychosis_load['paths'].sample(frac=DATASET_SAMPLE)

    subject_paths = pd.concat([control_paths, psychosis_paths])
    return subject_paths

def study_feature_sets(features_info: Dict[str, Dict[str, Any]], subject_info: pd.DataFrame):
    print()
    print("🚀 Running datasets profiling ...")
    for dataset_key in features_info:

        print("🚀 Running profiling of '{0}' dataset".format(dataset_key))
        module_exporter.change_current_directory(['Data Profiling', dataset_key])
        feature_info = features_info[dataset_key]

        feature_set : pd.DataFrame = feature_info['features'].drop(feature_info['drop_columns'] + GENERAL_DROP_COLUMNS, axis=1)
        target_set : pd.Series = feature_info['features'].reset_index()['Subject'].apply(lambda subject: subject_info.loc[subject]['Target'])
        profiler = module_profiling.DatasetProfiling(feature_set, target_set)
        profiler.make_profiling()

def generate_variations(features_info: Dict[str, Dict[str, Any]]) -> List[module_variations.Variation]:
    variation_features = list(features_info.keys())
    variation_generator = module_variations.VariationGenerator(args.variations_key,
        VARIATION_TASKS, VARIATION_GENDERS, variation_features, VARIATION_CLASSIFIERS, VARIATION_PREPROCESSING)

    variations_to_test = variation_generator.generate_variations(features_info)
    return variations_to_test

def run_variation(variation: module_variations.Variation, subject_info: pd.DataFrame, variations_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    print("🚀 Running variation '{0}'".format(variation.generate_code()))
    dataframe_X, dataframe_Y = variation.get_treated_dataset(GENERAL_DROP_COLUMNS, subject_info, PIVOT_ON_TASKS)

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