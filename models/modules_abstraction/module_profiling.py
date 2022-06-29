from numpy import save
import pandas as pd

from typing import Dict, List, Optional
from pandas.api.types import is_numeric_dtype

# Local Modules - Auxiliary
import modules_aux.module_exporter  as module_exporter

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

    def __init__(self, dataframe_X: pd.DataFrame, dataframe_Y: Optional[pd.Series], fast: bool = False) -> None:
        # Correct Dataframe for Study
        self.features       : pd.DataFrame              = dataframe_X.copy()
        self.target         : Optional[pd.Series]       = None
        # Complete Dataframe with Features and Target
        self.complete       : Optional[pd.DataFrame]    = None
        # Other attributes
        self.fast_execution : bool                      = fast

        if dataframe_Y is not None:
            self.target = dataframe_Y.copy()
            self.target.index = self.features.index
            self.complete = self.features.copy()
            self.complete['Target'] = self.target

    def make_profiling(self) -> None:

        # Save dataset to be profiled
        module_exporter.export_csv(self.features, 'dataset')
        if self.complete is not None:
            module_exporter.export_csv(self.complete, 'dataset (target)')

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

        if not self.fast_execution:
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
        if not self.fast_execution:
            module_exporter.push_current_directory('Sparsity Graphs')
            variables = dataset_types['Binary'] + dataset_types['Numeric'] + dataset_types['Symbolic']
            module_exporter.dataframe_all_variables_sparsity_sep('sparsity - plots', self.features, variables)
            if self.complete is not None:
                module_exporter.dataframe_all_variables_sparsity_sep('sparsity - plots (target)', self.complete, variables, hue='Target')
            module_exporter.pop_current_directory()

        # Run Confusion Matrix
        if not self.fast_execution:
            correlation_matrix = abs(self.features.corr())
            module_exporter.heatmap('sparcity - correlation', correlation_matrix, x_ticklabels=correlation_matrix.columns,
                y_ticklabels=correlation_matrix.columns, margins={ 'bottom': 0.15, 'left': 0.17, 'top': 0.90, 'right': 0.95 })
            if self.complete is not None:
                correlation_matrix = abs(self.complete.corr())
                module_exporter.heatmap('sparcity - correlation (target)', correlation_matrix, x_ticklabels=correlation_matrix.columns,
                    y_ticklabels=correlation_matrix.columns, margins={ 'bottom': 0.15, 'left': 0.17, 'top': 0.90, 'right': 0.95 })


# =================================== PUBLIC METHODS ===================================