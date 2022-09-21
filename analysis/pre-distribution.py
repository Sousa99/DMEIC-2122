import os
import math
import nltk
import stanza
import argparse
import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm
from typing import List
from pydub import AudioSegment

# ================================================= NLTK DOWNLOADS  =================================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()

stanza.download('pt')
print()
'''

# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', module = 'stanza')

# =================================== FLAGS PARSING ===================================

parser = argparse.ArgumentParser()
parser.add_argument("-save",                help="prefix of saved files")
parser.add_argument("-controls_data",       help="controls data path")
parser.add_argument("-psychosis_data",      help="psychosis data path")
parser.add_argument("-bipolars_data",       help="bipolars data path")
parser.add_argument("-controls_rec",        help="controls recordings path")
parser.add_argument("-psychosis_rec",       help="psychosis recordings path")
parser.add_argument("-bipolars_rec",        help="bipolars recordings path")
parser.add_argument("-controls_trans",      help="controls transcriptions path")
parser.add_argument("-psychosis_trans",     help="psychosis transcriptions path")
parser.add_argument("-bipolars_trans",      help="bipolars transcriptions path")
args = parser.parse_args()

requirements = [
    { 'arg': args.save, 'key': 'save', 'help': 'save file name prefix'},
    { 'arg': args.controls_data, 'key': 'controls_data', 'help': 'path to \'controls\' data'},
    { 'arg': args.psychosis_data, 'key': 'psychosis_data', 'help': 'path to \'psychosis\' data'},
    { 'arg': args.bipolars_data, 'key': 'bipolars_data', 'help': 'path to \'bipolars\' data'},
    { 'arg': args.controls_rec, 'key': 'controls_rec', 'help': 'path to \'controls\' recordings'},
    { 'arg': args.psychosis_rec, 'key': 'psychosis_rec', 'help': 'path to \'psychosis\' recordings'},
    { 'arg': args.bipolars_rec, 'key': 'bipolars_rec', 'help': 'path to \'bipolars\' recordings'},
    { 'arg': args.controls_trans, 'key': 'controls_trans', 'help': 'path to \'controls\' transcriptions'},
    { 'arg': args.psychosis_trans, 'key': 'psychosis_trans', 'help': 'path to \'psychosis\' transcriptions'},
    { 'arg': args.bipolars_trans, 'key': 'bipolars_trans', 'help': 'path to \'bipolars\' transcriptions'},
]

if ( any(not req['arg'] for req in requirements) ):
    print("🙏 Please provide a:")
    for requirement in requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

# =================================== AUXILIARY FUNCTIONS ===================================

def retrieveByTaskInformation(path: str, type: str, tasks: List[str], information_key: str, callback):
    information = []
    subjects_dirs = os.listdir(path)

    for current_subject in tqdm(subjects_dirs, desc="🚀 Processing subjects", leave=True):

        current_subject_path = os.path.join(path, current_subject)

        for current_subject_task in os.listdir(current_subject_path):

            current_task_index = int(current_subject_task.replace(current_subject + '_', '')) - 1
            current_task = tasks[current_task_index]
            current_task_subject_path = os.path.join(current_subject_path, current_subject_task)

            files_path = list( map(lambda file: os.path.join(current_task_subject_path, file), os.listdir(current_task_subject_path)))
            value = callback(files_path)
            entry = { 'id': current_subject, 'type': type, 'task': current_task, information_key: value }
            information.append(entry)
    
    return information

def callbackDuration(paths):

    if len(paths) == 0: return 0

    total_time = 0
    for file in paths:
        audio = AudioSegment.from_file(file)
        total_time = total_time + audio.duration_seconds

    return total_time / len(paths)

def callbackWordLength(paths):

    if len(paths) == 0: return 0

    total_words = 0
    for file_path in paths:
        file = open(file_path, 'r')
        for line in file.readlines():
            line_split = line.split()
            for _ in line_split[4:]: total_words = total_words + 1
        file.close()

    return total_words / len(paths)

def callbackWordFrequency(paths):

    word_frequencies = {}
    for file_path in paths:
        
        text : str = ''
        file = open(file_path, 'r')
        for line in file.readlines():
            line_split = line.split()
            for word in line_split[4:]:
                text = text + ' ' + word
        file.close()

        # Pre processing done to the text
        processed = STANZA_PIPELINE(text)
        processed_lemmas : List[str] = [ word.lemma for sentence in processed.sentences for word in sentence.words ]

        # Add to dict
        for word in processed_lemmas:
            if word is None: continue
            if not word.isalpha() or word in nltk.corpus.stopwords.words('portuguese'): continue

            if word not in word_frequencies: word_frequencies[word] = 1
            else: word_frequencies[word] = word_frequencies[word] + 1

    return word_frequencies

def mergeTasksInformation(info_df, type: str, tasks: List[str], infos, infos_columns):

    information = {}
    columns = info_df.columns

    # Append to entry information from xlsx
    for index, row in info_df.iterrows():
        for task in tasks:
            entry = { 'id': index, 'type': type }
            for column in columns: entry[column.lower()] = row[column]
            entry['task'] = task
            information[entry['id'] + '_' + entry['task']] = entry

    # Append each infos
    for info_column, info in zip(infos_columns, infos):
        for info_line in info:
            code = info_line['id'].split('_')[1] + '_' + info_line['task']
            if code in information: information[code][info_column] = info_line[info_column]

    return list(information.values())

# =================================== MAIN EXECUTION ===================================

TASKS = [ "Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7" ]
TYPE_CONTROL = 'Control'
TYPE_PSYCHOSIS = 'Psychosis'
TYPE_BIPOLAR = 'Control'
TYPES = [TYPE_CONTROL, TYPE_PSYCHOSIS]
WORD_FREQUENCIES_LARGEST = 10

STANZA_PIPELINE = stanza.Pipeline('pt', verbose=False)

# ======================================================================================

# Retrieve Control Data
worksheet_name = args.controls_data.split('/')[-1].replace('.xlsx', '')
dataframe_control = pd.read_excel(args.controls_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
controls_duration_information = retrieveByTaskInformation(args.controls_rec, TYPE_CONTROL, TASKS, 'duration', callbackDuration)
controls_word_count_information = retrieveByTaskInformation(args.controls_trans, TYPE_CONTROL, TASKS, 'word count', callbackWordLength)
controls_word_freq_information = retrieveByTaskInformation(args.controls_trans, TYPE_CONTROL, TASKS, 'word frequencies', callbackWordFrequency)
controls_info = mergeTasksInformation(dataframe_control, TYPE_CONTROL, TASKS,
    [controls_duration_information, controls_word_count_information, controls_word_freq_information],
    ['duration', 'word count', 'word frequencies'])
# Retrieve Psychosis Data
worksheet_name = args.psychosis_data.split('/')[-1].replace('.xlsx', '')
dataframe_psychosis = pd.read_excel(args.psychosis_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
psychosis_duration_information = retrieveByTaskInformation(args.psychosis_rec, TYPE_PSYCHOSIS, TASKS, 'duration', callbackDuration)
psychosis_word_count_information = retrieveByTaskInformation(args.psychosis_trans, TYPE_PSYCHOSIS, TASKS, 'word count', callbackWordLength)
psychosis_word_freq_information = retrieveByTaskInformation(args.psychosis_trans, TYPE_PSYCHOSIS, TASKS, 'word frequencies', callbackWordFrequency)
psychosis_info = mergeTasksInformation(dataframe_psychosis, TYPE_PSYCHOSIS, TASKS,
    [psychosis_duration_information, psychosis_word_count_information, psychosis_word_freq_information],
    ['duration', 'word count', 'word frequencies'])
# Retrieve Psychosis Data
worksheet_name = args.bipolars_data.split('/')[-1].replace('.xlsx', '')
dataframe_bipolars = pd.read_excel(args.bipolars_data, sheet_name = worksheet_name, index_col = 0, engine = 'openpyxl')
bipolars_duration_information = retrieveByTaskInformation(args.bipolars_rec, TYPE_BIPOLAR, TASKS, 'duration', callbackDuration)
bipolars_word_count_information = retrieveByTaskInformation(args.bipolars_trans, TYPE_BIPOLAR, TASKS, 'word count', callbackWordLength)
bipolars_word_freq_information = retrieveByTaskInformation(args.bipolars_trans, TYPE_BIPOLAR, TASKS, 'word frequencies', callbackWordFrequency)
bipolars_info = mergeTasksInformation(dataframe_bipolars, TYPE_BIPOLAR, TASKS,
    [bipolars_duration_information, bipolars_word_count_information, bipolars_word_freq_information],
    ['duration', 'word count', 'word frequencies'])

# Merge information into dataframe
full_task_information = controls_info + psychosis_info + bipolars_info
task_df = pd.DataFrame(full_task_information)
task_df.set_index('id') 
#print(task_df)

print()

# ================================================================== DURATION ==================================================================

print("Exporting 'duration' plots ...")
sns.set_theme(palette="deep")

plt.clf()
try: sns.displot(data=task_df, x="duration", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
except: sns.displot(data=task_df, x="duration", col="task", hue='type', multiple='dodge', kde=False, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by type.pdf')

plt.clf()
try: sns.displot(data=task_df, x="duration", row="gender", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
except: sns.displot(data=task_df, x="duration", row="gender", col="task", hue='type', multiple='dodge', kde=False, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by gender.pdf')

plt.clf()
try: sns.displot(data=task_df, x="duration", row="schooling", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
except: sns.displot(data=task_df, x="duration", row="schooling", col="task", hue='type', multiple='dodge', kde=False, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - task duration by schooling.pdf')

# ================================================================== WORD COUNT ==================================================================

print("Exporting 'word count' plots ...")
sns.set_theme(palette="deep")

plt.clf()
try: sns.displot(data=task_df, x="word count", col="task", hue='type', multiple='dodge', kde=True, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
except: sns.displot(data=task_df, x="word count", col="task", hue='type', multiple='dodge', kde=False, facet_kws=dict(sharex=False, sharey=False), common_bins=True)
plt.savefig(args.save + ' - word count by type.pdf')

# ================================================================== WORD FREQUENCIES ==================================================================

merged_word_freq_info = {}
for _, row in task_df.iterrows():
    if not isinstance(row['word frequencies'], dict): continue

    for word, count in row['word frequencies'].items():
        key = '_'.join([row['type'], row['task'], word])
        if key in merged_word_freq_info: merged_word_freq_info[key]['count'] += count
        else: merged_word_freq_info[key] = {'type': row['type'], 'task': row['task'], 'word': word, 'count': count }

word_frequencies_df = pd.DataFrame(list(merged_word_freq_info.values()))
#print(word_frequencies_df)
nlargest_word_frequencies_df = pd.DataFrame()
for type in TYPES:
    for task in TASKS:
        sub_df = word_frequencies_df[(word_frequencies_df['type'] == type) & (word_frequencies_df['task'] == task)]
        sub_df = sub_df.nlargest(WORD_FREQUENCIES_LARGEST, 'count')

        nlargest_word_frequencies_df = pd.concat([nlargest_word_frequencies_df, sub_df])

print("Exporting 'word frequency' plots ...")
sns.set_theme(palette="deep")

plt.clf()
fig, axes = plt.subplots(len(TYPES), len(TASKS), figsize=(4 * len(TASKS) + 8, 3 * len(TYPES) + 8))
for row_axes, type in zip(axes, TYPES):
    for axis, task in zip(row_axes, TASKS):
        sub_task_df = nlargest_word_frequencies_df[(nlargest_word_frequencies_df['type'] == type) & (nlargest_word_frequencies_df['task'] == task)]
        
        axis.title.set_text('type = ' + type + ' | task = ' + task)
        subplot = sns.barplot(data=sub_task_df, ax=axis, x="word", y="count")
        for item in subplot.get_xticklabels(): item.set_rotation(37.5)
fig.tight_layout(pad=3.0)
plt.savefig(args.save + ' - word frequencies by task and type.pdf')