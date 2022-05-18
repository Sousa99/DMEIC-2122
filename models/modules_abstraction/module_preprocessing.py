import abc

import pandas as pd

from typing import List, Tuple

# =================================== PRIVATE CLASSES ===================================

class PreprocessingStage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fitting(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> None: exit("🚨 Method 'fitting' not defined")
    @abc.abstractmethod
    def transform(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]: exit("🚨 Method 'transform' not defined")

class PreprocessingDropRowsNan(PreprocessingStage):

    def __init__(self) -> None: return
    def fitting(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> None: return
    def transform(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        dataframe_X_nulls   : pd.Series = dataframe_X.isnull().any(axis='columns')
        dataframe_Y_nulls   : pd.Series = dataframe_Y.isnull()

        joined_nulls        : pd.Series = dataframe_X_nulls | dataframe_Y_nulls

        new_dataframe_X     : pd.DataFrame  =   dataframe_X.drop(dataframe_X[joined_nulls].index, inplace=False)
        new_dataframe_Y     : pd.Series     =   dataframe_Y.drop(dataframe_Y[joined_nulls].index, inplace=False)
        if joined_nulls.all():
            print(dataframe_X.iloc[0])
            print(dataframe_Y.iloc[0])
            exit("🚨 After dropping rows with nan's nothing is left!")
        return (new_dataframe_X, new_dataframe_Y)

# =================================== PRIVATE FUNCTIONS ===================================

def convert_key(key: str) -> PreprocessingStage:
    if key == 'DROP_ROWS_NAN': return PreprocessingDropRowsNan()
    else: exit("🚨 Preprocessing key '{0}' not recognized".format(key))

# =================================== PUBLIC FUNCTIONS ===================================

# =================================== PUBLIC CLASSES ===================================

class Preprocesser():

    pipeline : List[PreprocessingStage] = []
    def __init__(self, pipeline_stages: List[str]):
        for pipeline_key in pipeline_stages:
            self.pipeline.append(convert_key(pipeline_key))

    def preprocess_train(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        current_dataframe_X = dataframe_X.copy(deep=True)
        current_dataframe_Y = dataframe_Y.copy(deep=True)

        for stage in self.pipeline:
            stage.fitting(current_dataframe_X, current_dataframe_Y)
            current_dataframe_X, current_dataframe_Y = stage.transform(current_dataframe_X, current_dataframe_Y)

        return (current_dataframe_X, current_dataframe_Y)

    def preprocess_test(self, dataframe_X: pd.DataFrame, dataframe_Y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        current_dataframe_X = dataframe_X.copy(deep=True)
        current_dataframe_Y = dataframe_Y.copy(deep=True)

        for stage in self.pipeline:
            current_dataframe_X, current_dataframe_Y = stage.transform(current_dataframe_X, current_dataframe_Y)

        return (current_dataframe_X, current_dataframe_Y)



    
