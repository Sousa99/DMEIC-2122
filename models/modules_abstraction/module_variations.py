import copy
import random
import itertools

import pandas as pd

from typing     import Any, Dict, List, Optional, Tuple

# Local Modules
import modules_abstraction.module_classifier    as module_classifier
import modules_abstraction.module_preprocessing as module_preprocessing

# =================================== PRIVATE METHODS ===================================

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Variation():

    def __init__(self, variation_info: Dict[str, str]) -> None:

        self.load_features(variation_info['features'])
        self.load_tasks(variation_info['tasks'])
        self.load_genders(variation_info['genders'])
        self.load_data(variation_info['data'])
        self.load_classifier(variation_info['classifier'], variation_info['classifier_variations'])
        self.load_preprocessing(variation_info['preprocessing'])

        self.repetition : int = variation_info['repetition']
        self.study_features_importance : bool = variation_info['study_features_importance']
        self.study_feature_importance : Optional[str] = None
        self.record_subjects : bool = variation_info['record_subjects']

    def load_features(self, key_features: str) -> None:
        self.features_code : List[str] = key_features

    def load_tasks(self, key_tasks: str) -> None:

        if key_tasks == 'Task 1': temp_tasks = ['Task 1']
        elif key_tasks == 'Task 2': temp_tasks = ['Task 2']
        elif key_tasks == 'Task 3': temp_tasks = ['Task 3']
        elif key_tasks == 'Task 4': temp_tasks = ['Task 4']
        elif key_tasks == 'Task 5': temp_tasks = ['Task 5']
        elif key_tasks == 'Task 6': temp_tasks = ['Task 6']
        elif key_tasks == 'Task 7': temp_tasks = ['Task 7']

        elif key_tasks == 'Verbal Fluency': temp_tasks = ['Task 1', 'Task 2']
        elif key_tasks == 'Reading + Retelling': temp_tasks = ['Task 3', 'Task 4']
        elif key_tasks == 'Description Affective Images': temp_tasks = ['Task 5', 'Task 6', 'Task 7']
        else: exit("🚨 Code for tasks '{0}' not recognized".format(key_tasks))

        self.tasks_code = key_tasks
        self.tasks = temp_tasks

    def load_genders(self, key_genders: str) -> None:

        if key_genders == 'Male Gender': temp_genders = ['Male']
        elif key_genders == 'Female Gender': temp_genders = ['Female']
        elif key_genders == 'All Genders': temp_genders = ['Male', 'Female']
        else: exit("🚨 Code for gender '{0}' not recognized".format(key_genders))

        self.genders_code = key_genders
        self.genders = temp_genders

    def load_data(self, key_data: str) -> None:

        if key_data == 'V1 Simple': temp_datas = ['V1']
        elif key_data == 'V2 Simple': temp_datas = ['V1', 'V2']
        elif key_data == 'V2 Complex': temp_datas = ['V1', 'V2', 'V2 - Complexity']
        else: exit("🚨 Code for data '{0}' not recognized".format(key_data))

        self.data_code = key_data
        self.datas = temp_datas

    def load_classifier(self, key_classifier: str, classifier_variations: Optional[List[str]]) -> None:
        temp_classifier = module_classifier.convert_key_to_classifier(key_classifier)

        self.classifier_code = key_classifier
        self.classifier_code_small = temp_classifier[0]
        self.classifier = temp_classifier[1]

        self.classifier_variations = classifier_variations

    def load_preprocessing(self, keys_preprocessing: str) -> None:

        self.preprocesser = module_preprocessing.Preprocesser(keys_preprocessing)

    def develop_classifier(self, categories: List[str]) -> module_classifier.Classifier:
        initialized_classifier = self.classifier(categories, self.classifier_variations)
        return initialized_classifier

    def generate_code(self) -> str:
        feature_importance_str : str = "No Feature Importance"
        if self.study_features_importance and self.study_feature_importance is None: feature_importance_str : str = f"Feature Importance"
        if self.study_features_importance and self.study_feature_importance is not None:
            feature_standardized : str = self.study_feature_importance.replace("/", "")
            feature_importance_str : str = f"{feature_standardized} Feature Importance"

        return ' - '.join([self.classifier_code_small, self.features_code, self.tasks_code, self.genders_code, self.data_code, f'Repetition {self.repetition:02d}', feature_importance_str])

    def generate_code_dataset(self, replace_feature_code: Optional[str] = None) -> str:
        feature_importance_str : str = "No Feature Importance"
        if self.study_features_importance and self.study_feature_importance is None: feature_importance_str : str = f"Feature Importance"
        if self.study_features_importance and self.study_feature_importance is not None:
            feature_standardized : str = self.study_feature_importance.replace("/", "")
            feature_importance_str : str = f"{feature_standardized} Feature Importance"

        if replace_feature_code is None: return ' - '.join([self.features_code, self.tasks_code, self.genders_code, self.data_code, f'Repetition {self.repetition:02d}'])
        else: return ' - '.join([replace_feature_code, self.tasks_code, self.genders_code, self.data_code, f'Repetition {self.repetition:02d}'])

    def generate_sub_variations(self, features: List[str]) -> List['Variation']:

        sub_variations : List[Variation] = []
        for feature in features:
            sub_variation : Variation = copy.deepcopy(self)
            sub_variation.study_feature_importance = feature

            sub_variations.append(sub_variation)

        return sub_variations

    def random_for_feature_importance(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> pd.DataFrame:

        column_sample : pd.Series = X_train[self.study_feature_importance]
        column_dtype : Any = column_sample.dtype

        if column_dtype == int:
            minimum : int = int(column_sample.min())
            maximum : int = int(column_sample.max())
            X_test[self.study_feature_importance] = X_test[self.study_feature_importance].apply(lambda _: random.randint(minimum, maximum))
        elif column_dtype == float:
            minimum : float = float(column_sample.min())
            maximum : float = float(column_sample.max())
            X_test[self.study_feature_importance] = X_test[self.study_feature_importance].apply(lambda _: random.uniform(minimum, maximum))
        else:
            possible_values : List[Any] = column_sample.unique().tolist()
            X_test[self.study_feature_importance] = X_test[self.study_feature_importance].apply(lambda _: random.choice(possible_values))

        return X_test

class VariationGenerator():

    def __init__(self, variations_key: Optional[str], variations_by_key: Dict[str, Dict[str, List[str]]],
        variation_tasks: List[str], variation_genders: List[str], variation_data: List[str],
        variation_features: List[str], variation_classifiers: List[str], variation_preprocessing: List[List[str]]) -> None:

        self.key = variations_key 
        self.variations_by_key = variations_by_key

        self.task_keys = variation_tasks
        self.genders_keys = variation_genders
        self.data_keys = variation_data
        self.feature_keys = variation_features
        self.classifier_keys = variation_classifiers
        self.preprocessing_pipeline_keys = variation_preprocessing

    def generate_variations(self) -> List[Variation]:

        if not self.key: return self.generate_default_variations()
        elif self.key in self.variations_by_key: return self.generate_variation_by_key(self.variations_by_key[self.key])
        else: exit("🚨 Variation key '{0}' not recognized".format(self.key)) 

    def generate_variation_by_key(self, variation_config: Dict[str, List[str]]) -> List[Variation]:

        if 'classifier' in variation_config: classifier_keys                            : List[str]                         = variation_config['classifier']
        else: classifier_keys                                                           : List[str]                         = self.classifier_keys
        if 'features' in variation_config: feature_keys                                 : List[str]                         = variation_config['features']
        else: feature_keys                                                              : List[str]                         = self.feature_keys
        if 'tasks' in variation_config: task_keys                                       : List[str]                         = variation_config['tasks']
        else: task_keys                                                                 : List[str]                         = self.task_keys
        if 'genders' in variation_config: genders_keys                                  : List[str]                         = variation_config['genders']
        else: genders_keys                                                              : List[str]                         = self.genders_keys
        if 'data' in variation_config: data_keys                                        : List[str]                         = variation_config['data']
        else: data_keys                                                                 : List[str]                         = self.data_keys
        if 'preprocessing' in variation_config: preprocessing_pipeline_keys             : List[str]                         = variation_config['preprocessing']
        else: preprocessing_pipeline_keys                                               : List[str]                         = self.preprocessing_pipeline_keys

        if 'variation_indexes' in variation_config: variation_indexes                   : Optional[Dict[int, List[str]]]    = variation_config['variation_indexes']
        else: variation_indexes                                                         : Optional[Dict[int, List[str]]]    = None
        if 'repetitions' in variation_config: variation_repetitions                     : int                               = variation_config['repetitions']
        else: variation_repetitions                                                     : int                               = 1
        if 'study_features_importance' in variation_config: study_features_importance   : bool                              = variation_config['study_features_importance']
        else: study_features_importance                                                 : bool                              = False
        if 'record_subjects' in variation_config: record_subjects                       : bool                              = variation_config['record_subjects']
        else: record_subjects                                                           : bool                              = False

        variations : List[Variation] = []
        for variation_index, (classifier_key, feature_key, task_key, gender_key, data_key, preprocessing_key) in \
            enumerate(itertools.product(classifier_keys, feature_keys, task_keys, genders_keys, data_keys, preprocessing_pipeline_keys)):

            if variation_indexes is None or variation_index in variation_indexes:

                classifier_variations : Optional[Dict[str, Any]] = None
                if variation_indexes is not None:
                    classifier_variations = variation_indexes[variation_index]
                
                for repetition in range(0, variation_repetitions):
                    variation_info = { 'tasks': task_key, 'genders': gender_key, 'data': data_key, 'features': feature_key,
                        'classifier': classifier_key, 'classifier_variations': classifier_variations, 'preprocessing': preprocessing_key,
                        'repetition': repetition, 'study_features_importance': False, 'record_subjects': record_subjects }
                    variations.append(Variation(variation_info))

                if study_features_importance:
                    variation_info = { 'tasks': task_key, 'genders': gender_key, 'data': data_key, 'features': feature_key,
                        'classifier': classifier_key, 'classifier_variations': classifier_variations, 'preprocessing': preprocessing_key,
                        'repetition': 0, 'study_features_importance': True, 'record_subjects': record_subjects }
                    variations.append(Variation(variation_info))

        return variations

    
    def generate_default_variations(self) -> List[Variation]:

        variations : List[Variation] = []
        for (classifier_key, feature_key, task_key, genders_key, data_key, preprocessing_key) in \
            itertools.product(self.classifier_keys, self.feature_keys, self.task_keys,
                self.genders_keys, self.data_keys, self.preprocessing_pipeline_keys):

            variation_info = { 'tasks': task_key, 'genders': genders_key, 'data': data_key, 'features': feature_key,
                'classifier': classifier_key, 'classifier_variations': None, 'preprocessing': preprocessing_key,
                'repetition': repetition, 'study_features_importance': False }
            variations.append(Variation(variation_info))

        return variations


# =================================== PUBLIC METHODS ===================================