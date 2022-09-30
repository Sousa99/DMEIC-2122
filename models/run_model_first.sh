#!/bin/bash

CONTROL_INFO="../data/control_info.xlsx"
PSYCHOSIS_INFO="../data/psychosis_info.xlsx"
BIPOLAR_INFO="../data/bipolar_info.xlsx"

CONTROL_AUDIOS="../data/recordings_converted/controls/"
PSYCHOSIS_AUDIOS="../data/recordings_converted/psychosis/"
BIPOLAR_AUDIOS="../data/recordings_converted/bipolars/"

CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
BIPOLAR_TRANSCRIPTIONS="../data/fixed_transcriptions/bipolars/"

VARIATION_KEY="second-detail"

python3 model_first.py -info_controls=${CONTROL_INFO} -info_psychosis=${PSYCHOSIS_INFO} -info_bipolars=${BIPOLAR_INFO} \
    -audio_controls=${CONTROL_AUDIOS} -audio_psychosis=${PSYCHOSIS_AUDIOS} -audio_bipolars=${BIPOLAR_AUDIOS} \
    -trans_controls=${CONTROL_TRANSCRIPTIONS} -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS} -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS} \
    -variations_key=${VARIATION_KEY}