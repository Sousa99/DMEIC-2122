import os
import tqdm
import gensim
import pickle
import random

from typing import Any, Dict, List

# ========================================== DEBUG CONSTANTS ==========================================

VECTOR_SIZE : int = 200
NUMBER_DOCUMENTS : int = 5000

# ========================================== DEFINITION OF ENUMERATORS ==========================================

if not os.path.exists('./exports/documents_clean/'): exit(f'🚨 The folder \'./exports/documents_clean/\' must exist')

documents_files : List[str] = os.listdir('./exports/documents_clean/')
documents_clean : List[List[str]] = []

documents_files_selected = random.sample(documents_files, NUMBER_DOCUMENTS)

for filename in tqdm.tqdm(documents_files_selected, desc='🚀 Reading Documents for Word2Vec Model', leave=True):
    file_path = os.path.join('./exports/documents_clean/', filename)
    if not os.path.isfile(file_path): continue

    file_save = open(file_path, 'rb')
    lemmatized_filtered : List[str] = pickle.load(file_save)
    file_save.close()
    
    documents_clean.append(lemmatized_filtered)

# Create FastText Model
model = gensim.models.FastText(sentences=documents_clean, vector_size=VECTOR_SIZE, window=5, min_count=1, workers=4)
model.save('./exports/fasttext_model.bin')
