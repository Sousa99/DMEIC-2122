from numpy import save
import pandas as pd

from typing import Any, Dict, List, Optional

# Local Modules
import module_exporter

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


# =================================== PUBLIC METHODS ===================================