import os
import abc
import pickle
import argparse
import warnings

from tqdm       import tqdm
from typing     import List, Optional, Tuple
from functools  import reduce

import pandas   as pd

# Local Modules - Auxiliar
import modules_aux.module_aux                   as module_aux
# Local Modules - Abstraction
import modules_abstraction.module_variations    as module_variations

# =================================== PACKAGES PARAMETERS ===================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', category = UserWarning, module = 'opensmile')

# =================================== CONSTANTS ===================================

# =================================== PRIVATE FUNCTIONS ===================================

# =================================== PUBLIC CLASSES ===================================

class FeatureSetAbstraction(abc.ABC):

    # =================================== PROPERTIES ===================================

    basis_dataframe         :   Optional[pd.DataFrame]  = None
    static_dataframe        :   Optional[pd.DataFrame]  = None
    feature_columns         :   List[str]               = []
    drop_columns            :   List[str]               = []

    # =================================== FUNCTIONS ===================================

    def __init__(self, id: str, paths_df: pd.DataFrame, preference_audio_tracks: List[str], preference_trans: List[str], trans_extension: str,
        subject_info: pd.DataFrame, general_drop_columns: List[str], pivot_on_task: bool = False) -> None:

        super().__init__()

        self.id                         = id

        self.paths_df                   = paths_df
        self.preference_audio_tracks    = preference_audio_tracks
        self.preference_trans           = preference_trans
        self.trans_extension            = trans_extension

        self.subject_info               = subject_info
        self.general_drop_columns       = general_drop_columns
        self.pivot_on_task              = pivot_on_task

    @abc.abstractmethod
    def develop_basis_df(self):
        exit(f"🚨 Method 'develop_basis_df' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def develop_static_df(self):
        exit(f"🚨 Method 'develop_static_df' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]: 
        exit(f"🚨 Method 'develop_dynamic_df' not defined for '{self.__class__.__name__}'")

    def filter_rows(self, dataframe: pd.DataFrame, variation: module_variations.Variation) -> pd.DataFrame:
        dataframe_filtered = dataframe.copy(deep=True)
        
        # Filter Dataframe by task
        dataframe_filtered = dataframe_filtered[dataframe_filtered['Task'].isin(variation.tasks)]
        # Filter Dataframe by gender
        filter_gender = dataframe_filtered['Subject'].apply(lambda subject: self.subject_info.loc[subject]['Gender'] in variation.genders)
        dataframe_filtered = dataframe_filtered[filter_gender.values]

        return dataframe_filtered

    def separate_target(self, dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]: 

        # Get final feature set (Dataframe X)
        dataframe_X = dataframe
        if self.pivot_on_task: dataframe_X = module_aux.pivot_on_column(dataframe_X, ['Subject'], 'Task', self.feature_columns, 'on')
        # Get final target class (Dataframe Y)
        dataframe_Y = dataframe_X.reset_index()['Subject'].apply(lambda subject: self.subject_info.loc[subject]['Target'])
        dataframe_Y.index = dataframe_X.index

        return (dataframe_X, dataframe_Y)

    def pre_process(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series, variation: module_variations.Variation) -> Tuple[pd.DataFrame, pd.Series]:
        dataframe_X = variation.preprocesser.preprocess_train(dataframe_X)
        dataframe_Y = variation.preprocesser.preprocess_test(dataframe_Y)

    def separate_train_test(self, indexes : Tuple[List[int], List[int]], dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series]]:
        
        train_index, test_index = indexes
        X_train, X_test = dataframe_X.iloc[train_index], dataframe_X.iloc[test_index]
        y_train, y_test = dataframe_Y.iloc[train_index], dataframe_Y.iloc[test_index]

        return ((X_train, y_train), (X_test, y_test))
    
    def get_df_for_classification(self, variation: module_variations.Variation = None, indexes: Optional[Tuple[List[int], List[int]]] = None) -> Tuple[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series]]:

        if self.basis_dataframe is None: self.develop_basis_df()
        if self.static_dataframe is None: self.develop_static_df()
        current_df : pd.DataFrame = self.static_dataframe.copy(deep=True)

        current_df = self.filter_rows(current_df, variation)
        current_df.drop(self.drop_columns)

        dataframe_X, dataframe_Y = self.separate_target(current_df)
        if not self.pivot_on_task: dataframe_X = dataframe_X.drop(self.general_drop_columns, axis=1)

        dataframe_X = variation.preprocesser.preprocess_train(dataframe_X)
        dataframe_Y = variation.preprocesser.preprocess_test(dataframe_Y)

        (train_X, train_Y), (test_X, test_Y) = self.separate_train_test(indexes, dataframe_X, dataframe_Y)

        train_X, test_X = self.develop_dynamic_df(train_X, train_Y, test_X)
        return ((train_X, train_Y), (test_X, test_Y))

    def get_full_df(self) -> Tuple[pd.DataFrame, pd.Series]:

        if self.basis_dataframe is None: self.develop_basis_df()
        if self.static_dataframe is None: self.develop_static_df()
        current_df : pd.DataFrame = self.static_dataframe.copy(deep=True)

        current_df.drop(self.drop_columns)
        dataframe_X, dataframe_Y = self.separate_target(current_df)
        if not self.pivot_on_task: dataframe_X = dataframe_X.drop(self.general_drop_columns, axis=1)

        train_X, test_X = self.develop_dynamic_df(dataframe_X, dataframe_Y)
        return train_X, test_X

class MergedFeatureSetAbstraction(FeatureSetAbstraction):

    def __init__(self, feature_sets: List[FeatureSetAbstraction]) -> None:
        super().__init__()

        self.feature_sets   = feature_sets
        self.id             = ' + '.join(map(lambda feature_set: feature_set.id, self.feature_sets))
    
    def develop_basis_df(self):
        for feature_set in self.feature_sets:
            feature_set.develop_basis_df()

    def develop_static_df(self):
        for feature_set in self.feature_sets:
            feature_set.develop_static_df()

    def develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        
        dynamic_dfs_train : List[pd.DataFrame] = []
        dynamic_dfs_test : List[pd.DataFrame] = []

        for feature_set in self.feature_sets:
            train_X, test_X = feature_set.develop_dynamic_df(train_X, train_Y, test_X)
            dynamic_dfs_train.append(train_X)
            if test_X is not None: dynamic_dfs_test.append(train_Y)

        final_dynamic_df_train = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), dynamic_dfs_train)
        if test_X is not None: final_dynamic_df_test = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), dynamic_dfs_test)
        
        if test_X is None: return (final_dynamic_df_train, None)
        else: return (final_dynamic_df_train, final_dynamic_df_test)