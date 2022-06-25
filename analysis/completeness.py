import argparse
import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from itertools import product

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",            help="prefix of saved files")
parser.add_argument("-controls_data",   help="controls data path")
parser.add_argument("-psychosis_data",  help="psychosis data path")
parser.add_argument("-bipolars_data",   help="bipolars data path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_data, 'key': 'controls_data', 'help': 'path to controls\' data'},
    { 'arg': args.psychosis_data, 'key': 'psychosis_data', 'help': 'path to psychosis\' data'},
    { 'arg': args.bipolars_data, 'key': 'bipolars_data', 'help': 'path to bipolars\' data'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def donut_chart(filename: str, dataframe_count_major: pd.DataFrame, dataframe_count_minor: pd.DataFrame):

    colors = [plt.cm.Blues, plt.cm.Reds, plt.cm.Greens]
    outter_colors = [ color(0.6) for color in colors ]
    inner_colors = [ color(value) for color in colors for value in [0.5, 0.4] ]
    
    outter_groups = []
    for out_index, _ in dataframe_count_minor.index.tolist():
        if out_index not in outter_groups:
            outter_groups.append(out_index)
    outter_values = [ dataframe_count_major.loc[index] for index in outter_groups ]
    inner_groups = [ f'{out_index} - {in_index}' for out_index, in_index in dataframe_count_minor.index.tolist()]
    inner_values = [ dataframe_count_minor.loc[index] for index in dataframe_count_minor.index.tolist() ]

    inner_filter_index = [ idx for idx, value in enumerate(inner_values) if value != 0 ]
    inner_colors = [ color for idx, color in enumerate(inner_colors) if idx in inner_filter_index ]
    inner_groups = [ group for idx, group in enumerate(inner_groups) if idx in inner_filter_index ]
    inner_values = [ value for idx, value in enumerate(inner_values) if idx in inner_filter_index ]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('equal')

    outter_piechart, _ = ax.pie(outter_values, radius=1.3, labels=outter_values, labeldistance=1.1, colors=outter_colors )
    plt.setp(outter_piechart, width=0.3, edgecolor='white')
    inner_piechart, _ = ax.pie(inner_values, radius=1.3 - 0.3, labels=inner_values, labeldistance=0.4, colors=inner_colors)
    plt.setp(inner_piechart, width=0.4, edgecolor='white')
    plt.legend(outter_piechart + inner_piechart, outter_groups + inner_groups, borderaxespad=0, loc='lower right', bbox_to_anchor=(1.12, 0.0))

    plt.savefig(filename)

# =================================== MAIN EXECUTION ===================================

AGES_CATEGORIES = ['18 - 29', '30 - 39', '40 - 49', '50 - 59', '60 - 69', '70 - 79', '>= 80']
SCHOOLINGS_CATEGORIES = ['4th', '6th', '9th', '12th', 'University']
DIAGNOSIS_CATEGORIES = ['Schizophrenic']
LANGUAGE_CATEGORIES = ['European Portuguese', 'Brazilian Portuguese']
MASK_WEARING_CATEGORIES = ['Unknown', 'Yes', 'No']
DATA_CATEGORIES = ['V1', 'V2', 'V2 - Complexity']
DATA_NEW_CATEGORIES = { DATA_CATEGORIES[0]: 'Original', DATA_CATEGORIES[1]: 'Extended', DATA_CATEGORIES[2]: 'Extended' }

# ======================================================================================

# Retrieve Control Healthy Data
worksheet_name = args.controls_data.split('/')[-1].replace('.xlsx', '')
dataframe_control = pd.read_excel(args.controls_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
dataframe_control["Type"] = 'Control'
dataframe_control["Diagnosis"] = 'Healthy'
# Retrieve Psychosis Data
worksheet_name = args.psychosis_data.split('/')[-1].replace('.xlsx', '')
dataframe_psychosis = pd.read_excel(args.psychosis_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
dataframe_psychosis["Type"] = 'Psychosis'
dataframe_psychosis["Diagnosis"] = 'Psychosis'
# Retrieve Bipolar Data
worksheet_name = args.bipolars_data.split('/')[-1].replace('.xlsx', '')
dataframe_bipolar = pd.read_excel(args.bipolars_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
dataframe_bipolar["Type"] = 'Control'
dataframe_bipolar["Diagnosis"] = 'Bipolar'

# Merge information into dataframe
full_dataframe = pd.concat([dataframe_control, dataframe_psychosis, dataframe_bipolar])
full_dataframe = full_dataframe.replace(DATA_NEW_CATEGORIES)
sns.set_theme(palette="deep")

# Achieve Count Dataframes
full_dataframe_index = full_dataframe.reset_index(inplace=False).rename(columns={'index': '# Records'})
dataframe_count_outter = full_dataframe_index.groupby(['Diagnosis'])['# Records'].count()
dataframe_count_inner = full_dataframe_index.groupby(['Diagnosis', 'Data Variation'])['# Records'].count().reset_index()
dataframe_combinations = pd.DataFrame(list(product(full_dataframe['Diagnosis'].unique(), full_dataframe['Data Variation'].unique())), columns=['Diagnosis', 'Data Variation'])
dataframe_count_inner = dataframe_count_inner.merge(dataframe_combinations, how='right').fillna(0.0)
dataframe_count_inner = dataframe_count_inner.set_index(['Diagnosis', 'Data Variation'])['# Records'].astype(int)

# General Count
plt.clf()
sns.set(font_scale = 1)
donut_chart(args.save + ' - corpus size donut.png', dataframe_count_outter, dataframe_count_inner)
plt.clf()
sns.set(font_scale = 1)
g = sns.barplot(x="Diagnosis", y="# Records", hue="Data Variation", data=dataframe_count_inner.reset_index())
g.legend().set_title(None)
for container in g.containers: g.bar_label(container)
plt.savefig(args.save + ' - corpus size bars.png')

# Gender Distribution
plt.clf()
sns.set(font_scale = 1)
g = sns.catplot(x="Gender", col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - gender distribution by type.png')
plt.clf()
sns.set(font_scale = 1)
g = sns.catplot(x="Gender", col="Diagnosis", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - gender distribution by diagnosis.png')

# Age Distribution
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Age", order=AGES_CATEGORIES, col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.set_xticklabels([str(i) for i in AGES_CATEGORIES], fontsize = 11)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - age distribution by type.png')
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Age", order=AGES_CATEGORIES, col="Diagnosis", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.set_xticklabels([str(i) for i in AGES_CATEGORIES], fontsize = 11)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - age distribution by diagnosis.png')

# Schooling Distribution
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Schooling", order=SCHOOLINGS_CATEGORIES , col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - schooling distribution by type.png')
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Schooling", order=SCHOOLINGS_CATEGORIES , col="Diagnosis", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - schooling distribution by diagnosis.png')

# Language Distribution
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Language", order=LANGUAGE_CATEGORIES , col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - language distribution by type.png')
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Language", order=LANGUAGE_CATEGORIES , col="Diagnosis", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - language distribution by diagnosis.png')

# Wearing Mask Distribution
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Wearing Mask", order=MASK_WEARING_CATEGORIES , col="Type", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - mask wearing distribution by type.png')
plt.clf()
sns.set(font_scale = 1.25)
g = sns.catplot(x="Wearing Mask", order=MASK_WEARING_CATEGORIES , col="Diagnosis", kind="count", data=full_dataframe)
for ax in g.axes.ravel(): ax.bar_label(ax.containers[0])
plt.savefig(args.save + ' - mask wearing distribution by diagnosis.png')

# Years Since Diagnosis Distribution
plt.clf()
sns.set(font_scale = 1)
g = sns.displot(x="Years Since Diagnosis", bins=15, kde=True, data=dataframe_psychosis)
plt.savefig(args.save + ' - years since diagnosis distribution.png')