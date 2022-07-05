import os
import pandas as pd

from typing import List

# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def pivot_on_column(data: pd.DataFrame, index: List[str], pivot_column: str, features: List[str], join_columns: str):

    data_pivot = data.pivot(index, pivot_column, features)
    data_pivot.columns =[' '.join([s1, join_columns, s2]) for (s1,s2) in data_pivot.columns.tolist()]
    data_pivot = data_pivot.reset_index()
    data_pivot = data_pivot.set_index(index)

    return data_pivot

def compute_file_paths(file_path: str, extension_preference_order: List[str], extension: str = None) -> str:

    _, _, files_full = list(os.walk(file_path))[0]
    if extension != None: files_full = list(filter(lambda file: os.path.splitext(file)[1] == extension, files_full))
    files = list(map(lambda file: (file, os.path.splitext(file)[0]), files_full))

    for prefered_extension in extension_preference_order:
        verifies_condition = list(filter(lambda file_info: file_info[1].endswith(prefered_extension), files))
        if len(verifies_condition) > 0: return verifies_condition[0][0]

    if len(files) == 0: return None
    return files[0][0]

def join_dataframes(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> pd.DataFrame:

    columns_1 = set(dataframe1.columns)
    columns_2 = set(dataframe2.columns)
    intersection_columns = columns_1.intersection(columns_2)
    dataframe2 = dataframe2.drop(intersection_columns, axis=1)

    joined_df = pd.merge(dataframe1, dataframe2, left_index=True, right_index=True, how='outer')
    joined_df = joined_df.drop(joined_df.filter(regex='_duplicate$').columns.tolist(), axis=1)
    return joined_df
