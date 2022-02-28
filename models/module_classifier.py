import abc
import pandas as pd

from typing import Any, Dict, Generator, List, Optional, Tuple, Type

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut

# Local Modules
import module_scorer

# =================================== CONSTANTS - VARIATIONS ===================================

VARIATIONS_DT = { 'default': {} }
VARIATIONS_SVM = {
    'regularization = 1, kernel = linear': { 'C': 1, 'kernel': 'linear' },
    'regularization = 2, kernel = linear': { 'C': 2, 'kernel': 'linear' },
}

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    @abc.abstractmethod
    def scorers(self) -> Dict[str, module_scorer.Scorer]:
        pass
    @abc.abstractproperty
    @abc.abstractmethod
    def variations(self) -> Dict[str, Dict[str, Any]]:
        pass
    @abc.abstractmethod
    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        pass

    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        for scorer_key in self.scorers:
            scorer = self.scorers[scorer_key]
            parameters = self.variations[scorer_key]

            y_train_pred, y_test_pred = self.make_prediction(parameters, train_X, train_Y, test_X)
            scorer.add_points(train_Y, y_train_pred, test_Y, y_test_pred)

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

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DecisionTree(Classifier):

    scorers = {}
    variations = VARIATIONS_DT
    def __init__(self, categories: List[str]):
        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        tree_classifier = DecisionTreeClassifier(**params)
        tree_classifier.fit(train_X, train_Y)

        prd_train_Y = tree_classifier.predict(train_X)
        prd_test_Y = tree_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

class SupportVectorMachine(Classifier):

    scorers = {}
    variations = VARIATIONS_SVM
    def __init__(self, categories: List[str]):
        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

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
