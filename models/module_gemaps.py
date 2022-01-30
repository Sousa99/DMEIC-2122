import os
import time

import numpy as np
import pandas as pd

import audb
import audiofile
import opensmile

from enum import Enum

# =================================== CLASS GEMAPS ANALYZER ===================================

class FeatureSet(Enum):
    eGeMAPSv02 = opensmile.FeatureSet.eGeMAPSv02

class GeMAPSAnalyzer():

    def __init__(self, featureSet: FeatureSet) -> None:
        self.smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.eGeMAPSv02,
            feature_level=opensmile.FeatureLevel.Functionals,
        )

    def process_file(self, file_path):
        signal, sampling_rate = audiofile.read(
            file_path,
            duration=None,
            always_2d=True,
        )

        output = self.smile.process_signal(signal, sampling_rate)
        return output.iloc[0]