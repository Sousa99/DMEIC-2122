import numpy as np

# Local Modules
import module_exporter

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

# Assuming False as Negative Class and True as Positive Class
class Scorer():

    def __init__(self, categories):
        self.categories = categories
        # Scores
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0

    def add_points(self, test_Y, pred_Y):
        
        for (test_y_elem, pred_Y_elem) in zip(test_Y, pred_Y):
            
            if test_y_elem and pred_Y_elem: self.true_positives += 1
            elif not test_y_elem and pred_Y_elem: self.false_positives += 1
            elif test_y_elem and not pred_Y_elem: self.false_negatives += 1
            elif not test_y_elem and not pred_Y_elem: self.true_negatives += 1

    def number_points(self):

        number_points = 0
        number_points = number_points + self.true_positives
        number_points = number_points + self.false_positives
        number_points = number_points + self.false_negatives
        number_points = number_points + self.true_negatives
        return number_points

    # ============================================= METRICS RETRIEVAL =============================================
    def calculate_accuracy(self): return (self.true_positives + self.true_negatives) / self.number_points()
    def calculate_precision(self): return self.true_positives / (self.true_positives + self.false_positives)
    def calculate_recall(self): return self.true_positives / (self.true_positives + self.false_negatives)
    def calculate_sensitivity(self): return self.true_positives / (self.true_positives + self.false_negatives)
    def calculate_specificity(self): return self.true_negatives / (self.false_positives + self.true_negatives)
    def calculate_f1_measure(self):
        precision = self.calculate_precision()
        recall = self.calculate_recall()
        return (2 * precision * recall) / (precision + recall)
    def calculate_unweighted_average_recall(self): return self.calculate_sensitivity() * 0.5 + self.calculate_specificity()
    # ============================================= METRICS RETRIEVAL =============================================

    def compute_confusion_matrix(self):
        confusion_matrix = [[self.true_positives, self.false_negatives],
            [self.false_positives, self.true_negatives]]

        return np.array(confusion_matrix)

    def export_metrics(self):
        metrics = [
            { 'name': 'Accuracy', 'score': self.calculate_accuracy() },
            { 'name': 'F1-Measure', 'score': self.calculate_f1_measure() },
            { 'name': 'Unweighted Average Recall', 'score': self.calculate_unweighted_average_recall() },
        ]

        return metrics

    def export_results(self, filename = 'temp.png'):

        confusion_matrix = self.compute_confusion_matrix()
        metrics = self.export_metrics()
        module_exporter.export_confusion_matrix(confusion_matrix, self.categories, filename)
        

# =================================== PUBLIC METHODS ===================================
