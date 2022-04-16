import os
import tqdm
import gensim
import pprint
import pickle

from typing import Any, Dict, List

import seaborn as sns
import matplotlib.pyplot as plt

# ========================================== DEFINITION OF ENUMERATORS ==========================================

if not os.path.exists('./exports/documents_clean/'): exit(f'🚨 The folder \'./exports/documents_clean/\' must exist')
if not os.path.exists('./exports/corpora_dictionary.bin'): exit(f'🚨 The file \'./exports/corpora_dictionary.bin\' must exist')

dictionary : gensim.corpora.Dictionary = gensim.corpora.Dictionary.load('./exports/corpora_dictionary.bin')

model_list : List[Dict[str, Any]] = []
for num_topics in tqdm.trange(2500, 625001, 2500, desc='🚀 Creating LSA models', leave=True):

    # Create LSA Model
    model = gensim.models.LsiModel([], num_topics = num_topics, id2word = dictionary)
    coherencemodel = gensim.models.CoherenceModel(model = None, texts = [], dictionary = dictionary, coherence='c_v')
    # Update Models with every document
    for filename in tqdm.tqdm(os.listdir('./exports/documents_clean/'), desc='🚀 Reading Documents', leave=False):
        file_path = os.path.join('./exports/documents_clean/', filename)
        if not os.path.isfile(file_path): continue

        file_save = open(file_path, 'rb')
        lemmatized_filtered : List[str] = pickle.load(file_save)
        file_save.close()

        model.add_documents([dictionary.doc2bow(lemmatized_filtered)])
        coherencemodel.texts.append(lemmatized_filtered)
    coherencemodel.model = model

    # Save Back Information
    model_information : Dict[str, Any] = { 'model': model, 'number_topics': num_topics, 'coherence_score': coherencemodel.get_coherence() }
    model_list.append(model_information)

plt.figure(figsize = (10, 4))
sns.lineplot(x = list(map(lambda elem: elem['number_topics'], model_list)), y = list(map(lambda elem: elem['coherence_score'], model_list)))
plt.xlabel("Number of Topics")
plt.ylabel("Coherence score")
plt.savefig('./exports/lsa_topics_coherence.png')

best_model : Dict[str, Any] = max(model_list, key = lambda key: key['coherence_score'])
best_model['model'].save('./exports/lsa_best_model.bin')

file = open('./exports/lsa_best_model_topics.txt', 'wt')
pprint.pprint(best_model['model'].print_topics(num_words = 100), stream = file)
file.close()