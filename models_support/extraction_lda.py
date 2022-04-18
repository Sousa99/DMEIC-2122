import os
import tqdm
import gensim
import pprint
import pickle
import random

from typing import Any, Dict, List, Tuple

import seaborn as sns
import matplotlib.pyplot as plt

# ========================================== DEBUG CONSTANTS ==========================================

NUMBER_DOCUMENTS : float = 100000

# ========================================== DEFINITION OF ENUMERATORS ==========================================

if not os.path.exists('./exports/documents_clean/'): exit(f'🚨 The folder \'./exports/documents_clean/\' must exist')
if not os.path.exists('./exports/corpora_dictionary.bin'): exit(f'🚨 The file \'./exports/corpora_dictionary.bin\' must exist')

documents_files : List[str] = os.listdir('./exports/documents_clean/')
dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load('./exports/corpora_dictionary.bin')
documents_clean : List[List[str]] = []
corpus : List[List[Tuple[int, int]]] = []

documents_files_selected = random.sample(documents_files, NUMBER_DOCUMENTS)

for filename in tqdm.tqdm(documents_files_selected, desc='🚀 Reading Documents for LDA Model', leave=True):
    file_path = os.path.join('./exports/documents_clean/', filename)
    if not os.path.isfile(file_path): continue

    file_save = open(file_path, 'rb')
    lemmatized_filtered : List[str] = pickle.load(file_save)
    file_save.close()
    
    documents_clean.append(lemmatized_filtered)
    vector = dictionary.doc2bow(lemmatized_filtered)
    corpus.append(vector)

model_list : List[Dict[str, Any]] = []
for num_topics in tqdm.trange(2500, min(len(documents_clean, 625001)), 2500, desc='🚀 Creating LDA models', leave=True):

    # Create LDA Model
    model = gensim.models.ldamulticore.LdaMulticore(corpus, num_topics = num_topics, id2word = dictionary)
    # Create Coherence Model
    coherencemodel = gensim.models.CoherenceModel(model = model, texts = documents_clean, dictionary = dictionary, coherence='c_v')

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
