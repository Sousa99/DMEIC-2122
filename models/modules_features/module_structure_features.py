import os

import pandas as pd

from typing import List, Optional, Tuple
from functools import reduce

# Local Modules - Features
import modules_features.support.module_lsa                  as module_lsa
import modules_features.support.module_word_graph           as module_word_graph
import modules_features.support.module_vector_unpacking     as module_vector_unpacking
# Local Modules - Auxiliary
import modules_aux.module_aux                               as module_aux
import modules_aux.module_nlp                               as module_nlp
import modules_aux.module_load                              as module_load
# Local Modules - Abstraction
import modules_abstraction.module_featureset                as module_featureset

# =================================== FEATURE SET DEFINITION ===================================

FEATURE_SET_ID : str = 'structure'
class StructureFeatureSet(module_featureset.FeatureSetAbstraction):

    def __init__(self) -> None:
        super().__init__(FEATURE_SET_ID)
        self.drop_columns = ['Trans Path', 'Trans File', 'Trans File Path', 'Trans Info', 'Lemmatized Text', 'Lemmatized Filtered Text',
            'Word Graph', 'Word Graph - WCC', 'Word Graph - SCC', 'Word Graph - LWCC', 'Word Graph - LSCC',
            'LSA - Word Groups', 'LSA - Embedding per Word Groups', 'LSA - Embedding Groups',
            'Vector Unpacking - Word Groups', 'Vector Unpacking - Embedding per Word Groups', 'Vector Unpacking - Embedding Groups']

    def _develop_basis_df(self):
        print(f"🚀 Preparing for '{self.id}' analysis ...")
        lemmatizer : module_nlp.LemmatizerStanza = module_nlp.LemmatizerStanza()

        # Dataframe to study structure features
        basics_dataframe = self.paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path']]
        # Choose trans files from dictionary
        basics_dataframe['Trans File'] = basics_dataframe['Trans Path'].apply(module_aux.compute_file_paths, args=(self.preference_trans, self.trans_extension))
        basics_dataframe = basics_dataframe.drop(basics_dataframe[basics_dataframe['Trans File'].isnull()].index)
        basics_dataframe['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(basics_dataframe['Trans Path'], basics_dataframe['Trans File']))))
        # Process Transcriptions
        basics_dataframe['Trans Info'] = basics_dataframe['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))
        basics_dataframe['Lemmatized Text'] = basics_dataframe['Trans Info'].apply(lambda trans_info: trans_info.lemmatize_words(lemmatizer))
        basics_dataframe['Lemmatized Filtered Text'] = basics_dataframe['Lemmatized Text'].apply(module_nlp.filter_out_stop_words)
        
        # Save back 'basis dataframe' and 'drop_columns'
        self.basis_dataframe = basics_dataframe
        del lemmatizer

    def _develop_static_df(self):
        static_dataframe = self.basis_dataframe.copy(deep=True)

        print(f"🚀 Developing '{self.id}' analysis ...")
        word_graph_df = module_word_graph.word_graph_analysis(static_dataframe.copy(deep=True))
        lsa_df = module_lsa.lsa_analysis(static_dataframe.copy(deep=True))
        vector_unpacking_df = module_vector_unpacking.vector_unpacking_analysis(static_dataframe.copy(deep=True))
        
        # Final Dataframe
        all_structure_dataframes : List[pd.DataFrame] = [word_graph_df, lsa_df, vector_unpacking_df]
        static_dataframe = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), all_structure_dataframes)
        
        # Save back 'static dataframe'
        self.static_dataframe = static_dataframe
        print(f"✅ Finished processing '{self.id}' analysis!")
    
    def _develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        return (train_X, test_X)
