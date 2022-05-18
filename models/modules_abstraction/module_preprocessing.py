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
        return dataframe_X.dropna()

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



    