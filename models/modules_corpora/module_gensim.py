import os
import abc
import sys
import gensim

import numpy        as np

from typing         import Any, List, Optional

if sys.version_info[0] == 3 and sys.version_info[1] >= 8: from numpy.typing   import NDArray
else: NDArray = List

# =================================== CONSTANTS DEFINITIONS ===================================

PATH_MODELS_SUPPORT = '../models_support/exports/gensim/'

FILENAME_DICTIONARY = 'corpora_dictionary.bin'
FILENAME_WORD2VEC   = 'word2vec_model.bin'
FILENAME_LSA        = 'lsa_best_model.bin'

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class ModelCorpora(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def word_in_model(self, word: str) -> bool:
        pass
    @abc.abstractmethod
    def get_word_embedding(self, word: str) -> Optional[NDArray[np.float64]]:
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

    def word_in_model(self, word: str) -> bool:
        if word not in self.dictionary.token2id: return False
        word_id = self.dictionary.token2id[word]
        if word_id not in self.model.projection.u: return False
        return True

    def get_word_embedding(self, word: str) -> Optional[NDArray[np.float64]]:

        if word not in self.dictionary.token2id: return None
        word_id = self.dictionary.token2id[word]
        embedding = self.model.projection.u[word_id]

        return np.array(embedding, dtype=np.float64)

class ModelWord2Vec(ModelCorpora):

    def __init__(self) -> None:
        filepath_model = os.path.join(PATH_MODELS_SUPPORT, FILENAME_WORD2VEC)
        if not os.path.exists(filepath_model): exit(f'🚨 The file \'{filepath_model}\' does not exist')

        self.model : gensim.models.Word2Vec = gensim.models.Word2Vec.load(filepath_model)

    def word_in_model(self, word: str) -> bool:
        if word not in self.model.wv: return False
        return True

    def get_word_embedding(self, word: str) -> Optional[NDArray[np.float64]]:

        if word not in self.model.wv: return None
        embedding : NDArray[np.float32] = self.model.wv[word]

        return embedding.astype(np.float64)

    def get_vocab_size(self) -> int:
        return len(self.model.wv)

    def get_vocab_by_frequency(self) -> List[str]:
        return self.model.wv.index_to_key