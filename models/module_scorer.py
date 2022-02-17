import numpy as np
import pandas as pd

from typing import List

# Local Modules
import module_exporter

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

# Assuming False as Negative Class and True as Positive Class
class Scorer():

    def __init__(self, categories: List[str]):
        self.categories = categories
        # Scores
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0

    def add_points(self, test_Y: pd.Series, pred_Y: pd.Series):
        
        for (test_y_elem, pred_Y_elem) in zip(test_Y, pred_Y):
            
            if test_y_elem and pred_Y_elem: self.true_positives += 1
            elif not test_y_elem and pred_Y_elem: self.false_positives += 1
            elif test_y_elem and not pred_Y_elem: self.false_negatives += 1
            elif not test_y_elem and not pred_Y_elem: self.true_negatives += 1

    def number_points(self) -> int:

        number_points = 0
        number_points = number_points + self.true_positives
        number_points = number_points + self.false_positives
        number_points = number_points + self.false_negatives
        number_points = number_points + self.true_negatives
        return number_points

    # ============================================= METRICS RETRIEVAL =============================================
    def calculate_accuracy(self) -> float: return (self.true_positives + self.true_negatives) / self.number_points()
    def calculate_precision(self) -> float:
        if self.true_positives == 0 and self.false_positives == 0: return 0
        return self.true_positives / (self.true_positives + self.false_positives)
    def calculate_recall(self) -> float:
        if self.true_positives == 0 and self.false_negatives == 0: return 0
        return self.true_positives / (self.true_positives + self.false_negatives)
    def calculate_sensitivity(self) -> float:
        if self.true_positives == 0 and self.false_negatives == 0: return 0
        return self.true_positives / (self.true_positives + self.false_negatives)
    def calculate_specificity(self) -> float:
        if self.false_positives == 0 and self.true_negatives == 0: return 0
        return self.true_negatives / (self.false_positives + self.true_negatives)
    def calculate_f1_measure(self) -> float:
        precision = self.calculate_precision()
        recall = self.calculate_recall()
        if precision == 0 and recall == 0: return 0
        return (2 * precision * recall) / (precision + recall)
    def calculate_unweighted_average_recall(self) -> float: return (self.calculate_sensitivity() + self.calculate_specificity()) * 0.5
    # ============================================= METRICS RETRIEVAL =============================================

    def compute_confusion_matrix(self) -> np.ndarray:
        confusion_matrix = [[self.true_positives, self.false_negatives],
            [self.false_positives, self.true_negatives]]

        return np.array(confusion_matrix)

    def export_metrics(self) -> List[module_exporter.ExportMetric]:
        metrics = [
            { 'name': 'Accuracy', 'score': self.calculate_accuracy() },
            { 'name': 'Precision', 'score': self.calculate_precision() },
            { 'name': 'Recall', 'score': self.calculate_recall() },
            { 'name': 'Sensitivity', 'score': self.calculate_sensitivity() },
            { 'name': 'Specificity', 'score': self.calculate_specificity() },
            { 'name': 'F1-Measure', 'score': self.calculate_f1_measure() },
            { 'name': 'UAR', 'score': self.calculate_unweighted_average_recall() },
        ]

        return metrics

    def export_results(self, filename: str = 'temp'):

        confusion_matrix = self.compute_confusion_matrix()
        metrics = self.export_metrics()
        module_exporter.export_confusion_matrix(confusion_matrix, self.categories, filename + ' - confusion matrix')
        module_exporter.export_metrics_bar_graph(metrics, filename + ' - scores')
        

# =================================== PUBLIC METHODS ===================================
