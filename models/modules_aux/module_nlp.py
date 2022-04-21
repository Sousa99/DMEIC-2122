import abc
import nltk
import stanza
import warnings

from typing import List

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
        