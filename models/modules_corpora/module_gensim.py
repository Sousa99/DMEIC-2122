import os
import abc
import gensim

from numpy.typing   import NDArray
from typing         import List, Optional

import numpy    as np

# =================================== CONSTANTS DEFINITIONS ===================================

PATH_MODELS_SUPPORT = '../models_support/exports/'

FILENAME_DICTIONARY = 'corpora_dictionary.bin'
FILENAME_LSA        = 'lsa_best_model.bin'

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class ModelCorpora(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_word_embedding(self, word: str) -> Optional[List[float]]:
        pass

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class ModelLSA(ModelCorpora):

    def __init__(self) -> None:
        filepath_dictionary = os.path.join(PATH_MODELS_SUPPORT, FILENAME_DICTIONARY)
        if not os.path.exists(filepath_dictionary): exit(f'🚨 The file \'{filepath_dictionary}\' does not exist')
        filepath_model = os.path.join(PATH_MODELS_SUPPORT, FILENAME_LSA)
        if not os.path.exists(filepath_model): exit(f'🚨 The file \'{filepath_model}\' does not exist')

        self.dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load(filepath_dictionary)
        self.model : gensim.models.LsiModel = gensim.models.LsiModel.load(filepath_model)

    def get_word_embedding(self, word: str) -> Optional[NDArray[np.float64]]:

        if word not in self.dictionary.token2id: return None
        word_id = self.dictionary.token2id[word]
        embedding = self.model.projection.u[word_id]

        return np.array(embedding, dtype=np.float64)