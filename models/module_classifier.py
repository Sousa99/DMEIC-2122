import abc
import pandas as pd

from typing import Generator

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame):
        pass

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DecisionTree(Classifier):

    def __init__(self):
        pass

    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame):
        tree_classifier = DecisionTreeClassifier()
        tree_classifier.fit(train_X, train_Y)

        prd_Y = tree_classifier.predict(test_X)
        return prd_Y

class SupportVectorMachine(Classifier):

    def __init__(self):
        pass

    def make_prediction(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame):
        svm_classifier = SVC(C=1, kernel='linear')
        svm_classifier.fit(train_X, train_Y)

        prd_Y = svm_classifier.predict(test_X)
        return prd_Y

# =================================== PUBLIC METHODS ===================================

def leave_one_out(data: pd.DataFrame) -> Generator[tuple, None, None]:

    leave_one_out = LeaveOneOut()
    splits = leave_one_out.split(data)
    return splits
