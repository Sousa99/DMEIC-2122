import pandas as pd

from typing import List

# =================================== PRIVATE FUNCTIONS ===================================

# =================================== PUBLIC FUNCTIONS ===================================

def drop_rows_nan(dataframe: pd.DataFrame): return dataframe.dropna()

# =================================== PUBLIC CLASSES ===================================

class Preprocesser():

    def __init__(self, pipeline: List[str]):
        self.pipeline = pipeline

    def preprocess(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        
        current_dataframe = dataframe.copy(deep=True)
        for key in self.pipeline: current_dataframe = self.preprocess_stage(key, current_dataframe)
        return current_dataframe

    def preprocess_stage(self, key: str, dataframe: pd.DataFrame) -> pd.DataFrame:

        if key == 'DROP_ROWS_NAN': new_dataframe = drop_rows_nan(dataframe)
        else: exit("🚨 Preprocessing key '{0}' not recognized".format(key))

        return new_dataframe



    