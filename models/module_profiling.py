import pandas as pd

from typing import Any, Dict, List

# Local Modules
import module_exporter

# =================================== EXECUTION CONSTANTS ===================================
DATASET_PROFILING_DIR = 'Dataset Profiling'

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class DatasetProfiling():

    def __init__(self, dataset_name: str, dataset_info: Dict[str, Any], general_drop_columns: List[str]) -> None:
        self.name : str = dataset_name;
        self.dataset : pd.DataFrame = dataset_info['features']
        self.drop_columns : List[str] = dataset_info['drop_columns']
        self.feature_columns : List[str] = dataset_info['feature_columns']
        self.general_drop_columns : List[str] = general_drop_columns
        # Correct Dataframe for Study
        self.features = self.dataset.copy(deep=True)
        self.features = self.features.drop(self.drop_columns + self.general_drop_columns, axis=1)

    def make_profiling(self) -> None:

        # Change to current directory
        module_exporter.change_current_sub_directory(DATASET_PROFILING_DIR)
        # Save dataset to be profiled
        save_file_dataset = self.generate_save_filename('dataset')
        module_exporter.export_csv(self.features, save_file_dataset)
        # Do profiling
        self.profile_dimensionality()

    def generate_save_filename(self, filename: str) -> str:
        return "{0} - {1}".format(self.name, filename)

    def profile_dimensionality(self) -> None:

        # Save File
        save_file_dimensionality = self.generate_save_filename('dimensionality')
        # Run Dimensionality Profiling
        bar_plots = { 'Nr Records': self.features.shape[0] , 'Nr Features': self.features.shape[1] }
        module_exporter.bar_chart(save_file_dimensionality, list(bar_plots.keys()), list(bar_plots.values()), figsize=(5, 4))


# =================================== PUBLIC METHODS ===================================