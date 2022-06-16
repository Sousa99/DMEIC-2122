import gensim
import load_corpus

from typing import Optional, Union

# =============================================== DEBUG CONSTANTS ================================================

NUMBER_DOCUMENTS : Optional[Union[int, float]] = None

# ================================================== CONSTANTS ===================================================

VECTOR_SIZE         : int   = 200
PATH_TO_DOCUMENTS   : str   = '../exports/gensim/documents_clean/'
PATH_TO_MODEL       : str   = '../exports/gensim/fasttext_model.bin'

# ================================================== MAIN CODE ==================================================

corpus : load_corpus.LemmatizedCorpusNotLoaded = load_corpus.LemmatizedCorpusNotLoaded(PATH_TO_DOCUMENTS, NUMBER_DOCUMENTS, True)
# Create FastText Model
model = gensim.models.FastText(sentences=corpus, vector_size=VECTOR_SIZE, window=5, min_count=1, workers=4)
model.save(PATH_TO_MODEL)
