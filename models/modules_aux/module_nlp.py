import abc
import nltk
import stanza
import warnings

from typing         import List, Optional
from numpy.typing   import NDArray

import numpy    as np

# Local Modules - Auxiliary
import modules_corpora.module_gensim    as module_gensim

# =================================== DOWNLOADS FOR LANGUAGE PROCESSING ===================================
'''
nltk.download('floresta')
nltk.download('punkt')
nltk.download('stopwords')
print()

stanza.download('pt')
print()
'''
# =================================== IGNORE CERTAIN ERRORS ===================================

warnings.filterwarnings('ignore', module = 'stanza')

# =================================== PUBLIC FUNCTIONS ===================================

def filter_out_stop_words(words: List[str]) -> List[str]:
    return list(filter(lambda word: word not in nltk.corpus.stopwords.words('portuguese'), words))

def subdivide_bags_of_words(words: List[str], words_per_bag: int) -> List[List[str]]:
    # Bag of Words Approach
    groups_of_words : List[List[str]] = [words[x : x + words_per_bag ] for x in range(0, len(words), words_per_bag)]
    return groups_of_words

def convert_words_to_embeddings(group_of_words: List[str], model: module_gensim.ModelCorpora) -> List[NDArray[np.float64]]:
    embeddings : List[Optional[NDArray[np.float64]]] = list(map(lambda word: model.get_word_embedding(word), group_of_words))
    embeddings_filtered : List[NDArray[np.float64]] = list(filter(lambda embedding: embedding is not None, embeddings))
    return embeddings_filtered

def convert_groups_of_words_to_embeddings(groups_of_words: List[List[str]], model: module_gensim.ModelCorpora) -> List[List[NDArray[np.float64]]]:
    embeddings_per_group : List[List[NDArray[np.float64]]] = list(map(lambda group_of_words: convert_words_to_embeddings(group_of_words, model), groups_of_words))
    embeddings_per_group_filtered : List[List[NDArray[np.float64]]] = list(filter(lambda group_of_embeddings: len(group_of_embeddings) != 0, embeddings_per_group))
    return embeddings_per_group_filtered

def average_embedding_per_group(groups_of_embeddings: List[List[NDArray[np.float64]]]) -> List[NDArray[np.float64]]:
    avg_embedding_per_group : List[NDArray[np.float64]] = list(map(lambda group_of_embedding: np.mean(np.array(group_of_embedding), axis=0), groups_of_embeddings))
    return avg_embedding_per_group

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Lemmatizer(abc.ABC):

    @abc.abstractmethod
    def __init__(self) -> None: super().__init__()
    @abc.abstractmethod
    def get_name(self) -> str: exit(f"🚨 Method 'get_name' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def process_words(self, words: List[str]) -> List[str]: exit(f"🚨 Method 'process_words' not defined for '{self.__class__.__name__}'")

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class LemmatizerStanza(Lemmatizer):

    pipeline = stanza.Pipeline('pt', verbose=False)

    def __init__(self) -> None: super().__init__()
    def get_name(self) -> str: return "Stanza"
    def process_words(self, words: List[str]) -> List[str]:
        words_as_string : str = ' '.join(words)
        processed = self.pipeline(words_as_string)
        return [ word.lemma for sentence in processed.sentences for word in sentence.words ]
        