import abc
import pandas as pd

from typing import Generator, List, Optional, Tuple, Type

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut

# Local Modules
import module_scorer

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    @abc.abstractmethod
    def scorer(self) -> module_scorer.Scorer:
        pass

    @abc.abstractmethod
    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        pass
    @abc.abstractmethod
    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        pass

    def get_scorer(self):
        return self.scorer

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DecisionTree(Classifier):

    scorer = None
    def __init__(self, categories: List[str]):
        self.scorer = module_scorer.Scorer(categories)

    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        y_train_pred, y_test_pred = self.make_prediction(train_X, train_Y, test_X)
        self.scorer.add_points(train_Y, y_train_pred, test_Y, y_test_pred)

    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        tree_classifier = DecisionTreeClassifier()
        tree_classifier.fit(train_X, train_Y)

        prd_train_Y = tree_classifier.predict(train_X)
        prd_test_Y = tree_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

class SupportVectorMachine(Classifier):

    scorer = None
    def __init__(self, categories: List[str]):
        self.scorer = module_scorer.Scorer(categories)

    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        y_train_pred, y_test_pred = self.make_prediction(train_X, train_Y, test_X)
        self.scorer.add_points(train_Y, y_train_pred, test_Y, y_test_pred)

    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        svm_classifier = SVC(C=1, kernel='linear')
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
