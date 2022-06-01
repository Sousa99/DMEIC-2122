import os

import pandas   as pd

from functools  import reduce
from typing     import List, Optional, Tuple

# Local Modules - Features
import modules_features.support.module_entirety_roberta as module_entirety_roberta
# Local Modules - Auxiliary
import modules_aux.module_aux                           as module_aux
import modules_aux.module_nlp                           as module_nlp
import modules_aux.module_load                          as module_load
# Local Modules - Abstraction
import modules_abstraction.module_featureset            as module_featureset

# =================================== FEATURE SET DEFINITION ===================================

FEATURE_SET_ID : str = 'entirety'
class EntiretyFeatureSet(module_featureset.FeatureSetAbstraction):

    def __init__(self) -> None:
        super().__init__(FEATURE_SET_ID)
        self.drop_columns = ['Trans Path', 'Trans File', 'Trans File Path', 'Trans Info', 'Text']

    def _develop_basis_df(self):
        print(f"🚀 Preparing for '{self.id}' analysis ...")

        # Dataframe to study content features
        basics_dataframe = self.paths_df.copy(deep=True)[['Subject', 'Task', 'Trans Path']]
        # Choose trans files from dictionary
        basics_dataframe['Trans File'] = basics_dataframe['Trans Path'].apply(module_aux.compute_file_paths, args=(self.preference_trans, self.trans_extension))
        basics_dataframe = basics_dataframe.drop(basics_dataframe[basics_dataframe['Trans File'].isnull()].index)
        basics_dataframe['Trans File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(basics_dataframe['Trans Path'], basics_dataframe['Trans File']))))
        # Process Transcriptions
        basics_dataframe['Trans Info'] = basics_dataframe['Trans File Path'].apply(lambda file_path: module_load.TranscriptionInfo(file_path))
        basics_dataframe['Text'] = basics_dataframe['Trans Info'].apply(lambda trans_info: trans_info.get_words())

        # Save back 'basis dataframe' and 'drop_columns'
        self.basis_dataframe = basics_dataframe

    def _develop_static_df(self):
        static_dataframe = self.basis_dataframe.copy(deep=True)

        print(f"🚀 Developing '{self.id}' analysis ...")
        entirety_roberta_df = module_entirety_roberta.entirety_roberta_analysis(static_dataframe.copy(deep=True))

        # Final Dataframe
        all_content_dataframes : List[pd.DataFrame] = [entirety_roberta_df]
        static_dataframe = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), all_content_dataframes)
        
        # Save back 'static dataframe'
        self.static_dataframe = static_dataframe
        print(f"✅ Finished processing '{self.id}' analysis!")
    
    def _develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        
        def copy_optional_df(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
            if df is None: return None
            else: return df.copy(deep=True)

        # Feature models to use
        entirety_roberta_train_X, entirety_roberta_test_X   = module_entirety_roberta.entirety_roberta_analysis_dynamic(train_X.copy(deep=True), train_Y.copy(deep=True), copy_optional_df(test_X))

        # Final Dataframe
        all_content_train : List[pd.DataFrame] = [entirety_roberta_train_X]
        train_X = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), all_content_train)
        all_content_test : List[pd.DataFrame] = [entirety_roberta_test_X]
        test_X = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), all_content_test)

        return (train_X, test_X)