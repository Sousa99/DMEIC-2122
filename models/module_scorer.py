
# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

# Assuming False as Negative Class and True as Positive Class
class Scorer():

    def __init__(self):
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

    def export_results(self):
        
        return { 'accuracy': (self.true_positives + self.true_negatives) / self.number_points() }

# =================================== PUBLIC METHODS ===================================
