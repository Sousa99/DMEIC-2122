import os
import gensim

from numpy.typing   import NDArray
from typing         import List, Optional, Tuple

import numpy    as np

# =================================== CONSTANTS DEFINITIONS ===================================

PATH_MODELS_SUPPORT = '../models_support/exports/'

FILENAME_DICTIONARY = 'corpora_dictionary.bin'

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class ModelTDIDF():

    def __init__(self, documents: List[List[str]]) -> None:
        filepath_dictionary = os.path.join(PATH_MODELS_SUPPORT, FILENAME_DICTIONARY)
        if not os.path.exists(filepath_dictionary): exit(f'🚨 The file \'{filepath_dictionary}\' does not exist')

        self.dictionary     : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load(filepath_dictionary)
        self.documents      : List[List[str]] = documents
        self.documents_bow  : List[List[int]] = list(map(lambda document: self.dictionary.doc2bow(document), self.documents))

        self.model = gensim.models.TfidfModel(self.documents_bow)

    def process_document(self, document: List[str]):
        document_bow        : List[int]                 = self.dictionary.doc2bow(document)
        td_idf_bow_result   : List[Tuple[int, float]]   = self.model[document_bow]
        td_idf_result       : List[Tuple[str, float]]   = list(map(lambda item: (self.dictionary[item[0]], item[1]), td_idf_bow_result))

        return td_idf_result