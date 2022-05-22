import os
import tqdm
import pickle

from typing import Dict, List

# =============================================== DEBUG CONSTANTS ================================================

# ================================================== CONSTANTS ===================================================

PATH_TO_SENTILEX_INFLECTIONS    : str = '../corpora/SentiLex/SentiLex-flex-PT02.txt'
PATH_TO_SENTILEX_LEMMATIZED     : str = '../corpora/SentiLex/SentiLex-lem-PT02.txt'    
PATH_TO_SENTILEX_SELECTED       : str = PATH_TO_SENTILEX_LEMMATIZED

PATH_TO_EXPORT                  : str = '../exports/dictionaries/'
PATH_TO_EXPORT_SENTILEX_MODEL   : str = PATH_TO_EXPORT + 'sentilex_model.pkl'

# ================================================== AUXILIARY FUNCTIONS ==================================================

# ================================================== MAIN CODE ==================================================

if not os.path.exists(PATH_TO_SENTILEX_SELECTED): exit(f'🚨 The file \'{PATH_TO_SENTILEX_SELECTED}\' must exist')

# Open file with SentiLex Corpus
sentilex_file = open(PATH_TO_SENTILEX_SELECTED, 'r')

# Create mapping from the SentiLex file
mapping : Dict[str, int]    = {}
for line in tqdm.tqdm(sentilex_file.readlines(), desc='🚀 Creating SentiLex Mapping', leave=True):

    first_split : List[str] = line.strip().split('.')
    items       : List[str] = first_split[0].split(',')
    attributes  : List[str] = first_split[1].split(';')

    attributes_fixed : Dict[str, str] = dict(map(lambda item: (item.split('=')[0], item.split('=')[1]), attributes))

    if 'POL:N0' not in attributes_fixed: continue
    attribute_valence : int = int(attributes_fixed['POL:N0'])
    for item in items: mapping[item] = attribute_valence

# Close SentiLex Corpus file
sentilex_file.close()

# Save back mapping
if not os.path.exists(PATH_TO_EXPORT): os.makedirs(PATH_TO_EXPORT)
file = open(PATH_TO_EXPORT_SENTILEX_MODEL, 'wb')
pickle.dump(mapping, file)
file.close()
