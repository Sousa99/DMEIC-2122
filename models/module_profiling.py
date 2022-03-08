from numpy import save
import pandas as pd

from typing import Dict, List, Optional
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

    def __init__(self, dataframe_X: pd.DataFrame, dataframe_Y: Optional[pd.Series]) -> None:
        # Correct Dataframe for Study
        self.features = dataframe_X.copy(deep=True)
        self.target = None
        # Complete Dataframe with Features and Target
        self.complete = None

        if dataframe_Y is not None:
            self.target = dataframe_Y.copy(deep=True)
            self.target.index = self.features.index
            self.complete = self.features.copy(deep=True)
            self.complete['Target'] = self.target

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
        bar_plots = [ {'dimensionality': 'Nr Records', 'size': self.features.shape[0] },
            {'dimensionality': 'Nr Features', 'size': self.features.shape[1] } ]
        module_exporter.bar_chart('dimensionality', pd.DataFrame(bar_plots), 'dimensionality', 'size', figsize=(5, 4), x_label="Dimensionality", y_label="Size")

    def profile_missing_values(self) -> None:
        # Run Missing Values Profiling
        bar_plots = []
        for column in self.features:
            number_missing = self.features[column].isna().sum()
            if number_missing != 0: bar_plots.append({'variable': column, 'number': number_missing})
        
        if len(bar_plots) != 0:
            module_exporter.bar_chart('missing values', pd.DataFrame(bar_plots), 'variable', 'number', x_label="Variable", y_label="Count",
                figsize=(5 + len(bar_plots) / 3, 4), x_rot=25, margins={ 'bottom': 0.35, 'left': None, 'top': None, 'right': None })

    def profile_distribution(self) -> None:

        dataset_types = profile_for_types(self.features)

        # Run Distribution - Boxplots Profiling
        if len(dataset_types['Numeric']) != 0: module_exporter.boxplot_for_each('boxplots', self.features, dataset_types['Numeric'])
        if len(dataset_types['Numeric']) != 0 and self.complete is not None: module_exporter.boxplot_for_each('boxplots (target)', self.complete, dataset_types['Numeric'], hue='Target')
        # Run Distribution - Histogram (numeric) Profiling
        if len(dataset_types['Numeric']) != 0: module_exporter.histogram_for_each_numeric('histogram - numeric', self.features, dataset_types['Numeric'])
        if len(dataset_types['Numeric']) != 0 and self.complete is not None: module_exporter.histogram_for_each_numeric('histogram - numeric (target)', self.complete, dataset_types['Numeric'], hue='Target')
        # Run Distribution - Histogram (symbolic) Profiling
        if len(dataset_types['Symbolic']) != 0: module_exporter.histogram_for_each_symbolic('histogram - symbolic', self.features, dataset_types['Symbolic'])
        if len(dataset_types['Symbolic']) != 0 and self.complete is not None: module_exporter.histogram_for_each_symbolic('histogram - symbolic (target)', self.complete, dataset_types['Symbolic'], hue='Target')

    def profile_sparsity(self) -> None:

        dataset_types = profile_for_types(self.features)

        # Run Sparsity Plots
        variables = dataset_types['Binary'] + dataset_types['Numeric'] + dataset_types['Symbolic']
        # FIXME: Needs to be executed
        #module_exporter.dataframe_all_variables_sparsity('sparsity - plots', self.features, variables)
        #module_exporter.dataframe_all_variables_sparsity('sparsity - plots (target)', self.complete, variables, hue='Target')
        # Run Confusion Matrix
        correlation_matrix = abs(self.features.corr())
        module_exporter.heatmap('sparcity - correlation', correlation_matrix, x_ticklabels=correlation_matrix.columns,
        y_ticklabels=correlation_matrix.columns, margins={ 'bottom': 0.15, 'left': 0.17, 'top': 0.90, 'right': 0.95 })

# =================================== PUBLIC METHODS ===================================