import os
import tqdm
import gensim
import pprint
import load_corpus

from typing import Any, Dict, List, Optional

import seaborn as sns
import matplotlib.pyplot as plt

# =============================================== DEBUG CONSTANTS ================================================

NUMBER_DOCUMENTS : Optional[int] = 5000

# ================================================== CONSTANTS ===================================================

PATH_TO_DOCUMENTS : str = './exports/documents_clean/'
PATH_TO_DICTIONARY : str = './exports/corpora_dictionary.bin'

# ================================================== MAIN CODE ==================================================

if not os.path.exists(PATH_TO_DICTIONARY): exit(f'🚨 The file \'{PATH_TO_DICTIONARY}\' must exist')

dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load(PATH_TO_DICTIONARY)
corpus : load_corpus.LemmatizedCorpusNotLoaded = load_corpus.LemmatizedCorpusNotLoaded(PATH_TO_DOCUMENTS, NUMBER_DOCUMENTS, True)
bow_corpus : load_corpus.BOWCorpusNotLoaded = load_corpus.BOWCorpusNotLoaded(PATH_TO_DOCUMENTS, dictionary, NUMBER_DOCUMENTS, True)

model_list : List[Dict[str, Any]] = []
for num_topics in tqdm.trange(2500, min(NUMBER_DOCUMENTS, 625001), 2500, desc='🚀 Creating LDA models', leave=True):

    # Create LDA Model
    model = gensim.models.ldamulticore.LdaMulticore(bow_corpus, num_topics = num_topics, id2word = dictionary)
    # Create Coherence Model
    coherencemodel = gensim.models.CoherenceModel(model = model, texts = corpus, dictionary = dictionary, coherence='c_v')

    # Save Back Information
    model_information : Dict[str, Any] = { 'model': model, 'number_topics': num_topics, 'coherence_score': coherencemodel.get_coherence() }
    model_list.append(model_information)

plt.figure(figsize = (10, 4))
sns.lineplot(x = list(map(lambda elem: elem['number_topics'], model_list)), y = list(map(lambda elem: elem['coherence_score'], model_list)))
plt.xlabel("Number of Topics")
plt.ylabel("Coherence score")
plt.savefig('./exports/lda_topics_coherence.png')

best_model : Dict[str, Any] = max(model_list, key = lambda key: key['coherence_score'])
best_model['model'].save('./exports/lda_best_model.bin')

file = open('./exports/lda_best_model_topics.txt', 'wt')
pprint.pprint(best_model['model'].print_topics(num_words = 100), stream = file)
file.close()
