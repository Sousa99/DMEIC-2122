import os
import abc
import sys
import nltk
import time
import stanza
import subprocess
import editdistance

# ================================================= NLTK DOWNLOADS  =================================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()

stanza.download('pt')
print()
'''
# ================================================= NLTK DOWNLOADS  =================================================

from enum       import Enum
from pprint     import pprint
from random     import sample
from functools  import partial
from datetime   import datetime
from typing     import Any, Dict, List, Optional, Tuple, Type

import numpy                    as np
import pandas                   as pd
import seaborn                  as sns
import matplotlib.pyplot        as plt
import NLPyPort.FullPipeline    as nlpyport

# ===================================================== SETUP =====================================================

if not os.path.exists('./exports/'): os.makedirs('./exports', exist_ok=True)
NUMBER_EXTRACTS_PRINT : int = 1

NUMBER_EXTRACTS_TO_USE : int = 2500
CORPORA_FILE : str = "./corpora/CETEMPublico/CETEMPublicoAnotado2019.txt"

EXPORT_DIRECTORY = './exports/'
EXECUTION_TIMESTAMP = datetime.now()
EXPORT_CSV_EXTENSION = '.csv'
EXPORT_TXT_EXTENSION = '.txt'
EXPORT_IMAGE_EXTENSION = '.pdf'

CURRENT_DIRECTORIES = []

# ================================================== SAVE VARIABLE ==================================================

extracts_information : List[Dict[str, Any]] = []

# ============================================ DEFINITION OF FUNCTIONS  ============================================

def compute_path(filename: str, extension: str) -> str:

    timestampStr = EXECUTION_TIMESTAMP.strftime("%Y.%m.%d %H.%M.%S")
    directory_path = os.path.join(EXPORT_DIRECTORY, timestampStr, *CURRENT_DIRECTORIES)
    filename_full = filename + extension

    if not os.path.exists(directory_path): os.makedirs(directory_path, exist_ok=True)
    return os.path.join(directory_path, filename_full)

# =========================================== DEFINITION OF CONSTANTS ===========================================

EXTRACT_TAG : str = 'ext'
PARAGRAPH_TAG : str = 'p'
SENTENCE_TAG : str = 's'
AUTHOR_TAG : str = 'a'
TITLE_TAG : str = 't'
LIST_TAG : str = 'li'

SKIP_TAGS : List[str] = [ AUTHOR_TAG, TITLE_TAG ]
BLACKLISTED_TAGS : List[str] = ['mwe']

# ========================================== DEFINITION OF ENUMERATORS ==========================================

class ExtractSemester(Enum):
    FIRST_SEMESTER      = 'FIRST_SEMESTER'
    SECOND_SEMESTER     = 'SECOND_SEMESTER'

# ====================================== DEFINITION OF ENUMERATORS MAPPING ======================================

EXTRACT_SEMESTER_MAP = {
    'a'     :   ExtractSemester.FIRST_SEMESTER,
    'b'     :   ExtractSemester.SECOND_SEMESTER,
}

# ============================================ DEFINITION OF CLASSES ============================================

class Lemmatizer(abc.ABC):

    @abc.abstractmethod
    def __init__(self) -> None: super().__init__()
    @abc.abstractmethod
    def get_name(self) -> str: exit(f"🚨 Method 'get_name' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def process_words(self, words: List[str]) -> List[str]: exit(f"🚨 Method 'process_words' not defined for '{self.__class__.__name__}'")

class LemmatizerNLPyPort(Lemmatizer):

    options = { "tokenizer" : True, "pos_tagger" : True, "lemmatizer" : True, "entity_recognition" : False,
        "np_chunking" : False, "pre_load" : True, "string_or_array" : True }
    config_list = nlpyport.load_congif_to_list()

    def __init__(self) -> None: super().__init__()
    def get_name(self) -> str: return "NLPyPort"
    def process_words(self, words: List[str]) -> List[str]:
        words_as_string : str = ' '.join(words)

        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        processed = nlpyport.new_full_pipe(words_as_string, options=self.options, config_list=self.config_list)
        sys.stdout = old_stdout

        return list(filter(lambda lemma: lemma != 'EOS', processed.lemas))

class LemmatizerStanza(Lemmatizer):

    pipeline = stanza.Pipeline('pt', verbose=False)

    def __init__(self) -> None: super().__init__()
    def get_name(self) -> str: return "Stanza"
    def process_words(self, words: List[str]) -> List[str]:
        words_as_string : str = ' '.join(words)
        processed = self.pipeline(words_as_string)
        return [ word.lemma for sentence in processed.sentences for word in sentence.words ]

class LemmatizerSTRING(Lemmatizer):
    
    def __init__(self) -> None: super().__init__()
    def get_name(self) -> str: return "STRING"
    def process_words(self, words: List[str]) -> List[str]:
        global CURRENT_DIRECTORIES
        words_as_string : str = ' '.join(words)
        
        CURRENT_DIRECTORIES = ['tmp']
        file_path : str = compute_path('current_lemmatization', EXPORT_TXT_EXTENSION)
        file = open(file_path, 'w')
        file.write(words_as_string)
        file.close()

        command_call : str = f'cat "{file_path}" | ~/share/STRING/string.sh -prexip2'
        process_return = subprocess.run(command_call, shell=True, check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        lines_with_extracts : List[str] = process_return.stdout.decode().splitlines()
        return list(map(lambda sentence: sentence.split('|')[1], lines_with_extracts))

class Extract():

    words   :   List[str] = []
    lemmas  :   List[str] = []

    def __init__(self, number: str, year_semester: str) -> None:
        self.number : int = int(number)

        self.year = 1900 + int(year_semester[0:2])
        if year_semester[2] not in EXTRACT_SEMESTER_MAP:
            exit(f'🚨 Semester code \'{year_semester[2]}\' not recognized')
        self.semester = EXTRACT_SEMESTER_MAP[year_semester[2]]

    def add_word(self, word: str) -> None: self.words.append(word)
    def add_lemma(self, lemma: str) -> None: self.lemmas.append(lemma)
    def get_words(self) -> List[str]: return self.words
    def get_lemmas(self) -> List[str]: return self.lemmas
    def get_code(self) -> str: return f'{self.year}.{self.semester.value}.{self.number}'

    def test_lemmatizers(self, export_information: bool = False) -> List[Dict[str, Any]]:
        global CURRENT_DIRECTORIES

        export_information : Dict[str, List[str]] = { 'words': self.words, 'lemmas_correct': self.lemmas }

        information : List[Dict[str, Any]] = []
        lemmatizers : List[Type[Lemmatizer]] = [ LemmatizerNLPyPort, LemmatizerStanza, LemmatizerSTRING ]
        for lemmatizer in lemmatizers:

            words = self.get_words()

            start_time : float = time.time()
            lemmatizer_initialized = lemmatizer()
            lemmas_achieved = lemmatizer_initialized.process_words(words)
            end_time : float = time.time()

            export_information[f'lemmas_{lemmatizer_initialized.get_name()}'] = lemmas_achieved
            information_entry : Dict[str, Any] = { 'extract': self.get_code(), 'lemmatizer': lemmatizer_initialized.get_name(),
                'score': 1.0 - (editdistance.eval(self.lemmas, lemmas_achieved) / max(len(self.lemmas), len(lemmas_achieved))), 'duration': (end_time - start_time) / len(self.words) }
            information.append(information_entry)

            CURRENT_DIRECTORIES = ['extracts_information']
            file = open(compute_path(self.get_code(), EXPORT_TXT_EXTENSION), 'w')
            pprint(export_information, stream=file, compact=True, width=150)
            file.close()

        return information

# ================================================ MAIN EXECUTION ================================================

command_to_run : str = f'grep -n "<ext" {CORPORA_FILE} | cut -f1 -d:'
process_return = subprocess.run(command_to_run, shell=True, check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

lines_with_extracts : List[str] = process_return.stdout.decode().splitlines()
lines_with_extracts = filter(lambda line: line != "", lines_with_extracts)
lines_with_extracts : List[int] = list(map(lambda line: int(line), lines_with_extracts))

chosen_extracts : List[int] = sample(lines_with_extracts, NUMBER_EXTRACTS_TO_USE)
chosen_extracts.sort(reverse=True)

file = open(CORPORA_FILE, 'r', encoding='latin-1')
queu_of_elements : List[str] = []
current_extract : Optional[Extract] = None
count_extracts : int = 0
count_line : int = 0

last_lemma : Optional[str] = None
line = file.readline()
while line and (len(chosen_extracts) > 0 or current_extract is not None):

    count_line = count_line + 1
    line = line.strip()
    if current_extract is None and len(chosen_extracts) > 0 and chosen_extracts[-1] != count_line:
        line = file.readline()
        continue

    # Reached Line of Start of Extract
    if len(chosen_extracts) > 0 and chosen_extracts[-1] == count_line:
        line = line.replace('<', '', 1).replace('>', '', 1)
        if line.startswith(EXTRACT_TAG):
            chosen_extracts.pop()
            line = line.replace(EXTRACT_TAG, '', 1).strip()
            line_splits = line.split()

            number, semester = 'UNKNOWN', 'UNKNOWN'
            for line_split in line_splits:
                code_splits = line_split.split('=')
                if code_splits[0] == 'n':       number = code_splits[1]
                elif code_splits[0] == 'sem':   semester = code_splits[1]
            
            current_extract = Extract(number, semester)
            count_extracts = count_extracts + 1
            queu_of_elements.append(EXTRACT_TAG)

    # Currently Reading an Extract
    elif current_extract is not None:
        # Closing Tag
        if line.startswith('</'):
            line = line.replace('</', '', 1).replace('>', '', 1)
            # Closing an Extract
            if line.startswith(EXTRACT_TAG):
                extracts_information.extend(current_extract.test_lemmatizers(export_information=True))
                current_extract = None
                if count_extracts % NUMBER_EXTRACTS_PRINT == 0:
                    print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")
            # Closing others
            elif not any(map(lambda blacklisted_tag: line.startswith(blacklisted_tag), BLACKLISTED_TAGS)):
                queu_of_elements.pop()
        # Opening Tag
        elif line.startswith('<'):
            # Opening Tag
            line = line.replace('<', '', 1).replace('>', '', 1)
            if line.startswith(EXTRACT_TAG): exit("🚨 Should not be opening an Extract tag here!")
            elif line.startswith(PARAGRAPH_TAG): queu_of_elements.append(PARAGRAPH_TAG)
            elif line.startswith(SENTENCE_TAG): queu_of_elements.append(SENTENCE_TAG)
            elif line.startswith(AUTHOR_TAG): queu_of_elements.append(AUTHOR_TAG)
            elif line.startswith(TITLE_TAG): queu_of_elements.append(TITLE_TAG)
            elif line.startswith(LIST_TAG): queu_of_elements.append(LIST_TAG)
        # Other Reads
        elif line != "" and queu_of_elements[-1] not in SKIP_TAGS:
            line_splitted = line.split()
            current_extract.add_word(line_splitted[0])
            if '=' not in line_splitted[3] or last_lemma is None or last_lemma != line_splitted[3]:
                last_lemma = line_splitted[3]
                for lema in line_splitted[3].split('+'):
                    word = lema.split('&')[0]
                    current_extract.add_lemma(word.replace('=', ' '))

    line = file.readline()

file.close()
print()

extracts_information_df = pd.DataFrame.from_dict(extracts_information)
extracts_information_df.set_index(['extract', 'lemmatizer'], inplace=True)
analysis_information_df = extracts_information_df.groupby(['lemmatizer'], as_index=True).agg({ 'score': ['mean','std'], 'duration': ['mean','std'] })

CURRENT_DIRECTORIES = []

extracts_information_df.to_csv(compute_path('information_extracts', EXPORT_CSV_EXTENSION))
analysis_information_df.to_csv(compute_path('information_analysis', EXPORT_CSV_EXTENSION))

sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
sns.set_context("paper", font_scale=1.15)

plt.figure()
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="lemmatizer", y="score", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="lemmatizer", y="score", jitter=False, alpha=0.15)
plt.xlabel("Lemmatizer")
plt.ylabel("Score")
plt.tight_layout()
sns.set_context("paper", font_scale=1.15)

plt.figure()
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="lemmatizer", y="duration", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="lemmatizer", y="duration", jitter=False, alpha=0.15)
plt.xlabel("Lemmatizer")
plt.ylabel("Seconds / Word")
plt.tight_layout()
plt.figure()
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="score", y="lemmatizer", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="score", y="lemmatizer", jitter=False, alpha=0.15)
plt.tight_layout()
plt.savefig(compute_path('boxplot_score', EXPORT_IMAGE_EXTENSION))

plt.figure()
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="duration", y="lemmatizer", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="duration", y="lemmatizer", jitter=False, alpha=0.15)
plt.tight_layout()
sns.set_context("paper", font_scale=1.15)
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="score", y="lemmatizer", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="score", y="lemmatizer", jitter=False, alpha=0.15)
plt.tight_layout()
plt.savefig(compute_path('boxplot_score', EXPORT_IMAGE_EXTENSION))

plt.figure()
violin_plot = sns.violinplot(data=extracts_information_df.reset_index(), x="duration", y="lemmatizer", inner=None, color=".8")
strip_plot = sns.stripplot(data=extracts_information_df.reset_index(), x="duration", y="lemmatizer", jitter=False, alpha=0.15)
plt.tight_layout()
plt.savefig(compute_path('boxplot_score', EXPORT_IMAGE_EXTENSION))
