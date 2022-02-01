import abc
import pandas as pd
from sklearn import tree

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def make_prediction(self, train_X, train_Y, test_X):
        pass

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DecisionTree(Classifier):

    def __init__(self):
        pass

    def make_prediction(self, train_X, train_Y, test_X):
        tree_classifier = DecisionTreeClassifier()
        tree_classifier.fit(train_X, train_Y)

        prd_Y = tree_classifier.predict(test_X)
        return prd_Y

# =================================== PUBLIC METHODS ===================================

def leave_one_out(data):

    leave_one_out = LeaveOneOut()
    splits = leave_one_out.split(data)
    return splits
