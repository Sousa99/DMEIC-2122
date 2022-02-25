import pandas as pd

from typing import Any, Dict, List, Optional

# Local Modules
import module_classifier
import module_preprocessing

# =================================== PRIVATE METHODS ===================================

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Variation():

    def __init__(self, variation_info: Dict[str, str], datasets_infos: Dict[str, Dict[str, Any]]) -> None:
        self.load_features(variation_info['features'], datasets_infos)
        self.load_tasks(variation_info['tasks'])
        self.load_classifier(variation_info['classifier'])
        self.load_preprocessing(variation_info['preprocessing'])

    def load_features(self, key_features: str, dataset_infos: Dict[str, Dict[str, Any]]) -> None:

        if key_features not in dataset_infos: exit("🚨 Code for dataset '{0}' not recognized from '{1}'".format(key_features, list(dataset_infos.keys()))) 

        temp_dataset_info = dataset_infos[key_features]
        self.features_code : List[str] = key_features
        self.features : pd.Dataframe = temp_dataset_info['features'].copy(deep=True)
        self.drop_columns : List[str] = temp_dataset_info['drop_columns']
        self.feature_columns : List[str] = temp_dataset_info['feature_columns']

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

    def load_classifier(self, key_classifier: str) -> None:
        temp_classifier = module_classifier.convert_key_to_classifier(key_classifier)

        self.classifier_code = key_classifier
        self.classifier_code_small = temp_classifier[0]
        self.classifier = temp_classifier[1]

    def load_preprocessing(self, keys_preprocessing: str) -> None:

        self.preprocesser = module_preprocessing.Preprocesser(keys_preprocessing)

    def generate_code(self) -> str:
        return ' - '.join([self.classifier_code_small, self.features_code, self.tasks_code])

class VariationGenerator():

    def __init__(self, variations_key: Optional[str], variation_tasks: List[str], variation_features: List[str],
        variation_classifiers: List[str], variation_preprocessing: List[List[str]]) -> None:

        self.key = variations_key 

        self.task_keys = variation_tasks
        self.feature_keys = variation_features
        self.classifier_keys = variation_classifiers
        self.preprocessing_pipeline_keys = variation_preprocessing

    def generate_variations(self, dataset_infos: Dict[str, Dict[str, Any]]) -> List[Variation]:

        if not self.key: return self.generate_default_variations(dataset_infos)
        # Add specific key for Generation of Variations
        # ...
        else: exit("🚨 Variation key '{0}' not recognized".format(self.key)) 
    
    def generate_default_variations(self, dataset_infos: Dict[str, Dict[str, Any]]) -> List[Variation]:

        variations : List[Variation] = []
        for classifier_key in self.classifier_keys:
            for feature_key in self.feature_keys:
                for task_key in self.task_keys:
                    for preprocessing_key in self.preprocessing_pipeline_keys:

                        variation_info = { 'tasks': task_key, 'features': feature_key,
                            'classifier': classifier_key, 'preprocessing': preprocessing_key }
                        variations.append(Variation(variation_info, dataset_infos))

        return variations


# =================================== PUBLIC METHODS ===================================