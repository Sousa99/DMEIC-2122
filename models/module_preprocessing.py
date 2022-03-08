import abc

import pandas as pd

from typing import List

# =================================== PRIVATE CLASSES ===================================

class PreprocessingStage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fitting(self, dataframe: pd.DataFrame) -> None: raise("🚨 Method 'fitting' not defined")
    @abc.abstractmethod
    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame: raise("🚨 Method 'transform' not defined")

class PreprocessingDropRowsNan(PreprocessingStage):

    def __init__(self) -> None: return
    def fitting(self, dataframe: pd.DataFrame) -> None: return
    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.dropna()

# =================================== PRIVATE FUNCTIONS ===================================

def convert_key(key: str) -> PreprocessingStage:
    if key == 'DROP_ROWS_NAN': return PreprocessingDropRowsNan()
    else: raise("🚨 Preprocessing key '{0}' not recognized".format(key))

# =================================== PUBLIC FUNCTIONS ===================================

# =================================== PUBLIC CLASSES ===================================

class Preprocesser():

    pipeline : List[PreprocessingStage] = []
    def __init__(self, pipeline_stages: List[str]):
        for pipeline_key in pipeline_stages:
            self.pipeline.append(convert_key(pipeline_key))

    def preprocess_train(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        current_dataframe = dataframe.copy(deep=True)
        for stage in self.pipeline:
            stage.fitting(current_dataframe)
            current_dataframe = stage.transform(current_dataframe)

        return current_dataframe

    def preprocess_test(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        current_dataframe = dataframe.copy(deep=True)
        for stage in self.pipeline:
            current_dataframe = stage.transform(current_dataframe)

        return current_dataframe



    