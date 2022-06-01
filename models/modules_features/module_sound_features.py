import os

import pandas   as pd

from typing     import List, Optional, Tuple

# Local Modules - Features
import modules_features.support.module_gemaps   as module_gemaps
# Local Modules - Auxiliary
import modules_aux.module_aux                   as module_aux
# Local Modules - Abstraction
import modules_abstraction.module_featureset    as module_featureset

# =================================== FEATURE SET DEFINITION ===================================

FEATURE_SET_ID : str = 'sound'
class SoundFeatureSet(module_featureset.FeatureSetAbstraction):

    def __init__(self) -> None:
        super().__init__(FEATURE_SET_ID)
        self.drop_columns = ['Audio Path', 'Audio File', 'Audio File Path']

    def _develop_basis_df(self):
        print(f"🚀 Preparing for '{self.id}' analysis ...")

        # Dataframe to study sound features
        basics_dataframe = self.paths_df.copy(deep=True)[['Subject', 'Task', 'Audio Path']]
        # Choose audio files from dictionary
        basics_dataframe['Audio File'] = basics_dataframe['Audio Path'].apply(module_aux.compute_file_paths, args=(self.preference_audio_tracks, None))
        basics_dataframe['Audio File Path'] = list(map(lambda items: os.path.join(items[0], items[1]), list(zip(basics_dataframe['Audio Path'], basics_dataframe['Audio File']))))

        # Save back 'basis dataframe' and 'drop_columns'
        self.basis_dataframe = basics_dataframe

    def _develop_static_df(self):
        static_dataframe = self.basis_dataframe.copy(deep=True)

        print(f"🚀 Developing '{self.id}' analysis ...")
        gemaps_extractor = module_gemaps.GeMAPSAnalyzer(module_gemaps.FeatureSet.eGeMAPSv02)
        static_dataframe = static_dataframe.merge(static_dataframe['Audio File Path']
            .progress_apply(lambda file: gemaps_extractor.process_file(file)), left_index=True, right_index=True)

        # Save back 'static dataframe'
        self.static_dataframe = static_dataframe
        print(f"✅ Finished processing '{self.id}' analysis!")
    
    def _develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        return (train_X, test_X)
