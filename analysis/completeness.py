import argparse
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import cm

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",        help="prefix of saved files")
parser.add_argument("-data",        help="data file")
parser.add_argument("-psychosis",   help="file is of psychosis patients", action='store_true')
args = parser.parse_args()

if ( not args.data or not args.save ):
    print("🙏 Please provide a 'save' and 'data' file")
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2., height + 0.04,
            '%d' % int(height),
            ha='center', va='bottom')

def grouped_bar_plot(data, grouped_collumn, categories_collumn, categories, file_name):

    barWidth = 0.08
    plt.figure(figsize=(10, 5), dpi=80)

    labels = list(map(lambda x: x.title(), categories['labels']))

    bars = []
    rs = []
    rects = []

    groups = data[grouped_collumn].unique()
    for category in categories['values']:

        bar_temp = []
        for group in groups:
            sub_data = data[data[grouped_collumn] == group]

            if (categories['type'] == 'equals'):
                bar_temp.append(sub_data[sub_data[categories_collumn] == category].shape[0])
            elif (categories['type'] == 'interval'):
                minimum = category['min']
                maximum = category['max']
                bar_temp.append(sub_data[(sub_data[categories_collumn] >= minimum) & (sub_data[categories_collumn] < maximum)].shape[0])

        if len(rs) == 0: r_temp = np.arange(len(bar_temp))
        else: r_temp = [x + barWidth for x in rs[-1]]

        bars.append(bar_temp)
        rs.append(r_temp)

    color_map = cm.get_cmap("rainbow")
    for i in range(len(categories['labels'])):
        color = color_map( 0.75 * (i / len(categories['labels'])) + 0.125)
        rect = plt.bar(rs[i], bars[i], color = color, width=barWidth, edgecolor='white', label = labels[i])
        rects.append(rect)
    
    title = 'Distribution of ' + categories_collumn.title() + ' by ' + grouped_collumn.title()
    plt.title(title, fontsize = 15, pad = 20, fontweight='bold')

    plt.xlabel('Datasets', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(bars[0]))], groups)

    plt.ylabel('Number of Samples', fontweight='bold')
    
    plt.legend()

    for rect in rects: autolabel(rect)
    plt.savefig(file_name)


# =================================== MAIN EXECUTION ===================================

AGES_CATEGORIES = {
    'type': 'equals',
    'labels': ['18 - 29', '30 - 39', '40 - 49', '50 - 59', '60 - 69', '70 - 79', '>= 80'],
    'values': ['18 - 29', '30 - 39', '40 - 49', '50 - 59', '60 - 69', '70 - 79', '>= 80']
}

SCHOOLINGS_CATEGORIES = {
    'type': 'equals',
    'labels': ['4th', '6th', '9th', '12th', 'University'],
    'values': ['4th', '6th', '9th', '12th', 'University']
}

DIAGNOSIS_CATEGORIES = {
    'type': 'equals',
    'labels': ['Schizophrenic'],
    'values': ['Schizophrenic']
}

BPRS_CATEGORIES = {
    'type': 'interval',
    'labels': ['18 - 35', '36 - 53', '54 - 71', '72 - 89', '90 - 107', '108 - 125', '126'],
    'values': [
        { 'min': 18,    'max': 36   },
        { 'min': 36,    'max': 54   },
        { 'min': 54,    'max': 72   },
        { 'min': 72,    'max': 90   },
        { 'min': 90,    'max': 108  },
        { 'min': 108,   'max': 126  },
        { 'min': 126,   'max': 999  }
    ]
}

YEARS_SINCE_DIAGNOSIS_CATEGORIES = {
    'type': 'interval',
    'labels': ['< 5 years', '>= 5 years'],
    'values': [
        { 'min': 0,     'max': 5    },
        { 'min': 5,     'max': 999  },
    ]
}

# ======================================================================================

worksheet_name = args.data.split('/')[-1].replace('.xlsx', '')
dataframe = pd.read_excel(args.data, sheet_name = worksheet_name, index_col = 0)

grouped_bar_plot(dataframe, 'Gender', 'Age', AGES_CATEGORIES, args.save + ' - age by gender.png')
grouped_bar_plot(dataframe, 'Gender', 'Schooling', SCHOOLINGS_CATEGORIES, args.save + ' - schooling by gender.png')

if args.psychosis:
    grouped_bar_plot(dataframe, 'Gender', 'Diagnosis', DIAGNOSIS_CATEGORIES, args.save + ' - diagnosis by gender.png')
    grouped_bar_plot(dataframe, 'Gender', 'BPRS', BPRS_CATEGORIES, args.save + ' - BPRS since diagnosis by gender.png')
    grouped_bar_plot(dataframe, 'Gender', 'Years Since Diagnosis', YEARS_SINCE_DIAGNOSIS_CATEGORIES, args.save + ' - years since diagnosis by gender.png')
