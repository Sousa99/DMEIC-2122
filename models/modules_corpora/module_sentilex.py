import os
import pickle

from typing import Dict, Optional

# =================================== CONSTANTS DEFINITIONS ===================================

PATH_MODELS_SUPPORT = '../models_support/exports/'

FILENAME_SENTILEX   = 'sentilex_model.pkl'

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class ModelSentiLex():

    def __init__(self) -> None:
        filepath_sentilex = os.path.join(PATH_MODELS_SUPPORT, FILENAME_SENTILEX)
        if not os.path.exists(filepath_sentilex): exit(f'🚨 The file \'{filepath_sentilex}\' does not exist')

        file_sentilex = open(filepath_sentilex, 'rb')
        self.model : Dict[str,int] = pickle.load(file_sentilex)
        file_sentilex.close()

    def word_in_model(self, word: str) -> bool:
        if word not in self.model: return False
        return True

    def get_word_valence(self, word: str) -> Optional[int]:

        if word not in self.model: return None
        return self.model[word]