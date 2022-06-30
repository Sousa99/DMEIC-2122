import os
import abc
import pickle
import warnings

from tqdm       import tqdm
from typing     import Callable, List, Optional, Set, Tuple
from functools  import reduce

import pandas   as pd

# Local Modules - Auxiliar
import modules_aux.module_aux                   as module_aux
import modules_aux.module_exporter              as module_exporter
# Local Modules - Abstraction
import modules_abstraction.module_variations    as module_variations

# =================================== PACKAGES PARAMETERS ===================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
warnings.filterwarnings('ignore', category = UserWarning, module = 'opensmile')
warnings.filterwarnings('ignore', category = pd.errors.PerformanceWarning)

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

    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id

    def init_execution(self, paths_df: pd.DataFrame, preference_audio_tracks: List[str], preference_trans: List[str], trans_extension: str,
        subject_info: pd.DataFrame, general_drop_columns: List[str], pivot_on_task: bool = False) -> None:

        self.paths_df                   = paths_df
        self.preference_audio_tracks    = preference_audio_tracks
        self.preference_trans           = preference_trans
        self.trans_extension            = trans_extension

        self.subject_info               = subject_info
        self.general_drop_columns       = general_drop_columns
        self.pivot_on_task              = pivot_on_task

    @abc.abstractmethod
    def _develop_basis_df(self):
        exit(f"🚨 Method '_develop_basis_df' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def _develop_static_df(self):
        exit(f"🚨 Method '_develop_static_df' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def _develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]: 
        exit(f"🚨 Method '_develop_dynamic_df' not defined for '{self.__class__.__name__}'")

    def develop_basis_df(self):

        filename_h5 : str = f'{self.id}.h5'
        filename_pkl : str = f'{self.id}.pkl'
        filename_parquet : str = f'{self.id}.parquet'

        # Get Dataframe - Pickle
        if self.basis_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['basis']), filename_pkl)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                file = open(load_path, 'rb')
                try: 
                    self.basis_dataframe = pickle.load(file)
                    print(f"✅ Loaded '{self.id}' basis dataframe from pickle checkpoint!")
                except: self.static_dataframe = None
                file.close()
        # Get Dataframe - Parquet
        if self.basis_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['basis']), filename_parquet)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    self.basis_dataframe = pd.read_parquet(load_path)
                    print(f"✅ Loaded '{self.id}' basis dataframe from parquet checkpoint!")
                except: self.basis_dataframe = None
        # Get Dataframe - H5
        if self.basis_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['basis']), filename_h5)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    self.basis_dataframe = pd.read_hdf(load_path, key='df', mode='r')
                    print(f"✅ Loaded '{self.id}' basis dataframe from h5 checkpoint!")
                except: self.basis_dataframe = None
        if self.basis_dataframe is None: self._develop_basis_df()

        print(f"ℹ️ Attempting to save basis '{self.id}' pickle checkpoint")

        # Save back dataframe
        save_path = os.path.join(module_exporter.get_checkpoint_save_directory(['basis']), filename_pkl)
        if not os.path.exists(save_path) or not os.path.isfile(save_path):
            file = open(save_path, 'wb')
            pickle.dump(self.basis_dataframe, file)
            file.close()

        print(f"ℹ️ Finished development of basis '{self.id}' dataframe")

    def develop_static_df(self):

        if self.basis_dataframe is None: self.develop_basis_df()
        filename_h5 : str = f'{self.id}.h5'
        filename_pkl : str = f'{self.id}.pkl'
        filename_parquet : str = f'{self.id}.parquet'

        # Get Dataframe - Pickle
        if self.static_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['static']), filename_pkl)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                file = open(load_path, 'rb')
                try: 
                    self.static_dataframe = pickle.load(file)
                    print(f"✅ Loaded '{self.id}' static dataframe from pickle checkpoint!")
                except: self.static_dataframme = None
                file.close()
        # Get Dataframe - Parquet
        if self.static_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['static']), filename_parquet)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    self.static_dataframe = pd.read_parquet(load_path)
                    print(f"✅ Loaded '{self.id}' static dataframe from parquet checkpoint!")
                except: self.static_dataframe = None
        # Get Dataframe - H5
        if self.static_dataframe is None:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['static']), filename_h5)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    self.static_dataframe = pd.read_hdf(load_path, key='df', mode='r')
                    print(f"✅ Loaded '{self.id}' static dataframe from h5 checkpoint!")
                except: self.static_dataframe = None
        if self.static_dataframe is None: self._develop_static_df()

        print(f"ℹ️ Attempting to save static '{self.id}' pickle checkpoint")
        
        # Save back dataframe
        save_path = os.path.join(module_exporter.get_checkpoint_save_directory(['static']), filename_pkl)
        if not os.path.exists(save_path) or not os.path.isfile(save_path):
            file = open(save_path, 'wb')
            pickle.dump(self.static_dataframe, file)
            file.close()

        print(f"ℹ️ Finished development of static '{self.id}' dataframe")

    def develop_dynamic_df(self, code: str, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:

        if self.basis_dataframe is None: self.develop_basis_df()
        if self.static_dataframe is None: self.develop_static_df()
        filename_h5 : str = f'{self.id}.h5'
        filename_pkl : str = f'{self.id}.pkl'
        filename_parquet_train : str = f'{self.id} - train.pkl'
        filename_parquet_test : str = f'{self.id} - test.pkl'

        loaded : bool = False

        dynamic_df_train    : pd.DataFrame
        dynamic_df_test     : Optional[pd.DataFrame] = None

        # Get Dataframe - Parquet
        if not loaded:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['dynamic']), filename_parquet_train)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    dynamic_df_train = pd.read_parquet(load_path)
                    loaded = True
                except: pass
        if loaded:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['dynamic']), filename_parquet_test)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    dynamic_df_test = pd.read_parquet(load_path)
                    print(f"✅ Loaded '{self.id}' dynamic with code '{code}' dataframe from parquet checkpoint!")
                except: loaded = False
            else: print(f"✅ Loaded '{self.id}' dynamic with code '{code}' dataframe from parquet checkpoint!")
        # Get Dataframe - H5
        if not loaded:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['dynamic']), filename_h5)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                try:
                    dynamic_df_train = pd.read_hdf(load_path, key='df_train', mode='r')
                    loaded = True
                    print(f"✅ Loaded '{self.id}' dynamic with code '{code}' dataframe from h5 checkpoint!")
                    dynamic_df_test = pd.read_hdf(load_path, key='df_test', mode='r')
                except: pass
        # Get Dataframe - Pickle
        if not loaded:
            load_path = os.path.join(module_exporter.get_checkpoint_load_directory(['dynamic']), filename_pkl)
            if os.path.exists(load_path) and os.path.isfile(load_path):
                file = open(load_path, 'rb')
                try: 
                    dynamic_df_train, dynamic_df_test = pickle.load(file)
                    loaded = True
                    print(f"✅ Loaded '{self.id}' dynamic with code '{code}' dataframe from pickle checkpoint!")
                finally: file.close()
        if not loaded: dynamic_df_train, dynamic_df_test = self._develop_dynamic_df(train_X, train_Y, test_X)

        # Save back dataframe
        save_path = os.path.join(module_exporter.get_checkpoint_save_directory(['dynamic']), filename_pkl)
        if not os.path.exists(save_path) or not os.path.isfile(save_path):
            file = open(save_path, 'wb')
            pickle.dump((dynamic_df_train, dynamic_df_test), file)
            file.close()

        return dynamic_df_train, dynamic_df_test
    
    def filter_rows(self, dataframe: pd.DataFrame, variation: module_variations.Variation) -> pd.DataFrame:
        dataframe_filtered = dataframe.copy()
        
        # Filter Dataframe by task
        dataframe_filtered = dataframe_filtered[dataframe_filtered['Task'].isin(variation.tasks)]
        # Filter Dataframe by gender
        filter_gender = dataframe_filtered['Subject'].apply(lambda subject: self.subject_info.loc[subject]['Gender'] in variation.genders)
        dataframe_filtered = dataframe_filtered[filter_gender.values]
        # Filter Dataframe by data variation
        filter_data = dataframe_filtered['Subject'].apply(lambda subject: self.subject_info.loc[subject]['Data Variation'] in variation.datas)
        dataframe_filtered = dataframe_filtered[filter_data.values]

        return dataframe_filtered

    def separate_target(self, dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]: 

        # Get final feature set (Dataframe X)
        dataframe_X = dataframe
        if self.pivot_on_task: dataframe_X = module_aux.pivot_on_column(dataframe_X, ['Subject'], 'Task', self.feature_columns, 'on')
        # Get final target class (Dataframe Y)
        dataframe_Y = dataframe_X.reset_index()['Subject'].apply(lambda subject: self.subject_info.loc[subject]['Target'])
        dataframe_Y.index = dataframe_X.index

        return (dataframe_X, dataframe_Y)

    def separate_train_test(self, indexes : Tuple[List[int], List[int]], dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series]]:
        
        train_index, test_index = indexes
        X_train, X_test = dataframe_X.iloc[train_index], dataframe_X.iloc[test_index]
        y_train, y_test = dataframe_Y.iloc[train_index], dataframe_Y.iloc[test_index]

        return ((X_train, y_train), (X_test, y_test))
    
    def get_df_for_classification(self, variation: module_variations.Variation, index_key: str, indexes: Tuple[List[int], List[int]]) -> Tuple[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series]]:

        if self.basis_dataframe is None: self.develop_basis_df()
        if self.static_dataframe is None: self.develop_static_df()
        current_df : pd.DataFrame = self.static_dataframe.copy(deep=True)

        current_df = self.filter_rows(current_df, variation)

        dataframe_X, dataframe_Y = self.separate_target(current_df)
        (train_X, train_Y), (test_X, test_Y) = self.separate_train_test(indexes, dataframe_X, dataframe_Y)
        train_X, test_X = self.develop_dynamic_df(f'{variation.generate_code_dataset()} - {index_key}', train_X, train_Y, test_X)

        train_X = train_X.drop(self.drop_columns, axis=1, errors='ignore')
        test_X = test_X.drop(self.drop_columns, axis=1, errors='ignore')
        if not self.pivot_on_task:
            train_X = train_X.drop(self.general_drop_columns, axis=1, errors='ignore')
            test_X = test_X.drop(self.general_drop_columns, axis=1, errors='ignore')

        train_X, train_Y = variation.preprocesser.preprocess_train(train_X, train_Y)
        test_X, test_Y = variation.preprocesser.preprocess_test(test_X, test_Y)

        return ((train_X, train_Y), (test_X, test_Y))

    def get_full_df(self, variation: Optional[module_variations.Variation] = None) -> Tuple[pd.DataFrame, pd.Series]:

        if self.basis_dataframe is None: self.develop_basis_df()
        if self.static_dataframe is None: self.develop_static_df()
        current_df : pd.DataFrame = self.static_dataframe.copy(deep=True)

        if variation is not None: current_df = self.filter_rows(current_df, variation)

        dataframe_X, dataframe_Y = self.separate_target(current_df)

        if variation is None: code = f'{self.id} - full'
        else: code = f'{variation.generate_code_dataset()} - full'

        dataframe_X, _ = self.develop_dynamic_df(code, dataframe_X, dataframe_Y)
        dataframe_X = dataframe_X.drop(self.drop_columns, axis=1, errors='ignore')
        if not self.pivot_on_task:
            dataframe_X = dataframe_X.drop(self.general_drop_columns, axis=1, errors='ignore')

        if variation is not None:
            dataframe_X, dataframe_Y = variation.preprocesser.preprocess_train(dataframe_X, dataframe_Y)
        
        return dataframe_X, dataframe_Y

class MergedFeatureSetAbstraction(FeatureSetAbstraction):

    def __init__(self, feature_sets: List[FeatureSetAbstraction]) -> None:
        super().__init__(' + '.join(map(lambda feature_set: feature_set.id, feature_sets)))
        self.feature_sets = feature_sets
    
    def _develop_basis_df(self):
        basis_dfs : List[pd.DataFrame] = []
        all_drop_columns : Set[str] = set()
        for feature_set in self.feature_sets:
            if feature_set.basis_dataframe is None:
                feature_set.develop_basis_df()
            basis_dfs.append(feature_set.basis_dataframe)
            all_drop_columns.update(feature_set.drop_columns)
        self.drop_columns = list(all_drop_columns)

        final_basis_df = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), basis_dfs)
        self.basis_dataframe = final_basis_df

    def _develop_static_df(self):
        static_dfs : List[pd.DataFrame] = []
        all_drop_columns : Set[str] = set()
        for feature_set in self.feature_sets:
            if feature_set.static_dataframe is None:
                feature_set.develop_static_df()
            static_dfs.append(feature_set.static_dataframe)
            all_drop_columns.update(feature_set.drop_columns)
        self.drop_columns = list(all_drop_columns)

        final_static_df = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), static_dfs)
        self.static_dataframe = final_static_df

    def _develop_dynamic_df(self, train_X: pd.DataFrame, train_Y: pd.Series, test_X: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        
        dynamic_dfs_train : List[pd.DataFrame] = []
        dynamic_dfs_test : List[pd.DataFrame] = []
        all_drop_columns : Set[str] = set()
        for feature_set in self.feature_sets:
            train_X, test_X = feature_set._develop_dynamic_df(train_X, train_Y, test_X)
            dynamic_dfs_train.append(train_X)
            if test_X is not None: dynamic_dfs_test.append(test_X)
            all_drop_columns.update(feature_set.drop_columns)
        self.drop_columns = list(all_drop_columns)

        final_dynamic_df_train = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), dynamic_dfs_train)
        if test_X is not None: final_dynamic_df_test = reduce(lambda dataset_left, dataset_right: module_aux.join_dataframes(dataset_left, dataset_right), dynamic_dfs_test)
        
        if test_X is None: return (final_dynamic_df_train, None)
        else: return (final_dynamic_df_train, final_dynamic_df_test)
