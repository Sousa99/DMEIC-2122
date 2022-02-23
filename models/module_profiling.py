from numpy import save
import pandas as pd

from typing import Any, Dict, List, Optional
from pandas.api.types import is_numeric_dtype

# Local Modules
import module_exporter

# =================================== PRIVATE METHODS ===================================

def profile_for_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    variable_types: Dict[str, List[str]] = {
        'Numeric': [],
        'Binary': [],
        'Date': [],
        'Symbolic': []
    }

    for column in df.columns:
        unique_values = df[column].dropna(inplace=False).unique()

        # Binary even if not automatically recognized
        if len(unique_values) == 2:
            variable_types['Binary'].append(column)
            df[column].astype('bool')
        # Dates / Times
        elif df[column].dtype == 'datetime64': variable_types['Date'].append(column)
        # Integers / Floats
        elif is_numeric_dtype(df[column]): variable_types['Numeric'].append(column)
        # Categorical / Symbolic
        else:
            df[column].astype('category')
            variable_types['Symbolic'].append(column)
        
    return variable_types

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DatasetProfiling():

    def __init__(self, dataset: pd.DataFrame, drop_columns: List[str], feature_columns: List[str], general_drop_columns: List[str]) -> None:
        self.dataset = dataset
        self.drop_columns = drop_columns
        self.feature_columns = feature_columns
        self.general_drop_columns : List[str] = general_drop_columns
        # Correct Dataframe for Study
        self.features = self.dataset.copy(deep=True)
        self.features = self.features.drop(self.drop_columns + self.general_drop_columns, axis=1)

    def make_profiling(self) -> None:

        # Save dataset to be profiled
        module_exporter.export_csv(self.features, 'dataset')
        # Do profiling
        self.profile_dimensionality()
        self.profile_missing_values()
        self.profile_distribution()
        self.profile_sparsity()

    def profile_dimensionality(self) -> None:
        # Run Dimensionality Profiling
        bar_plots = { 'Nr Records': self.features.shape[0] , 'Nr Features': self.features.shape[1] }
        module_exporter.bar_chart('dimensionality', list(bar_plots.keys()), list(bar_plots.values()), figsize=(5, 4))

    def profile_missing_values(self) -> None:
        # Run Missing Values Profiling
        bar_plots = {}
        for column in self.features:
            number_missing = self.features[column].isna().sum()
            if number_missing != 0: bar_plots[column] = number_missing
        
        if len(bar_plots) != 0:
            module_exporter.bar_chart('missing values', list(bar_plots.keys()), list(bar_plots.values()),
                figsize=(5 + len(bar_plots) / 3, 4), x_rot=25, margins={ 'bottom': 0.35, 'left': None, 'top': None, 'right': None })

    def profile_distribution(self) -> None:

        dataset_types = profile_for_types(self.features)

        # Run Distribution - Boxplots Profiling
        values = {}
        for numeric_feature in dataset_types['Numeric']:
            values[numeric_feature] = self.features[numeric_feature].dropna().values
        if len(values) != 0: module_exporter.boxplot_for_each('boxplots', values)
        # Run Distribution - Histogram (numeric) Profiling
        values = {}
        for numeric_feature in dataset_types['Numeric']:
            values[numeric_feature] = self.features[numeric_feature].dropna().values
        if len(values) != 0: module_exporter.histogram_for_each_numeric('histogram - numeric', values)
        # Run Distribution - Histogram (symbolic) Profiling
        values = {}
        for symbolic_feature in dataset_types['Symbolic']:
            values[symbolic_feature] = self.features[symbolic_feature].dropna().value_counts().to_dict()
        if len(values) != 0: module_exporter.histogram_for_each_symbolic('histogram - symbolic', values)

    def profile_sparsity(self) -> None:

        dataset_types = profile_for_types(self.features)

        # Run Sparsity Plots
        variables = dataset_types['Binary'] + dataset_types['Numeric'] + dataset_types['Symbolic']
        # FIXME: Needs to be executed
        #module_exporter.dataframe_all_variables_sparsity('sparsity - plots', self.features, variables)
        # Run Confusion Matrix
        correlation_matrix = abs(self.features.corr())
        module_exporter.heatmap('sparcity - correlation', correlation_matrix, x_ticklabels=correlation_matrix.columns,
        y_ticklabels=correlation_matrix.columns, margins={ 'bottom': 0.15, 'left': 0.17, 'top': 0.90, 'right': 0.95 })

# =================================== PUBLIC METHODS ===================================