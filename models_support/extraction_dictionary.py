import os
import abc
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

# ===================================================== SETUP =====================================================

parser = argparse.ArgumentParser()
parser.add_argument("-extracts_per_run",        help="the number of extracts that should execute")
parser.add_argument("-parallelization_key",     help="key for the parallelized model, if not given is executed sequentially")
parser.add_argument("-parallelization_index",   help="key index for the parallelized model, must be given if task is to be parallelized")
arguments = parser.parse_args()
arguments_dict = vars(arguments)

PARALLELIZATION_EXTRACT = "extract"
PARALLELIZATION_FINAL = "final"

if not os.path.exists('./exports/'): os.makedirs('./exports')
if arguments_dict['parallelization_key'] is not None and not os.path.exists('./tmp/'): os.makedirs('./tmp/')
NUMBER_EXTRACTS_PRINT : int = 1
if arguments_dict['extracts_per_run'] is None: NUMBER_EXTRACTS_BREAK : Optional[int] = None
else: NUMBER_EXTRACTS_BREAK : Optional[int] = int(arguments_dict['extracts_per_run'])

# ================================================== SAVE VARIABLE ==================================================

corpora_dictionary : Dict[str, Dict[str, int]] = {}
documents_clean : List[List[str]] = []

# ============================================ DEFINITION OF FUNCTIONS  ============================================

def read_lines() -> None:

    file = open('./corpora/CETEMPublico/CETEMPublicoAnotado2019.txt', 'r', encoding='latin-1')
    queu_of_elements : List[Any] = []
    count_extracts : int = 0
    count_line : int = 0

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
                extract : Extract = queu_of_elements.pop()
                extract_words : List[Word] = extract.get_words()

                lemmatized : List[List[str]] = list(map(lambda word: word.get_lemma(), extract_words))
                lemmatized_flattened : List[str] = [item for sublist in lemmatized for item in sublist]
                lemmatized_filtered : List[str] = list(filter(lambda word: word.isalpha(), lemmatized_flattened))
                lemmatized_filtered : List[str] = list(filter(lambda word: word not in nltk.corpus.stopwords.words('portuguese'), lemmatized_filtered))

                extract_code : str = extract.get_code()

                if arguments_dict['parallelization_key'] is None:
                    documents_clean.append(lemmatized_filtered)
                    for word in lemmatized_filtered:
                        if word not in corpora_dictionary: corpora_dictionary[word] = { extract_code: 1 }
                        elif word in corpora_dictionary and extract_code not in corpora_dictionary[word]: corpora_dictionary[word][extract_code] = 1
                        else: corpora_dictionary[word][extract_code] = corpora_dictionary[word][extract_code] + 1

                else:
                    file_save = open(f'./tmp/lemmatized_{extract_code}.pkl', 'wb')
                    pickle.dump(lemmatized_filtered, file_save)
                    file_save.close()

                if count_extracts % NUMBER_EXTRACTS_PRINT == 0: print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")
                if NUMBER_EXTRACTS_BREAK is not None and count_extracts == NUMBER_EXTRACTS_BREAK: break

            # Closing others
            elif not any(map(lambda blacklisted_tag: line.startswith(blacklisted_tag), BLACKLISTED_TAGS)):
                last_element = queu_of_elements.pop()
                queu_of_elements[-1].add_element(last_element)

        elif line.startswith('<'):
            # Opening Tag
            line = line.replace('<', '', 1).replace('>', '', 1)
            if line.startswith(EXTRACT_TAG):
                line = line.replace(EXTRACT_TAG, '', 1).strip()
                line_splits = line.split()

                number, section, semester = 'UNKNOWN', 'UNKNOWN', 'UNKNOWN'
                for line_split in line_splits:
                    code_splits = line_split.split('=')
                    if code_splits[0] == 'n':       number = code_splits[1]
                    elif code_splits[0] == 'sec':   section = code_splits[1]
                    elif code_splits[0] == 'sem':   semester = code_splits[1]
                
                extract = Extract(number, section, semester)
                count_extracts = count_extracts + 1
                queu_of_elements.append(extract)

            elif line.startswith(PARAGRAPH_TAG): queu_of_elements.append(Paragraph())
            elif line.startswith(SENTENCE_TAG): queu_of_elements.append(Sentence())
            elif line.startswith(AUTHOR_TAG): queu_of_elements.append(Author())
            elif line.startswith(TITLE_TAG): queu_of_elements.append(Title())
            elif line.startswith(LIST_TAG): queu_of_elements.append(ListItem())

        elif line != "":
            line_splitted = line.split()
            word : Word = Word(line_splitted[0], line_splitted[3], line_splitted[4], line_splitted[5], line_splitted[6], line_splitted[7], line_splitted[8])
            queu_of_elements[-1].add_word(word)
        
        line = file.readline()

    file.close()
    print()

def load_information() -> None:
    global documents_clean, corpora_dictionary
    
    count_extracts : int = 0
    for filename in os.listdir('./tmp/'):
        file_path = os.path.join('./tmp/', filename)
        if not os.path.isfile(file_path): continue

        extract_code : str = filename.replace('lemmatized_', '').replace('.pkl', '')
        file_save = open(file_path, 'rb')
        lemmatized_filtered : List[str] = pickle.load(file_save)
        file_save.close()

        documents_clean.append(lemmatized_filtered)

        for word in lemmatized_filtered:
            if word not in corpora_dictionary: corpora_dictionary[word] = { extract_code: 1 }
            elif word in corpora_dictionary and extract_code not in corpora_dictionary[word]: corpora_dictionary[word][extract_code] = 1
            else: corpora_dictionary[word][extract_code] = corpora_dictionary[word][extract_code] + 1

        count_extracts = count_extracts + 1
        if count_extracts % NUMBER_EXTRACTS_PRINT == 0: print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")
    print()

def save_information() -> None:
    file = open('./exports/corpora_documents_clean.pkl', 'wb')
    pickle.dump(documents_clean, file)
    file.close()

    corpora_dataset = pd.DataFrame.from_dict(corpora_dictionary)
    corpora_dataset = corpora_dataset.fillna(0)
    corpora_dataset = corpora_dataset.astype(int)
    corpora_dataset.to_csv('./exports/corpora_dataset.cvs')

    dictionary = gensim.corpora.Dictionary(documents_clean)
    dictionary.save('./exports/corpora_dictionary.bin')

# =========================================== DEFINITION OF CONSTANTS ===========================================

EXTRACT_TAG : str = 'ext'
PARAGRAPH_TAG : str = 'p'
SENTENCE_TAG : str = 's'
AUTHOR_TAG : str = 'a'
TITLE_TAG : str = 't'
LIST_TAG : str = 'li'

BLACKLISTED_TAGS : List[str] = ['mwe']

# ========================================== DEFINITION OF ENUMERATORS ==========================================

class ExtractClassification(Enum):
    CLASSIFICATION_POLITICS         = 'POLITICS'
    CLASSIFICATION_SOCIETY          = 'SOCIETY'
    CLASSIFICATION_SPORTS           = 'SPORTS'
    CLASSIFICATION_ECONOMY          = 'ECONOMY'
    CLASSIFICATION_CULTURE          = 'CULTURE'
    CLASSIFICATION_OPINION          = 'OPINION'
    CLASSIFICATION_INFORMATICS      = 'INFORMATICS'
    CLASSIFICATION_NON_DETERMINED   = 'NON_DETERMINED'

class ExtractSemester(Enum):
    FIRST_SEMESTER      = 'FIRST_SEMESTER'
    SECOND_SEMESTER     = 'SECOND_SEMESTER'

# ====================================== DEFINITION OF ENUMERATORS MAPPING ======================================

EXTRACT_CLASSIFICATIONS_MAP = {
    'pol'   :   ExtractClassification.CLASSIFICATION_POLITICS,
    'soc'   :   ExtractClassification.CLASSIFICATION_SOCIETY,
    'des'   :   ExtractClassification.CLASSIFICATION_SPORTS,
    'eco'   :   ExtractClassification.CLASSIFICATION_ECONOMY,
    'clt'   :   ExtractClassification.CLASSIFICATION_CULTURE,
    'opi'   :   ExtractClassification.CLASSIFICATION_OPINION,
    'com'   :   ExtractClassification.CLASSIFICATION_INFORMATICS,
    'nd'    :   ExtractClassification.CLASSIFICATION_NON_DETERMINED,
}

EXTRACT_SEMESTER_MAP = {
    'a'     :   ExtractSemester.FIRST_SEMESTER,
    'b'     :   ExtractSemester.SECOND_SEMESTER,
}

# ============================================ DEFINITION OF CLASSES ============================================

class Word():
    word_raw    :   str
    lemas       :   List[str]
    pos         :   str
    temcagr     :   str
    pessnum     :   str
    gen         :   str
    fun         :   str

    def __init__(self, word_raw: str, lemas: str, pos: str, temcagr: str, pessnum: str, gen: str, fun: str) -> None:
        self.word_raw = word_raw
        self.lemas = lemas.split('+')
        self.pos = pos
        self.temcagr = temcagr
        self.pessnum = pessnum
        self.gen = gen
        self.fun = fun

    def get_lemma(self) -> List[str]: return self.lemas

class Element(abc.ABC):

    @abc.abstractproperty
    def words(self) -> List[Word]: pass
    @abc.abstractproperty
    def elements(self) -> List['Element']: pass

    @abc.abstractmethod
    def __init__(self) -> None: super().__init__()

    def add_element(self, element: 'Element') -> None: self.elements.append(element)
    def add_word(self, word: Word) -> None: self.words.append(word)
    def get_words(self) -> List[Word]:
        all_words : List[Word] = list(self.words)
        for element in self.elements:
            for word in element.get_words():
                all_words.append(word)
        return all_words

class Extract(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self, number: str, classifications: str, year_semester: str) -> None:
        self.number : int = int(number)

        self.classifications : List[ExtractClassification] = []
        for classification_code in classifications.split('-'):
            if classification_code not in EXTRACT_CLASSIFICATIONS_MAP:
                exit(f'🚨 Classification code \'{classification_code}\' not recognized')
            self.classifications.append(EXTRACT_CLASSIFICATIONS_MAP[classification_code])

        self.year = 1900 + int(year_semester[0:2])
        if year_semester[2] not in EXTRACT_SEMESTER_MAP:
            exit(f'🚨 Semester code \'{year_semester[2]}\' not recognized')
        self.semester = EXTRACT_SEMESTER_MAP[year_semester[2]]

    def add_word(self, word: Word) -> None: exit(f'🚨 Words are not addable to {self.__class__.__name__}')
    def get_code(self) -> str: return f'{self.year}.{self.semester.value}.{self.number}'

class Author(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self) -> None: super().__init__()
    def add_element(self, element: Element) -> None: exit(f'🚨 Elements are not addable to {self.__class__.__name__}')
    def get_words(self) -> List[Word]: return []
    
class Title(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self) -> None: super().__init__()
    def add_element(self, element: Element) -> None: exit(f'🚨 Elements are not addable to {self.__class__.__name__}')
    def get_words(self) -> List[Word]: return []

class ListItem(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self) -> None: super().__init__()
    def add_element(self, element: Element) -> None: exit(f'🚨 Elements are not addable to {self.__class__.__name__}')
    
class Sentence(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self) -> None: super().__init__()
    def add_element(self, element: Element) -> None: exit(f'🚨 Elements are not addable to {self.__class__.__name__}')
    
class Paragraph(Element):

    words : List[Word] = []
    elements : List[Element] = []

    def __init__(self) -> None: super().__init__()
    def add_word(self, word: Word) -> None: exit(f'🚨 Words are not addable to {self.__class__.__name__}')
    
# ================================================ MAIN EXECUTION ================================================

if arguments_dict['parallelization_key'] is None or arguments_dict['parallelization_key'] == PARALLELIZATION_EXTRACT: read_lines()
if arguments_dict['parallelization_key'] is not None and arguments_dict['parallelization_key'] == PARALLELIZATION_FINAL: load_information()
if arguments_dict['parallelization_key'] is None or arguments_dict['parallelization_key'] == PARALLELIZATION_FINAL: save_information()