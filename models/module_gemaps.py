import numpy as np
import pandas as pd

import audiofile
import opensmile

from enum import Enum, auto

# =================================== CLASS GEMAPS ANALYZER ===================================

class FeatureSet(Enum):
    eGeMAPSv02 = auto(),

class GeMAPSAnalyzer():

    def __init__(self, feature_set_enum: FeatureSet):

        feature_set = None
        if feature_set_enum == FeatureSet.eGeMAPSv02: feature_set = opensmile.FeatureSet.eGeMAPSv02

        if feature_set == None: exit("🚨  You should have specified a valid FeatureSet")

        self.smile = opensmile.Smile(
            feature_set=feature_set,
            feature_level=opensmile.FeatureLevel.Functionals,
        )

    def process_file(self, file_path: str) -> pd.Series:
        signal, sampling_rate = audiofile.read(
            file_path,
            duration=None,
            always_2d=True,
        )

        output = self.smile.process_signal(signal, sampling_rate)
        return output.iloc[0]