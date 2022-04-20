import os
import tqdm
import math
import gensim
import pprint
import load_corpus

from typing import Any, Dict, List, Optional

import seaborn as sns
import matplotlib.pyplot as plt

# =============================================== DEBUG CONSTANTS ================================================

NUMBER_DOCUMENTS : Optional[int] = 5000
MAX_USABLE_RAM_GB : float = 40.0
NUMBER_OF_TOPIC_VARIATIONS_TO_TEST : int = 20

# ================================================== CONSTANTS ===================================================

PATH_TO_DOCUMENTS : str = './exports/documents_clean/'
PATH_TO_DICTIONARY : str = './exports/corpora_dictionary.bin'

PATH_TO_LDA_MODELS_DIRECTORY : str = './exports/lda_variations/'
PATH_TO_LDA_MODELS_TOPIC_COHERENCE : str = './exports/lda_topics_coherence.png'
PATH_TO_LDA_BEST_MODEL : str = './exports/lda_best_model.bin'
PATH_TO_LDA_BEST_MODEL_TOPICS : str = './exports/lda_best_model_topics.txt'

# ================================================== AUXILIARY FUNCTIONS ==================================================

def compute_max_number_of_topics_possible(dictionary: gensim.corpora.Dictionary, usable_ram_gb: float) -> int:
    number_of_tokens : int = len(dictionary.keys())
    usable_ram_bytes = usable_ram_gb * pow(10, 9)
    number_of_topics_float : float = usable_ram_bytes / number_of_tokens / 8 / 3

    return math.floor(number_of_topics_float)

# ================================================== MAIN CODE ==================================================

if not os.path.exists(PATH_TO_DICTIONARY): exit(f'🚨 The file \'{PATH_TO_DICTIONARY}\' must exist')

dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load(PATH_TO_DICTIONARY)
corpus : load_corpus.LemmatizedCorpusNotLoaded = load_corpus.LemmatizedCorpusNotLoaded(PATH_TO_DOCUMENTS, NUMBER_DOCUMENTS, True)
bow_corpus : load_corpus.BOWCorpusNotLoaded = load_corpus.BOWCorpusNotLoaded(PATH_TO_DOCUMENTS, dictionary, NUMBER_DOCUMENTS, True)

num_topics_max : int = min(NUMBER_DOCUMENTS, compute_max_number_of_topics_possible(dictionary, MAX_USABLE_RAM_GB))
num_topics_step : int = math.floor(num_topics_max / NUMBER_OF_TOPIC_VARIATIONS_TO_TEST)

model_list : List[Dict[str, Any]] = []
for num_topics in tqdm.trange(num_topics_step, num_topics_max + 1, num_topics_step, desc='🚀 Creating LDA models', leave=True):

    # Create LDA Model
    model = gensim.models.ldamulticore.LdaMulticore(bow_corpus, num_topics = num_topics, id2word = dictionary)
    # Create Coherence Model
    coherencemodel = gensim.models.CoherenceModel(model = model, texts = corpus, dictionary = dictionary, coherence='c_v')

    # Save Back Information
    model_save_path : str = f'{PATH_TO_LDA_MODELS_DIRECTORY}lda_model_{str(num_topics)}.bin'
    model_information : Dict[str, Any] = { 'model_path': model_save_path, 'number_topics': num_topics, 'coherence_score': coherencemodel.get_coherence() }
    model_list.append(model_information)
    model.save(model_save_path)

    # Cleared variable for next iteration execution
    del model
    del coherencemodel

plt.figure(figsize = (10, 4))
sns.lineplot(x = list(map(lambda elem: elem['number_topics'], model_list)), y = list(map(lambda elem: elem['coherence_score'], model_list)))
plt.xlabel("Number of Topics")
plt.ylabel("Coherence score")
plt.savefig(PATH_TO_LDA_MODELS_TOPIC_COHERENCE)

best_model_entry : Dict[str, Any] = max(model_list, key = lambda key: key['coherence_score'])
best_model : gensim.models.ldamulticore.LdaMulticore = gensim.models.ldamulticore.LdaMulticore.load(best_model_entry['model_path'])
best_model.save(PATH_TO_LDA_BEST_MODEL)

file = open(PATH_TO_LDA_BEST_MODEL_TOPICS, 'wt')
pprint.pprint(best_model.print_topics(num_words = 100), stream = file)
file.close()
