import argparse
import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",            help="prefix of saved files")
parser.add_argument("-controls_data",   help="controls data path")
parser.add_argument("-psychosis_data",  help="psychosis data path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_data, 'key': 'controls_data', 'help': 'path to controls\' data'},
    { 'arg': args.psychosis_data, 'key': 'psychosis_data', 'help': 'path to psychosis\' data'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

# =================================== MAIN EXECUTION ===================================

AGES_CATEGORIES = ['18 - 29', '30 - 39', '40 - 49', '50 - 59', '60 - 69', '70 - 79', '>= 80']
SCHOOLINGS_CATEGORIES = ['4th', '6th', '9th', '12th', 'University']
DIAGNOSIS_CATEGORIES = ['Schizophrenic']

# ======================================================================================

# Retrieve Control Data
worksheet_name = args.controls_data.split('/')[-1].replace('.xlsx', '')
dataframe_control = pd.read_excel(args.controls_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
dataframe_control["Type"] = 'Control'
# Retrieve Psychosis Data
worksheet_name = args.psychosis_data.split('/')[-1].replace('.xlsx', '')
dataframe_psychosis = pd.read_excel(args.psychosis_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
dataframe_psychosis["Type"] = 'Psychosis'

# Merge information into dataframe
full_dataframe = pd.concat([dataframe_control, dataframe_psychosis])
sns.set_theme(palette="deep")

plt.clf()
sns.set(font_scale = 1)
g = sns.catplot(x="Gender", col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - gender distribution.png')

plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Age", order=AGES_CATEGORIES, col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.set_xticklabels([str(i) for i in AGES_CATEGORIES], fontsize = 11)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - age distribution.png')

plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Schooling", order=SCHOOLINGS_CATEGORIES , col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - schooling distribution.png')

plt.clf()
sns.set(font_scale = 1)
g = sns.displot(x="Years Since Diagnosis", bins=15, kde=True, data=dataframe_psychosis)
plt.savefig(args.save + ' - years since diagnosis distribution.png')