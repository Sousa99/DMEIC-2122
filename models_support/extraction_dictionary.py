import os
import abc
import sys
import nltk
import pickle
import gensim

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
import NLPyPort as nlport

# ===================================================== SETUP  =====================================================

if not os.path.exists('./exports/'): os.makedirs('./exports')
NUMBER_EXTRACTS_PRINT : int = 1
NUMBER_EXTRACTS_BREAK : Optional[int] = None

# ============================================ DEFINITION OF FUNCTIONS  ============================================

def lemmatize_text(input_text: str) -> nlport.Text:
    
    options = {
			"tokenizer" :           True,
			"pos_tagger" :          False,
			"lemmatizer" :          True,
			"entity_recognition" :  False,
			"np_chunking" :         False,
			"pre_load" :            False,
			"string_or_array" :     True
    }

    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    text_return = nlport.FullPipeline.new_full_pipe(input_text, options=options)
    sys.stdout = old_stdout
    return text_return

# =========================================== DEFINITION OF CONSTANTS ===========================================

EXTRACT_TAG = 'ext'
PARAGRAPH_TAG = 'p'
SENTENCE_TAG = 's'
AUTHOR_TAG = 'a'
TITLE_TAG = 't'
LIST_TAG = 'li'

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

Word = str

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

corpora_dictionary : Dict[Word, Dict[str, int]] = {}
documents_clean : List[List[str]] = []

file = open('./corpora/CETEMPublico/CETEMPublico1.7.txt', 'r', encoding='latin-1')
queu_of_elements : List[Any] = []
count_extracts : int = 0

line = file.readline()
while line:
    line = line.strip()
    if line.startswith('</'):
        # Closing Tag
        line = line.replace('</', '', 1).replace('>', '', 1)

        # Closing an Extract
        if line.startswith(EXTRACT_TAG):
            extract : Extract = queu_of_elements.pop()
            extract_words : List[Word] = extract.get_words()
            extract_entire : str = ' '.join(extract_words)

            lemmatized : List[str] = lemmatize_text(extract_entire).lemas
            lemmatized_filtered : List[str] = list(filter(lambda word: word.isalpha() and word != 'EOS', lemmatized))
            lemmatized_filtered : List[str] = list(filter(lambda word: word not in nltk.corpus.stopwords.words('portuguese'), lemmatized_filtered))

            extract_code : str = extract.get_code()
            for word in lemmatized_filtered:
                if word not in corpora_dictionary: corpora_dictionary[word] = { extract_code: 1 }
                elif word in corpora_dictionary and extract_code not in corpora_dictionary[word]: corpora_dictionary[word][extract_code] = 1
                else: corpora_dictionary[word][extract_code] = corpora_dictionary[word][extract_code] + 1

            documents_clean.append(lemmatized_filtered)

            if count_extracts % NUMBER_EXTRACTS_PRINT == 0: print(f'🚀 \'{count_extracts}\' extracts have already been processed', end="\r")
            if NUMBER_EXTRACTS_BREAK is not None and count_extracts == NUMBER_EXTRACTS_BREAK: break

        # Closing others
        else:
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
        for word in line.split(): queu_of_elements[-1].add_word(word)

    
    line = file.readline()

file.close()
print()

file = open('./exports/corpora_documents_clean.pkl', 'wb')
pickle.dump(documents_clean, file)
file.close()

corpora_dataset = pd.DataFrame.from_dict(corpora_dictionary)
corpora_dataset = corpora_dataset.fillna(0)
corpora_dataset = corpora_dataset.astype(int)
corpora_dataset.to_csv('./exports/corpora_dataset.cvs')

dictionary = gensim.corpora.Dictionary(documents_clean)
dictionary.save('./exports/corpora_dictionary.bin')