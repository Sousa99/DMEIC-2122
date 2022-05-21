import gensim
import load_corpus

from typing import Optional

# =============================================== DEBUG CONSTANTS ================================================

NUMBER_DOCUMENTS : Optional[int] = 5000

# ================================================== CONSTANTS ===================================================

VECTOR_SIZE : int = 200
PATH_TO_DOCUMENTS : str = '../exports/documents_clean/'
PATH_TO_MODEL : str = '../exports/fasttext_model.bin'

# ================================================== MAIN CODE ==================================================

corpus : load_corpus.LemmatizedCorpusNotLoaded = load_corpus.LemmatizedCorpusNotLoaded(PATH_TO_DOCUMENTS, NUMBER_DOCUMENTS, True)
# Create FastText Model
model = gensim.models.FastText(sentences=corpus, vector_size=VECTOR_SIZE, window=5, min_count=1, workers=4)
model.save(PATH_TO_MODEL)
