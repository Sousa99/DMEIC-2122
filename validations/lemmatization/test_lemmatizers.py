import os
import nltk
import subprocess

# ================================================= NLTK DOWNLOADS  =================================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()
'''
# ================================================= NLTK DOWNLOADS  =================================================

from enum import Enum
from random import sample
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ===================================================== SETUP =====================================================

if not os.path.exists('./exports/'): os.makedirs('./exports')
NUMBER_EXTRACTS_PRINT : int = 1

NUMBER_EXTRACTS_TO_USE : int = 1
CORPORA_FILE : str = "./corpora/CETEMPublico/CETEMPublicoAnotado2019.txt"

# ================================================== SAVE VARIABLE ==================================================

corpora_dictionary : Dict[str, Dict[str, int]] = {}
documents_clean : List[List[str]] = []

# ============================================ DEFINITION OF FUNCTIONS  ============================================

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

# ================================================ MAIN EXECUTION ================================================

command_to_run : str = f'grep -n "<ext" {CORPORA_FILE} | cut -f1 -d:'
process_return = subprocess.run(command_to_run, capture_output=True, text=True, shell=True)

lines_with_extracts : List[str] = process_return.stdout.splitlines()
lines_with_extracts = filter(lambda line: line != "", lines_with_extracts)
lines_with_extracts : List[int] = list(map(lambda line: int(line), lines_with_extracts))

chosen_extracts : List[int] = sample(lines_with_extracts, NUMBER_EXTRACTS_TO_USE)
chosen_extracts.sort(reverse=True)

print(chosen_extracts)

file = open(CORPORA_FILE, 'r', encoding='latin-1')
queu_of_elements : List[str] = []
current_extract : Optional[Extract] = None
count_extracts : int = 0
count_line : int = 0

line = file.readline()
while line and (len(chosen_extracts) > 0 or current_extract is not None):

    count_line = count_line + 1
    line = line.strip()
    if current_extract is None and len(chosen_extracts) > 0 and chosen_extracts[0] != count_line:
        line = file.readline()
        continue

    # Reached Line of Start of Extract
    if len(chosen_extracts) > 0 and chosen_extracts[0] == count_line:
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
                print("\t Words:", current_extract.get_words())
                print("\t Lemmas:", current_extract.get_lemmas())
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
            for lema in line_splitted[3].split('+'):
                word = lema.split('&')[0]
                current_extract.add_lemma(word)

    line = file.readline()

file.close()
print()