import abc
import sys
import nltk
import stanza
import warnings

from typing         import List, Optional

if sys.version_info[0] == 3 and sys.version_info[1] >= 8: from numpy.typing   import NDArray
else: NDArray = np.ndarray

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

# =================================== PRIVATE FUNCTIONS ===================================

def average_embeddings(embeddings: List[NDArray[np.float64]]) -> NDArray[np.float64]:
    matrix_embeddings : NDArray[np.float64] = convert_embeddings_to_matrix(embeddings)
    avg_embedding : NDArray[np.float64] = np.mean(matrix_embeddings, axis=0)
    return avg_embedding

def normalize_embedding(embedding: NDArray[np.float64]) -> NDArray[np.float64]:
    embedding_norm : float = np.linalg.norm(embedding)
    return embedding / embedding_norm

def sum_normalize_embeddings(embeddings: List[NDArray[np.float64]]) -> NDArray[np.float64]:
    matrix_embeddings : NDArray[np.float64] = convert_embeddings_to_matrix(embeddings)
    sum_embedding : NDArray[np.float64] = np.sum(matrix_embeddings, axis=0)
    return normalize_embedding(sum_embedding)

# =================================== PUBLIC FUNCTIONS ===================================

def filter_out_stop_words(words: List[str]) -> List[str]:
    return list(filter(lambda word: word not in nltk.corpus.stopwords.words('portuguese'), words))

def subdivide_bags_of_words(words: List[str], words_per_bag: int) -> List[List[str]]:
    # Bag of Words Approach
    groups_of_words : List[List[str]] = [words[x : x + words_per_bag ] for x in range(0, len(words), words_per_bag)]
    return groups_of_words

def convert_word_to_embedding(word: str, model: module_gensim.ModelCorpora) -> Optional[NDArray[np.float64]]:
    embedding : Optional[NDArray[np.float64]] = model.get_word_embedding(word)
    if embedding is not None: embedding = normalize_embedding(embedding)
    return embedding

def convert_words_to_embeddings(group_of_words: List[str], model: module_gensim.ModelCorpora) -> List[NDArray[np.float64]]:
    embeddings : List[Optional[NDArray[np.float64]]] = list(map(lambda word: convert_word_to_embedding(word, model), group_of_words))
    embeddings_filtered : List[NDArray[np.float64]] = list(filter(lambda embedding: embedding is not None, embeddings))
    return embeddings_filtered

def convert_groups_of_words_to_embeddings(groups_of_words: List[List[str]], model: module_gensim.ModelCorpora) -> List[List[NDArray[np.float64]]]:
    embeddings_per_group : List[List[NDArray[np.float64]]] = list(map(lambda group_of_words: convert_words_to_embeddings(group_of_words, model), groups_of_words))
    embeddings_per_group_filtered : List[List[NDArray[np.float64]]] = list(filter(lambda group_of_embeddings: len(group_of_embeddings) != 0, embeddings_per_group))
    return embeddings_per_group_filtered

def convert_embeddings_to_matrix(group_of_embeddings: List[NDArray[np.float64]]) -> NDArray[np.float64]:
    return np.array(group_of_embeddings).astype(np.float64)

def convert_matrix_to_embeddings(embeddings_matrix: NDArray[np.float64]) -> List[NDArray[np.float64]]:
    list_elem   : List[List[float]] = embeddings_matrix.tolist()
    return list(map(lambda item: np.array(item).astype(np.float64), list_elem))

def average_embedding_per_group(groups_embeddings: List[List[NDArray[np.float64]]]) -> List[NDArray[np.float64]]:
    avg_embedding_per_group : List[NDArray[np.float64]] = list(map(lambda group_embeddings: average_embeddings(group_embeddings), groups_embeddings))
    return avg_embedding_per_group

def sum_normalize_embedding_per_group(groups_embeddings: List[List[NDArray[np.float64]]]) -> List[NDArray[np.float64]]:
    sum_norm_embedding_per_group : List[NDArray[np.float64]] = list(map(lambda group_embeddings: sum_normalize_embeddings(group_embeddings), groups_embeddings))
    return sum_norm_embedding_per_group

def embeddings_cossine_similarity(embedding_1: NDArray[np.float64], embedding_2: NDArray[np.float64]) -> float:
    dot_product : float = np.dot(embedding_1, embedding_2)
    normal_product : float = np.linalg.norm(embedding_1) * np.linalg.norm(embedding_2)
    return dot_product / normal_product

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
        