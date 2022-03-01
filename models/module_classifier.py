import abc
import itertools

import pandas as pd

from typing import Any, Dict, Generator, List, Optional, Tuple, Type

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut

# Local Modules
import module_scorer
import module_exporter

# =================================== CONSTANTS - VARIATIONS ===================================

VARIATIONS_DT_CRITERION =           [ 'gini', 'entropy' ]
VARIATIONS_DT_MAX_DEPTH =           [ None ] + [ pow(2, value) for value in range(0, 7) ]
VARIATIONS_DT_MAX_FEATURES =        [ None, 'auto', 'sqrt', 'log2' ]
VARIATIONS_MIN_IMPURITY_DECREASE =  [ 0 ] + [ 0.1 * pow(2, value) for value in range(0, 4) ]

VARIATIONS_SVM_C =      [ 0.1 * pow(2, value) for value in range(1, 4) ] + [ pow(2, value) for value in range(0, 7) ]
VARIATIONS_SVM_KERNEL = [ 'linear', 'poly', 'rbf', 'sigmoid' ]

VARIATIONS_DT_PRESET =  { }
VARIATIONS_SVM_PRESET = { }

# =================================== PRIVATE METHODS ===================================

def develop_parameters_variations(keys: List[str], values: List[List[Any]]) -> Dict[str, Dict[str, Any]]:

    variations : Dict[str, Dict[str, Any]] = {}
    permutations_values : List[Tuple[Any, ...]] = list(itertools.product(*values))
    for permutation in permutations_values:

        # Define variables to keep track
        variation_keys = []
        variation = {}
        # Iterate over various params
        for (param_key, param_value) in zip(keys, permutation):
            variation_keys.append("{0} = {1}".format(param_key, str(param_value)))
            variation[param_key] = param_value
        # Store back into global variations
        variation_key = ", ".join(variation_keys)
        variations[variation_key] = variation

    return variations



# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    @abc.abstractmethod
    def scorers(self) -> Dict[str, module_scorer.Scorer]: raise("🚨 Property 'scorers' not defined")
    @abc.abstractproperty
    @abc.abstractmethod
    def variations(self) -> Dict[str, Dict[str, Any]]: raise("🚨 Property 'variations' not defined")

    @abc.abstractmethod
    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        raise("🚨 Method 'compute_variations' not defined")
    @abc.abstractmethod
    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        raise("🚨 Method 'make_prediction' not defined")

    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        for scorer_key in self.scorers:
            scorer = self.scorers[scorer_key]
            parameters = self.variations[scorer_key]

            y_train_pred, y_test_pred = self.make_prediction(parameters, train_X.copy(deep=True), train_Y.copy(deep=True), test_X.copy(deep=True))
            scorer.add_points(train_Y.copy(deep=True), y_train_pred, test_Y.copy(deep=True), y_test_pred)

    def get_scorers(self) -> Dict[str, module_scorer.Scorer]: return self.scorers
    def get_best_scorer(self, metric: str) -> Optional[Tuple[str, module_scorer.Scorer]]:
        
        current_max : Optional[Tuple[str, module_scorer.Scorer, float]] = None
        for scorer_key in self.scorers:
            scorer = self.scorers[scorer_key]
            scorer_metrics = scorer.export_metrics(module_scorer.ScorerSet.Test)

            scorer_metric = list(filter(lambda score_metric: score_metric['name'] == metric, scorer_metrics))[0]
            if current_max is None or scorer_metric['score'] > current_max[2]:
                current_max = (scorer_key, scorer, scorer_metric['score'])
        return (current_max[0], current_max[1])

    def export_variations_results(self, variation_summary: Dict[str, Any]) -> None:

        summary = []
        for scorer_key in self.scorers:
            scorer = self.scorers[scorer_key]
            # Current Line
            for result_set in [('Train', module_scorer.ScorerSet.Train), ('Test', module_scorer.ScorerSet.Test) ]:
                # Define variation summary
                variation_summary_copy = dict(variation_summary)
                # Define variation summary, by adding its parameters
                for param_key in self.variations[scorer_key]: variation_summary_copy[param_key] = self.variations[scorer_key][param_key]
                # Define variation summary, by adding its set
                variation_summary_copy['Set'] = result_set[0]
                # Define variation summary, by adding its scores
                for score in scorer.export_metrics(result_set[1]): variation_summary_copy[score['name']] = score['score']
                # Add Current Line and Current Set
                summary.append(variation_summary_copy)

        summary_df = pd.DataFrame(summary)
        module_exporter.export_csv(summary_df, 'results (variations)')

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DecisionTree(Classifier):

    scorers = {}
    variations = VARIATIONS_DT_PRESET
    def __init__(self, categories: List[str]):
        self.variations.update(self.compute_variations())
        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'criterion', 'max_depth', 'max_features', 'min_impurity_decrease' ]
        values = [ VARIATIONS_DT_CRITERION, VARIATIONS_DT_MAX_DEPTH, VARIATIONS_DT_MAX_FEATURES, VARIATIONS_MIN_IMPURITY_DECREASE ]
        return develop_parameters_variations(keys, values)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        tree_classifier = DecisionTreeClassifier(**params)
        tree_classifier.fit(train_X, train_Y)

        prd_train_Y = tree_classifier.predict(train_X)
        prd_test_Y = tree_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

class SupportVectorMachine(Classifier):

    scorers = {}
    variations = VARIATIONS_SVM_PRESET
    def __init__(self, categories: List[str]):
        self.variations.update(self.compute_variations())
        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'C', 'kernel' ]
        values = [ VARIATIONS_SVM_C, VARIATIONS_SVM_KERNEL ]
        return develop_parameters_variations(keys, values)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        svm_classifier = SVC(**params)
        svm_classifier.fit(train_X, train_Y)

        prd_train_Y = svm_classifier.predict(train_X)
        prd_test_Y = svm_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

# =================================== PUBLIC METHODS ===================================

def convert_key_to_classifier(key: str) -> Optional[Tuple[str, Type[Classifier]]]:

    if key == 'Decision Tree': return ('DT', DecisionTree)
    elif key == 'Support Vector Machine': return ('SVM', SupportVectorMachine)
    else: return None

def leave_one_out(data: pd.DataFrame) -> Generator[tuple, None, None]:

    leave_one_out = LeaveOneOut()
    splits = leave_one_out.split(data)
    return splits
