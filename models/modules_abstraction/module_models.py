import os
import abc
import pickle
import argparse
import warnings

from tqdm import tqdm
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Local Modules
import modules_abstraction.module_scorer        as module_scorer
import modules_abstraction.module_profiling     as module_profiling
import modules_abstraction.module_classifier    as module_classifier
import modules_abstraction.module_variations    as module_variations
import modules_abstraction.module_featureset    as module_featureset
# Local Modules - Auxiliary
import modules_aux.module_load      as module_load
import modules_aux.module_exporter  as module_exporter

# =================================== PACKAGES PARAMETERS ===================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', category = UserWarning, module = 'opensmile')

# =================================== DEBUG CONSTANTS ===================================

DATASET_SAMPLE              :   float               = 1.00
PIVOT_ON_TASKS              :   bool                = False
VARIATIONS_FILTER_BY_INDEX  :   Optional[List[int]] = None

# =================================== CONSTANTS ===================================

PICKLE_EXTENSION = '.pkl'

PARALLEL_TMP_DIRECTORY          = './tmp/'
PARALLEL_FEATURE_SETS_FILE      = 'tmp_feature_set' + PICKLE_EXTENSION
PARALLEL_NUMBER_VARIATIONS_FILE = 'tmp_number_variations.txt'

PARALLEL_FEATURE_EXTRACTION = 'FEATURE_EXTRACTION'
PARALLEL_RUN_MODELS         = 'RUN_MODELS'
PARALLEL_RUN_FINAL          = 'RUN_FINAL'

# =================================== PRIVATE CLASSES ===================================

class ModelAbstraction(metaclass=abc.ABCMeta):

    # =================================== EXECUTION CONSTANTS ===================================

    TASKS = [ {'code': 1, 'name': 'Task 1'},  {'code': 2, 'name': 'Task 2'},  {'code': 3, 'name': 'Task 3'}, 
        {'code': 4, 'name': 'Task 4'}, {'code': 5, 'name': 'Task 5'}, {'code': 6, 'name': 'Task 6'}, {'code': 7, 'name': 'Task 7'}]

    CODE_CONTROL = { 'code': 'Control', 'target': False, 'file_system': 'c' }
    CODE_PSYCHOSIS = { 'code': 'Psychosis', 'target': True, 'file_system': 'p' }
    CODE_BIPOLAR = { 'code': 'Bipolar', 'target': False, 'file_system': 'b' }

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

    # =================================== PROPERTIES ===================================

    arguments : argparse.Namespace
    feature_sets : List[module_featureset.FeatureSetAbstraction] = []
    
    subjects_loads : Tuple[pd.DataFrame, pd.DataFrame]
    subjects_infos : pd.DataFrame
    subjects_paths : pd.DataFrame
    variations_to_test : List[module_variations.Variation] = []
    
    variations_results : List[Dict[str, Any]] = []

    # =================================== FUNCTIONS ===================================

    def load_subjects(self):
        # Load Datasets and Paths
        control_load = module_load.load_dataset(self.CODE_CONTROL['file_system'],
            self.arguments.info_controls, self.arguments.audio_controls, self.arguments.trans_controls, self.TASKS)
        psychosis_load = module_load.load_dataset(self.CODE_PSYCHOSIS['file_system'],
            self.arguments.info_psychosis, self.arguments.audio_psychosis, self.arguments.trans_psychosis, self.TASKS)
        bipolar_load = module_load.load_dataset(self.CODE_BIPOLAR['file_system'],
            self.arguments.info_bipolars, self.arguments.audio_bipolars, self.arguments.trans_bipolars, self.TASKS)
        # Store Load
        self.subjects_loads = (control_load, psychosis_load, bipolar_load)

    def load_subjects_info(self):
        # Get Loads
        control_load, psychosis_load, bipolar_load = self.subjects_loads
        # Control Info
        control_info = control_load['info']
        control_info_columns = list(control_info.columns.values)
        control_info['Type'] = self.CODE_CONTROL['code']
        control_info['Target'] = self.CODE_CONTROL['target']
        control_info = control_info[['Type', 'Target'] + control_info_columns]
        # Psychosis Info
        psychosis_info = psychosis_load['info']
        psychosis_info_columns = list(psychosis_info.columns.values)
        psychosis_info['Type'] = self.CODE_PSYCHOSIS['code']
        psychosis_info['Target'] = self.CODE_PSYCHOSIS['target']
        psychosis_info = psychosis_info[['Type', 'Target'] + psychosis_info_columns]
        # Bipolar Info
        bipolar_info = bipolar_load['info']
        bipolar_info_columns = list(bipolar_info.columns.values)
        bipolar_info['Type'] = self.CODE_BIPOLAR['code']
        bipolar_info['Target'] = self.CODE_BIPOLAR['target']
        bipolar_info = bipolar_info[['Type', 'Target'] + bipolar_info_columns]
        # Store Info
        self.subjects_infos = pd.concat([control_info, psychosis_info, bipolar_info])

    def load_subjects_paths(self) -> pd.DataFrame:
        # Get Loads
        control_load, psychosis_load, bipolar_load = self.subjects_loads
        # Control Info
        control_paths = control_load['paths'].sample(frac=DATASET_SAMPLE)
        # Psychosis Info
        psychosis_paths = psychosis_load['paths'].sample(frac=DATASET_SAMPLE)
        # Bipolar Info
        bipolar_paths = bipolar_load['paths'].sample(frac=DATASET_SAMPLE)
        # Store Paths
        self.subjects_paths = pd.concat([control_paths, psychosis_paths, bipolar_paths])

    def load_feature_sets(self, feature_sets: Optional[List[module_featureset.FeatureSetAbstraction]] = None):
        self.feature_sets = feature_sets
        self.generate_variations()

    def generate_variations(self):
        variation_features = list(map(lambda feature_set: feature_set.id, self.feature_sets))
        variation_generator = module_variations.VariationGenerator(self.arguments.variations_key,
            self.VARIATION_TASKS, self.VARIATION_GENDERS, variation_features, self.VARIATION_CLASSIFIERS, self.VARIATION_PREPROCESSING)

        self.variations_to_test = variation_generator.generate_variations()
        if VARIATIONS_FILTER_BY_INDEX is not None:
            self.variations_to_test = [ self.variations_to_test[index] for index in VARIATIONS_FILTER_BY_INDEX ]

    @abc.abstractmethod
    def __init__(self, arguments: argparse.Namespace) -> None:
        # Arguments and Logic        
        self.arguments = arguments
        timestamp_argument = arguments.timestamp;
        if timestamp_argument is not None: module_exporter.change_execution_timestamp(timestamp_argument)

        # Load Informations
        self.load_subjects()
        self.load_subjects_info()
        self.load_subjects_paths()

    def study_feature_sets(self):

        print()
        print("🚀 Running datasets profiling ...")

        for feature_set in self.feature_sets:

            feature_key : str = feature_set.id
            print("🚀 Running profiling of '{0}' dataset".format(feature_key))

            module_exporter.change_current_directory(['Feature Extraction'])
            feature_df, target_df = feature_set.get_full_df()

            module_exporter.change_current_directory(['Data Profiling', feature_key])
            profiler = module_profiling.DatasetProfiling(feature_df, target_df)
            profiler.make_profiling()

    def run_variation(self, variation: module_variations.Variation) -> Tuple[str, module_scorer.Scorer]:

        print("🚀 Running variation '{0}'".format(variation.generate_code()))
        feature_sets_filter = list(filter(lambda feature_set: feature_set.id == variation.features_code, self.feature_sets))
        if len(feature_sets_filter) == 0: exit(f"🚨 Feature set with key '{variation.features_code}' not found in model feature_sets")
        feature_set : module_featureset.FeatureSetAbstraction = feature_sets_filter[0]

        module_exporter.change_current_directory([variation.generate_code(), 'Feature Extraction'])
        dataframe_X, dataframe_Y = feature_set.get_full_df(variation)

        # Do profiling of current dataset
        module_exporter.change_current_directory([variation.generate_code(), 'Data Profiling'])
        print("🚀 Running profiling ...")
        profiler = module_profiling.DatasetProfiling(dataframe_X, dataframe_Y)
        profiler.make_profiling()

        # Running the classifier itself
        print("🚀 Running model ...")
        data_splits = list(module_classifier.leave_one_out(dataframe_X))
        classifier = variation.classifier(['Psychosis', 'Control'])
        for (split_index, (train_index, test_index)) in enumerate(tqdm(data_splits, desc="👉 Running classifier:", leave=False)):
            module_exporter.change_current_directory([variation.generate_code(), 'Feature Extraction', f'split {split_index}'])
            (X_train, y_train), (X_test, y_test) = feature_set.get_df_for_classification(variation, (train_index, test_index))
            classifier.process_iteration(X_train, y_train, X_test, y_test)

        # Export Classifier Variations Results
        module_exporter.change_current_directory([variation.generate_code(), 'Classifier'])
        variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 
            'Features': variation.features_code, 'Tasks': variation.tasks_code, 'Genders': variation.genders_code }
        classifier.export_variations_results(variation_summary, self.TARGET_METRIC)
        # Export Best Classifier Variation Results
        _, best_scorer = classifier.get_best_scorer(self.TARGET_METRIC)
        best_scorer.export_results('results')

        print("✅ Completed variation")
        return classifier.get_best_scorer(self.TARGET_METRIC)

    def export_final_results(self):

        print()
        print("🚀 Exporting Final Results ...")

        module_exporter.change_current_directory()
        # Summary of All Variations
        variations_results_df = pd.DataFrame(self.variations_results)
        module_exporter.export_csv(variations_results_df, 'results', False)

    @abc.abstractmethod
    def execute(self, feature_sets: Optional[List[module_featureset.FeatureSetAbstraction]] = None):
        exit("🚨 Method 'execute' not defined")

# =================================== PUBLIC CLASSES ===================================

class SequentialModel(ModelAbstraction):

    def __init__(self, arguments: argparse.Namespace) -> None:
        # Run Super Initialization
        super().__init__(arguments)

    def run_variations(self):

        print()
        print("🚀 Running solution variations ...")

        for variation in self.variations_to_test:

            best_scorer_key, best_scorer = self.run_variation(variation)
            # Update General Scores
            variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 'Classifier Variation': best_scorer_key,
                'Features': variation.features_code, 'Tasks': variation.tasks_code, 'Genders': variation.genders_code }
            for score in best_scorer.export_metrics(module_scorer.ScorerSet.Test): variation_summary[score['name']] = score['score']
            self.variations_results.append(variation_summary)

    def execute(self, feature_sets: Optional[List[module_featureset.FeatureSetAbstraction]] = None):
        
        if feature_sets is None:
            exit("🚨 Execute on 'SequentialModel' requires 'feature_sets'")

        self.load_feature_sets(feature_sets)
        self.study_feature_sets()
        self.run_variations()
        self.export_final_results()

class ParallelModel(ModelAbstraction):

    def __init__(self, arguments: argparse.Namespace) -> None:
        # Run Super Initialization
        super().__init__(arguments)

    def load_feature_sets_from_memory(self):

        directory_path = PARALLEL_TMP_DIRECTORY
        if self.arguments.timestamp is not None: directory_path = os.path.join(directory_path, self.arguments.timestamp)
        full_path = os.path.join(directory_path, PARALLEL_FEATURE_SETS_FILE)

        file = open(full_path, 'rb')
        self.load_feature_sets(pickle.load(file))
        file.close()

    def save_feature_sets(self):

        directory_path = PARALLEL_TMP_DIRECTORY
        if self.arguments.timestamp is not None: directory_path = os.path.join(directory_path, self.arguments.timestamp)
        if not os.path.exists(directory_path): os.makedirs(directory_path)
        full_path = os.path.join(directory_path, PARALLEL_FEATURE_SETS_FILE)

        file = open(full_path, 'wb')
        pickle.dump(self.feature_sets, file)
        file.close()

    def save_number_of_variations(self):

        directory_path = PARALLEL_TMP_DIRECTORY
        if self.arguments.timestamp is not None: directory_path = os.path.join(directory_path, self.arguments.timestamp)
        if not os.path.exists(directory_path): os.makedirs(directory_path)
        full_path = os.path.join(directory_path, PARALLEL_NUMBER_VARIATIONS_FILE)

        file = open(full_path, 'w')
        file.write(str(len(self.variations_to_test)))
        file.close()
    
    def run_variation_by_index(self, index: int):

        variation = self.variations_to_test[index]
        best_scorer_key, best_scorer = self.run_variation(variation)

        # Update General Scores
        variation_summary = { 'Key': variation.generate_code(), 'Classifier': variation.classifier_code, 'Classifier Variation': best_scorer_key,
            'Features': variation.features_code, 'Tasks': variation.tasks_code, 'Genders': variation.genders_code }
        for score in best_scorer.export_metrics(module_scorer.ScorerSet.Test): variation_summary[score['name']] = score['score']

        # Save Temporarily Variation Summary
        directory_path = PARALLEL_TMP_DIRECTORY
        if self.arguments.timestamp is not None: directory_path = os.path.join(directory_path, self.arguments.timestamp)
        if not os.path.exists(directory_path): os.makedirs(directory_path)
        full_path = os.path.join(directory_path, variation.generate_code() + PICKLE_EXTENSION)

        file = open(full_path, 'wb')
        pickle.dump(variation_summary, file)
        file.close()

    def load_variations_results(self):

        # Iterate Variation Summaries which should have been created
        directory_path = PARALLEL_TMP_DIRECTORY
        if self.arguments.timestamp is not None: directory_path = os.path.join(directory_path, self.arguments.timestamp)
        for variation in self.variations_to_test:
            full_path = os.path.join(directory_path, variation.generate_code() + PICKLE_EXTENSION)

            if not os.path.exists(full_path):
                exit(f"🚨 File for variation '{variation.generate_code()}' not found in '{directory_path}'")

            file = open(full_path, 'rb')
            variation_summary = pickle.load(file)
            file.close()
            # Save back variation summary
            self.variations_results.append(variation_summary)

    def execute(self, feature_sets: Optional[List[module_featureset.FeatureSetAbstraction]] = None):

        # Get pertinent arguments
        parallelization = self.arguments.parallelization_key
        parallelization_index = self.arguments.parallelization_index

        if parallelization == PARALLEL_FEATURE_EXTRACTION:

            if feature_sets is None:
                exit("🚨 Execute on 'SequentialModel' requires 'feature_sets'")

            self.load_feature_sets(feature_sets)
            self.study_feature_sets()
            self.save_feature_sets()
            self.save_number_of_variations()

        elif parallelization == PARALLEL_RUN_MODELS:
            self.load_feature_sets_from_memory()
            self.run_variation_by_index(int(parallelization_index))

        elif parallelization == PARALLEL_RUN_FINAL:
            self.load_feature_sets_from_memory()
            self.load_variations_results()
            self.export_final_results()