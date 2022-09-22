import abc
import copy
import itertools
import warnings

import numpy as np
import pandas as pd

from typing import Any, Dict, Generator, List, Optional, Tuple, Type

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.exceptions import ConvergenceWarning

# Local Modules
import modules_abstraction.module_scorer    as module_scorer
# Local Modules - Auxiliary
import modules_aux.module_exporter  as module_exporter

# =================================== PACKAGES PARAMETERS ===================================

warnings.filterwarnings('ignore', category = ConvergenceWarning)

# =================================== CONSTANTS - VARIATIONS ===================================

VARIATIONS_NB_ALGORITHM =   [ 'Gaussian', 'Bernoulli' ]

VARIATIONS_DT_CRITERION =               [ 'gini', 'entropy' ]
VARIATIONS_DT_MAX_DEPTH =               [ pow(2, value) for value in range(0, 8) ]
VARIATIONS_DT_MAX_FEATURES =            [ None, 'auto', 'sqrt', 'log2' ]
VARIATIONS_DT_MIN_IMPURITY_DECREASE =   [ 0 ] + [ 0.1 * pow(2, value) for value in range(0, 4) ]

VARIATIONS_SVM_C =      [ pow(2, value) for value in range(-2, 3) ]
VARIATIONS_SVM_KERNEL = [ 'linear', 'poly', 'rbf', 'sigmoid' ]

VARIATIONS_RF_ESTIMATORS =              [ 10, 50, 100, 150 ]
VARIATIONS_RF_CRITERION =               [ 'gini', 'entropy' ]
VARIATIONS_RF_MAX_DEPTH =               [ pow(2, value) for value in range(0, 8) ]
VARIATIONS_RF_MAX_FEATURES =            [ None, 'auto', 'sqrt', 'log2' ]
VARIATIONS_RF_MIN_IMPURITY_DECREASE =   [ 0, 0.25, 0.50 ]

VARIATIONS_MLP_HIDDEN_LAYERS =      [ (50, ), (100, ), (100, 50), (50, 100, 50) ]
VARIATIONS_MLP_ACTIVATION =         [ 'logistic', 'tanh', 'relu' ]
VARIATIONS_MLP_LEARNING_RATE_INIT = [ 0.001 * pow(5, value) for value in range(0, 4) ]
VARIATIONS_MLP_LEARNING_RATE =      [ 'constant', 'invscaling', 'adaptive' ]
VARIATIONS_MLP_MAX_ITERATIONS =     [ 100, 500, 1000 ]

VARIATIONS_NB_PRESET =  { }
VARIATIONS_DT_PRESET =  { }
VARIATIONS_SVM_PRESET = { }
VARIATIONS_RF_PRESET =  { }
VARIATIONS_MLP_PRESET = { }

# =================================== PRIVATE METHODS ===================================

def develop_parameters_variations(keys: List[str], values: List[List[Any]], filter_variations: Optional[List[str]]) -> Dict[str, Dict[str, Any]]:

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

        if filter_variations is None or variation_key in filter_variations:
            variations[variation_key] = variation

    return variations

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Classifier(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    @abc.abstractmethod
    def scorers(self) -> Dict[str, module_scorer.Scorer]: exit("🚨 Property 'scorers' not defined")
    @abc.abstractproperty
    @abc.abstractmethod
    def variations(self) -> Dict[str, Dict[str, Any]]: exit("🚨 Property 'variations' not defined")
    @abc.abstractproperty
    @abc.abstractmethod
    def filter_variations(self) -> List[str]: exit("🚨 Property 'filter_variations' not defined")

    @abc.abstractmethod
    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        exit("🚨 Method 'compute_variations' not defined")
    @abc.abstractmethod
    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        exit("🚨 Method 'make_prediction' not defined")
    @abc.abstractmethod
    def export_variations_results(self, variation_summary: pd.DataFrame, metric: str) -> None:
        exit("🚨 Method 'export_variations_results' not defined")

    def process_iteration(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame, test_Y: pd.Series):
        for scorer_key in self.scorers:
            scorer = self.scorers[scorer_key]
            parameters = self.variations[scorer_key]

            y_train_pred, y_test_pred = self.make_prediction(parameters, train_X.copy(), train_Y.copy(), test_X.copy())
            scorer.add_points(train_Y.copy(), y_train_pred, test_Y.copy(), y_test_pred)

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

    def get_variations_df(self, variation_summary: Dict[str, Any]) -> pd.DataFrame:
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
        return summary_df

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class NaiveBayes(Classifier):

    scorers = {}
    variations = VARIATIONS_NB_PRESET
    filter_variations = None

    def __init__(self, categories: List[str], filter_variations: Optional[List[str]]):
        self.filter_variations = filter_variations
        self.variations.update(self.compute_variations())

        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'algorithm' ]
        values = [ VARIATIONS_NB_ALGORITHM ]
        return develop_parameters_variations(keys, values, self.filter_variations)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        # Remove params not fed to classifier
        params_copy = copy.deepcopy(params)
        algorithm = params_copy.pop('algorithm', None)

        if algorithm == 'Gaussian': nb_classifier = GaussianNB(**params_copy)
        elif algorithm == 'Multinomial': nb_classifier = MultinomialNB(**params_copy)
        elif algorithm == 'Bernoulli': nb_classifier = BernoulliNB(**params_copy)
        else: exit(f"🚨 Naive Bayes algorithm '{algorithm}' not recognized")
        nb_classifier.fit(train_X, train_Y)

        prd_train_Y = nb_classifier.predict(train_X)
        prd_test_Y = nb_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

    def export_variations_results(self, variation_summary: Dict[str, Any], metric: str) -> None:
        summary_df = self.get_variations_df(variation_summary)
        # Standard Output of Variations
        module_exporter.export_csv(summary_df, 'results (variations)')
        # Specific graphs
        module_exporter.bar_chart('algorithms', summary_df, 'Set', metric, hue_key='algorithm', y_lim=(0, 1))

class DecisionTree(Classifier):

    scorers = {}
    variations = VARIATIONS_DT_PRESET
    filter_variations = None

    def __init__(self, categories: List[str], filter_variations: Optional[List[str]]):
        self.filter_variations = filter_variations
        self.variations.update(self.compute_variations())

        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'criterion', 'max_depth', 'max_features', 'min_impurity_decrease' ]
        values = [ VARIATIONS_DT_CRITERION, VARIATIONS_DT_MAX_DEPTH, VARIATIONS_DT_MAX_FEATURES, VARIATIONS_DT_MIN_IMPURITY_DECREASE ]
        return develop_parameters_variations(keys, values, self.filter_variations)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        tree_classifier = DecisionTreeClassifier(**params)
        tree_classifier.fit(train_X, train_Y)

        prd_train_Y = tree_classifier.predict(train_X)
        prd_test_Y = tree_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

    def export_variations_results(self, variation_summary: Dict[str, Any], metric: str) -> None:
        summary_df = self.get_variations_df(variation_summary)
        summary_df = summary_df.fillna("None")
        best_row = summary_df.loc[summary_df[metric].idxmax()]
        # Standard Output of Variations
        module_exporter.export_csv(summary_df, 'results (variations)')
        # Specific graphs
        module_exporter.multiple_lines_chart('complexity - maximum depth', summary_df, 'max_depth', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - minimum impurity decrease', summary_df, 'min_impurity_decrease', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        
        best_criterion =                best_row['criterion']
        best_min_impurity_decrease =    best_row['min_impurity_decrease']
        best_max_depth =                best_row['max_depth']

        tmp_df = summary_df[(summary_df['criterion'] == best_criterion) & (summary_df['min_impurity_decrease'] == best_min_impurity_decrease)]
        module_exporter.multiple_lines_chart(f'complexity - maximum depth (criterion = {best_criterion}, min_impurity_decrease = {best_min_impurity_decrease})',
            tmp_df, 'max_depth', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['criterion'] == best_criterion) & (summary_df['max_depth'] == best_max_depth)]
        module_exporter.multiple_lines_chart(f'complexity - minimum impurity decrease (criterion = {best_criterion}, max_depth = {best_max_depth})',
            tmp_df, 'min_impurity_decrease', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))

class SupportVectorMachine(Classifier):

    scorers = {}
    variations = VARIATIONS_SVM_PRESET
    filter_variations = None

    def __init__(self, categories: List[str], filter_variations: Optional[List[str]]):
        self.filter_variations = filter_variations
        self.variations.update(self.compute_variations())

        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'C', 'kernel' ]
        values = [ VARIATIONS_SVM_C, VARIATIONS_SVM_KERNEL ]
        return develop_parameters_variations(keys, values, self.filter_variations)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        svm_classifier = SVC(**params)
        svm_classifier.fit(train_X, train_Y)

        prd_train_Y = svm_classifier.predict(train_X)
        prd_test_Y = svm_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

    def export_variations_results(self, variation_summary: Dict[str, Any], metric: str) -> None:
        summary_df = self.get_variations_df(variation_summary)
        # Standard Output of Variations
        module_exporter.export_csv(summary_df, 'results (variations)')
        # Specific graphs
        module_exporter.multiple_lines_chart('complexity - regularization', summary_df, 'C', metric, hue_key='kernel', style_key='Set', y_lim=(0, 1))

class RandomForest(Classifier):

    scorers = {}
    variations = VARIATIONS_RF_PRESET
    filter_variations = None

    def __init__(self, categories: List[str], filter_variations: Optional[List[str]]):
        self.filter_variations = filter_variations
        self.variations.update(self.compute_variations())

        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'n_estimators', 'criterion', 'max_depth', 'max_features', 'min_impurity_decrease' ]
        values = [ VARIATIONS_RF_ESTIMATORS, VARIATIONS_RF_CRITERION, VARIATIONS_RF_MAX_DEPTH, VARIATIONS_RF_MAX_FEATURES, VARIATIONS_RF_MIN_IMPURITY_DECREASE ]
        return develop_parameters_variations(keys, values, self.filter_variations)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        forest_classifier = RandomForestClassifier(**params)
        forest_classifier.fit(train_X, train_Y)

        prd_train_Y = forest_classifier.predict(train_X)
        prd_test_Y = forest_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

    def export_variations_results(self, variation_summary: Dict[str, Any], metric: str) -> None:
        summary_df = self.get_variations_df(variation_summary)
        summary_df = summary_df.fillna("None")
        best_row = summary_df.loc[summary_df[metric].idxmax()]
        # Standard Output of Variations
        module_exporter.export_csv(summary_df, 'results (variations)')
        # Specific graphs
        module_exporter.multiple_lines_chart('complexity - number of estimators', summary_df, 'n_estimators', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - maximum depth', summary_df, 'max_depth', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - minimum impurity decrease', summary_df, 'min_impurity_decrease', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        
        best_estimators =               best_row['n_estimators']
        best_criterion =                best_row['criterion']
        best_min_impurity_decrease =    best_row['min_impurity_decrease']
        best_max_depth =                best_row['max_depth']

        tmp_df = summary_df[(summary_df['n_estimators'] == best_estimators) & (summary_df['criterion'] == best_criterion) & (summary_df['min_impurity_decrease'] == best_min_impurity_decrease)]
        module_exporter.multiple_lines_chart(f'complexity - maximum depth (n_estimators = {best_estimators}, criterion = {best_criterion}, min_impurity_decrease = {best_min_impurity_decrease})',
            tmp_df, 'max_depth', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['n_estimators'] == best_estimators) & (summary_df['criterion'] == best_criterion) & (summary_df['max_depth'] == best_max_depth)]
        module_exporter.multiple_lines_chart(f'complexity - minimum impurity decrease (n_estimators = {best_estimators}, criterion = {best_criterion}, max_depth = {best_max_depth})',
            tmp_df, 'min_impurity_decrease', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['criterion'] == best_criterion) & (summary_df['min_impurity_decrease'] == best_min_impurity_decrease) & (summary_df['max_depth'] == best_max_depth)]
        module_exporter.multiple_lines_chart(f'complexity - number of estimators (criterion = {best_criterion}, min_impurity_decrease = {best_min_impurity_decrease}, max_depth = {best_max_depth})',
            tmp_df, 'n_estimators', metric, hue_key='max_features', style_key='Set', y_lim=(0, 1))

class MultiLayerPerceptron(Classifier):

    scorers = {}
    variations = VARIATIONS_RF_PRESET
    filter_variations = None

    def __init__(self, categories: List[str], filter_variations: Optional[List[str]]):
        self.filter_variations = filter_variations
        self.variations.update(self.compute_variations())
        
        for variation_key in self.variations:
            self.scorers[variation_key] = module_scorer.Scorer(categories)

    def compute_variations(self) -> Dict[str, Dict[str, Any]]:
        keys = [ 'hidden_layer_sizes', 'activation', 'learning_rate_init', 'learning_rate', 'max_iter' ]
        values = [ VARIATIONS_MLP_HIDDEN_LAYERS, VARIATIONS_MLP_ACTIVATION, VARIATIONS_MLP_LEARNING_RATE_INIT, VARIATIONS_MLP_LEARNING_RATE, VARIATIONS_MLP_MAX_ITERATIONS ]
        return develop_parameters_variations(keys, values, self.filter_variations)

    def make_prediction(self, params: Dict[str, Dict[str, Any]], train_X: pd.DataFrame, train_Y: pd.Series, test_X: pd.DataFrame) -> Tuple[pd.Series]:
        mlp_classifier = MLPClassifier(**params)
        mlp_classifier.fit(train_X, train_Y)

        prd_train_Y = mlp_classifier.predict(train_X)
        prd_test_Y = mlp_classifier.predict(test_X)
        return (prd_train_Y, prd_test_Y)

    def export_variations_results(self, variation_summary: Dict[str, Any], metric: str) -> None:
        summary_df = self.get_variations_df(variation_summary)
        best_row = summary_df.loc[summary_df[metric].idxmax()]
        # Standard Output of Variations
        module_exporter.export_csv(summary_df, 'results (variations)')
        # Specific graphs
        module_exporter.multiple_lines_chart('complexity - number of maximum iterations per hidden layer', summary_df, 'max_iter', metric, hue_key='hidden_layer_sizes', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - number of maximum iterations per activation', summary_df, 'max_iter', metric, hue_key='activation', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - number of maximum iterations per learning rate type', summary_df, 'max_iter', metric, hue_key='learning_rate_init', style_key='Set', y_lim=(0, 1))
        module_exporter.multiple_lines_chart('complexity - number of maximum iterations per learning rate init', summary_df, 'max_iter', metric, hue_key='learning_rate', style_key='Set', y_lim=(0, 1))

        best_hidden_layer_sizes =   best_row['hidden_layer_sizes']
        best_activation =           best_row['activation']
        best_learning_rate_init =   best_row['learning_rate_init']
        best_learning_rate =        best_row['learning_rate']

        tmp_df = summary_df[(summary_df['activation'] == best_activation) & (summary_df['learning_rate_init'] == best_learning_rate_init) & (summary_df['learning_rate'] == best_learning_rate)]
        module_exporter.multiple_lines_chart(f'complexity - number of maximum iterations per hidden layer (activation = {best_activation}, learning_rate_init = {best_learning_rate_init}, learning_rate = {best_learning_rate})',
            tmp_df, 'max_iter', metric, hue_key='hidden_layer_sizes', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['hidden_layer_sizes'] == best_hidden_layer_sizes) & (summary_df['learning_rate_init'] == best_learning_rate_init) & (summary_df['learning_rate'] == best_learning_rate)]
        module_exporter.multiple_lines_chart(f'complexity - number of maximum iterations per activation (hidden_layer_sizes = {best_hidden_layer_sizes}, learning_rate_init = {best_learning_rate_init}, learning_rate = {best_learning_rate})',
            tmp_df, 'max_iter', metric, hue_key='activation', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['hidden_layer_sizes'] == best_hidden_layer_sizes) & (summary_df['activation'] == best_activation) & (summary_df['learning_rate'] == best_learning_rate)]
        module_exporter.multiple_lines_chart(f'complexity - number of maximum iterations per learning rate type (hidden_layer_sizes = {best_hidden_layer_sizes}, activation = {best_activation}, learning_rate = {best_learning_rate})',
            tmp_df, 'max_iter', metric, hue_key='learning_rate_init', style_key='Set', y_lim=(0, 1))
        tmp_df = summary_df[(summary_df['hidden_layer_sizes'] == best_hidden_layer_sizes) & (summary_df['activation'] == best_activation) & (summary_df['learning_rate_init'] == best_learning_rate_init)]
        module_exporter.multiple_lines_chart(f'complexity - number of maximum iterations per learning rate init (hidden_layer_sizes = {best_hidden_layer_sizes}, activation = {best_activation}, learning_rate_init = {best_learning_rate_init})',
            tmp_df, 'max_iter', metric, hue_key='learning_rate', style_key='Set', y_lim=(0, 1))

# =================================== PUBLIC METHODS ===================================

def convert_key_to_classifier(key: str) -> Optional[Tuple[str, Type[Classifier]]]:

    if key == 'Naive Bayes':                return ('NB', NaiveBayes)
    elif key == 'Decision Tree':            return ('DT', DecisionTree)
    elif key == 'Support Vector Machine':   return ('SVM', SupportVectorMachine)
    elif key == 'Random Forest':            return ('RF', RandomForest)
    elif key == 'Multi-Layer Perceptron':   return ('MLP', MultiLayerPerceptron)
    else: return None

def leave_one_out(data: pd.DataFrame) -> Generator[tuple, None, None]:

    leave_one_out = LeaveOneOut()
    splits = leave_one_out.split(data)
    return splits
