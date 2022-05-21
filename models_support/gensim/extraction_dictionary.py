import os
import nltk
import pickle
import gensim
import argparse

# ================================================= NLTK DOWNLOADS  =================================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()
'''
# ================================================= NLTK DOWNLOADS  =================================================

from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd

# ================================================== CONSTANTS ===================================================

PATH_TO_EXPORTS : str = '../exports/'
PATH_TO_DOCUMENTS : str = '../exports/documents_clean/'

PATH_TO_CORPORA : str = '../corpora/CETEMPublico/CETEMPublicoAnotado2019.txt'

PATH_TO_DICTIONARY : str = '../exports/corpora_dictionary.bin'

# ===================================================== SETUP =====================================================

parser = argparse.ArgumentParser()
parser.add_argument("-extracts_per_run",        help="the number of extracts that should execute")
parser.add_argument("-parallelization_key",     help="key for the parallelized model, if not given is executed sequentially")
parser.add_argument("-parallelization_index",   help="key index for the parallelized model, must be given if task is to be parallelized")
arguments = parser.parse_args()
arguments_dict = vars(arguments)

PARALLELIZATION_EXTRACT = "extract"
PARALLELIZATION_FINAL = "final"

if not os.path.exists(PATH_TO_EXPORTS): os.makedirs(PATH_TO_EXPORTS)
if not os.path.exists(PATH_TO_DOCUMENTS): os.makedirs(PATH_TO_DOCUMENTS)

NUMBER_EXTRACTS_PRINT : int = 1
if arguments_dict['extracts_per_run'] is None: NUMBER_EXTRACTS_BREAK : Optional[int] = None
else: NUMBER_EXTRACTS_BREAK : Optional[int] = int(arguments_dict['extracts_per_run'])

# ================================================== SAVE VARIABLE ==================================================

# ============================================ DEFINITION OF FUNCTIONS  ============================================

def read_lines() -> None:

    file = open(PATH_TO_CORPORA, 'r', encoding='latin-1')
    queu_of_elements : List[str] = []
    count_extracts : int = 0
    count_line : int = 0

    current_extract : Optional[Extract] = None

    line = file.readline()
    while line:

        count_line = count_line + 1
        # If running parallelized skip until correct line
        if arguments_dict['parallelization_index'] is not None and int(arguments_dict['parallelization_index']) > count_line:
            line = file.readline()
            continue

        line = line.strip()
        if line.startswith('</'):
            # Closing Tag
            line = line.replace('</', '', 1).replace('>', '', 1)

            # Closing an Extract
            if line.startswith(EXTRACT_TAG):
                extract_words : List[str] = current_extract.get_words()
                extract_code : str = current_extract.get_code()
                
                file_save = open(f'{PATH_TO_DOCUMENTS}lemmatized_{extract_code}.pkl', 'wb')
                pickle.dump(extract_words, file_save)
                file_save.close()

                if count_extracts % NUMBER_EXTRACTS_PRINT == 0: print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")
                if NUMBER_EXTRACTS_BREAK is not None and count_extracts == NUMBER_EXTRACTS_BREAK: break

            # Closing others
            elif not any(map(lambda blacklisted_tag: line.startswith(blacklisted_tag), BLACKLISTED_TAGS)):
                queu_of_elements.pop()

        elif line.startswith('<'):
            # Opening Tag
            line = line.replace('<', '', 1).replace('>', '', 1)
            if line.startswith(EXTRACT_TAG):
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

            elif line.startswith(PARAGRAPH_TAG): queu_of_elements.append(PARAGRAPH_TAG)
            elif line.startswith(SENTENCE_TAG): queu_of_elements.append(SENTENCE_TAG)
            elif line.startswith(AUTHOR_TAG): queu_of_elements.append(AUTHOR_TAG)
            elif line.startswith(TITLE_TAG): queu_of_elements.append(TITLE_TAG)
            elif line.startswith(LIST_TAG): queu_of_elements.append(LIST_TAG)

        elif line != "" and queu_of_elements[-1] not in SKIP_TAGS:
            line_splitted = line.split()
            lemas : str = line_splitted[3]
            for lema in lemas.split('+'):
                word = lema.split('&')[0]
                word = word.replace('=', ' ')
                if word.isalpha() and word not in nltk.corpus.stopwords.words('portuguese'):
                    current_extract.add_word(word)
        
        line = file.readline()

    file.close()
    print()

def save_information() -> None:
    gensim_dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary()

    count_extracts : int = 0
    for filename in os.listdir(PATH_TO_DOCUMENTS):
        file_path = os.path.join(PATH_TO_DOCUMENTS, filename)
        if not os.path.isfile(file_path): continue
        
        file_save = open(file_path, 'rb')
        lemmatized_filtered : List[str] = pickle.load(file_save)
        file_save.close()
        # Add to Gensim Dictionary
        gensim_dictionary.add_documents([lemmatized_filtered])

        count_extracts = count_extracts + 1
        if count_extracts % NUMBER_EXTRACTS_PRINT == 0: print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")

    print()

    gensim_dictionary.save(PATH_TO_DICTIONARY)

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

class Extract():

    words : List[str] = []

    def __init__(self, number: str, year_semester: str) -> None:
        self.number : int = int(number)

        self.year = 1900 + int(year_semester[0:2])
        if year_semester[2] not in EXTRACT_SEMESTER_MAP:
            exit(f'🚨 Semester code \'{year_semester[2]}\' not recognized')
        self.semester = EXTRACT_SEMESTER_MAP[year_semester[2]]

    def add_word(self, word: str) -> None: self.words.append(word)
    def get_words(self) -> List[str]: return self.words
    def get_code(self) -> str: return f'{self.year}.{self.semester.value}.{self.number}'

# ================================================ MAIN EXECUTION ================================================

if arguments_dict['parallelization_key'] is None or arguments_dict['parallelization_key'] == PARALLELIZATION_EXTRACT: read_lines()
if arguments_dict['parallelization_key'] is None or arguments_dict['parallelization_key'] == PARALLELIZATION_FINAL: save_information()