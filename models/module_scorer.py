import numpy as np
import pandas as pd

from enum import Enum
from typing import Dict, List, Tuple

# Local Modules
import module_exporter

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

# Assuming False as Negative Class and True as Positive Class
class ScorerSet(Enum):
    Train = 0,
    Test = 1,

class Scorer():

    def __init__(self, categories: List[str]):
        self.categories = categories
        # Scores - Train
        self.train_true_positives   = 0.0
        self.train_true_negatives   = 0.0
        self.train_false_positives  = 0.0
        self.train_false_negatives  = 0.0
        # Scores - Test
        self.test_true_positives    = 0.0
        self.test_true_negatives    = 0.0
        self.test_false_positives   = 0.0
        self.test_false_negatives   = 0.0

    def add_points(self, train_Y: pd.Series, train_pred_Y: pd.Series, test_Y: pd.Series, test_pred_Y: pd.Series):
        
        number_of_train_samples = len(train_Y)
        for (train_y_elem, pred_Y_elem) in zip(train_Y, train_pred_Y):
            
            if train_y_elem and pred_Y_elem: self.train_true_positives += 1 / number_of_train_samples
            elif not train_y_elem and pred_Y_elem: self.train_false_positives += 1 / number_of_train_samples
            elif train_y_elem and not pred_Y_elem: self.train_false_negatives += 1 / number_of_train_samples
            elif not train_y_elem and not pred_Y_elem: self.train_true_negatives += 1 / number_of_train_samples

        number_of_test_samples = len(test_Y)
        for (test_y_elem, pred_Y_elem) in zip(test_Y, test_pred_Y):
            
            if test_y_elem and pred_Y_elem: self.test_true_positives += 1 / number_of_test_samples
            elif not test_y_elem and pred_Y_elem: self.test_false_positives += 1 / number_of_test_samples
            elif test_y_elem and not pred_Y_elem: self.test_false_negatives += 1 / number_of_test_samples
            elif not test_y_elem and not pred_Y_elem: self.test_true_negatives += 1 / number_of_test_samples

    def get_points_from_set(self, scorer_set: ScorerSet) -> Dict[str, float]:

        if scorer_set == ScorerSet.Train: return { 'true_positives': self.train_true_positives, 'true_negatives': self.train_true_negatives,
            'false_positives': self.train_false_positives, 'false_negatives': self.train_false_negatives }
        if scorer_set == ScorerSet.Test: return { 'true_positives': self.test_true_positives, 'true_negatives': self.test_true_negatives,
            'false_positives': self.test_false_positives, 'false_negatives': self.test_false_negatives }

    def number_points(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        return sum(list(points.values()))

    # ============================================= METRICS RETRIEVAL =============================================
    def calculate_accuracy(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        return (points['true_positives'] + points['true_negatives']) / self.number_points(scorer_set)

    def calculate_precision(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        if points['true_positives'] == 0 and points['false_positives'] == 0: return 0
        return points['true_positives'] / (points['true_positives'] + points['false_positives'])

    def calculate_recall(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        if points['true_positives'] == 0 and points['false_negatives'] == 0: return 0
        return points['true_positives'] / (points['true_positives'] + points['false_negatives'])

    def calculate_sensitivity(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        if points['true_positives'] == 0 and points['false_negatives'] == 0: return 0
        return points['true_positives'] / (points['true_positives'] + points['false_negatives'])

    def calculate_specificity(self, scorer_set: ScorerSet) -> float:
        points = self.get_points_from_set(scorer_set)
        if points['false_positives'] == 0 and points['true_negatives'] == 0: return 0
        return points['true_negatives'] / (points['false_positives'] + points['true_negatives'])

    def calculate_f1_measure(self, scorer_set: ScorerSet) -> float:
        precision = self.calculate_precision(scorer_set)
        recall = self.calculate_recall(scorer_set)
        if precision == 0 and recall == 0: return 0
        return (2 * precision * recall) / (precision + recall)

    def calculate_unweighted_average_recall(self, scorer_set: ScorerSet) -> float:
        return (self.calculate_sensitivity(scorer_set) + self.calculate_specificity(scorer_set)) * 0.5
    # ============================================= METRICS RETRIEVAL =============================================

    def compute_confusion_matrix(self, scorer_set: ScorerSet) -> np.ndarray:
        
        points = self.get_points_from_set(scorer_set)
        confusion_matrix = [[points['true_positives'], points['false_negatives']],
            [points['false_positives'], points['true_negatives']]]

        return np.array(confusion_matrix)

    def export_metrics(self, scorer_set: ScorerSet) -> List[module_exporter.ExportMetric]:
        metrics = [
            { 'name': 'Accuracy', 'score': self.calculate_accuracy(scorer_set) },
            { 'name': 'Precision', 'score': self.calculate_precision(scorer_set) },
            { 'name': 'Recall', 'score': self.calculate_recall(scorer_set) },
            { 'name': 'Sensitivity', 'score': self.calculate_sensitivity(scorer_set) },
            { 'name': 'Specificity', 'score': self.calculate_specificity(scorer_set) },
            { 'name': 'F1-Measure', 'score': self.calculate_f1_measure(scorer_set) },
            { 'name': 'UAR', 'score': self.calculate_unweighted_average_recall(scorer_set) },
        ]

        return metrics

    def export_results(self, filename: str = 'temp'):

        confusion_matrix = self.compute_confusion_matrix(ScorerSet.Train)
        metrics = self.export_metrics(ScorerSet.Train)
        module_exporter.export_confusion_matrix(confusion_matrix, self.categories, filename + ' - confusion matrix (train)')
        module_exporter.export_metrics_bar_graph(metrics, filename + ' - scores (train)')

        confusion_matrix = self.compute_confusion_matrix(ScorerSet.Test)
        metrics = self.export_metrics(ScorerSet.Test)
        module_exporter.export_confusion_matrix(confusion_matrix, self.categories, filename + ' - confusion matrix (test)')
        module_exporter.export_metrics_bar_graph(metrics, filename + ' - scores (test)')
        

# =================================== PUBLIC METHODS ===================================
