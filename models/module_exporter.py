import os
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime

EXPORT_DIRECTORY = '../results/'
EXECUTION_TIMESTAMP = datetime.now()

# =================================== PRIVATE FUNCTIONS ===================================

def calculate_file_prefix():

    timestampStr = EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S")
    return timestampStr + ' - '

# =================================== PUBLIC FUNCTIONS ===================================

def export_confusion_matrix(confusion_matrix, categories, filename = 'temp.png'):

    complete_path = os.path.join(EXPORT_DIRECTORY, calculate_file_prefix() + filename)
    y_label = 'True Label'
    x_label = 'Predicted Label'

    plt.figure()
    sns.heatmap(confusion_matrix, annot=True, cmap='Blues', xticklabels=categories, yticklabels=categories)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(complete_path)