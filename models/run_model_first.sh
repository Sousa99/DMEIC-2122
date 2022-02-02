#!/bin/bash

CONTROL_INFO="../data/control_info.xlsx"
PSYCHOSIS_INFO="../data/psychosis_info.xlsx"
CONTROL_AUDIOS="../data/recordings_converted/controls_converted/"
PSYCHOSIS_AUDIOS="../data/recordings_converted/psychosis_converted/"
CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
CONTROL_TRANSCRIPTIONS="../data/recordings_transcribed_results/controls_transcribed_results/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
PSYCHOSIS_TRANSCRIPTIONS="../data/recordings_transcribed_results/psychosis_transcribed_results/"

python3 model_first.py -info_controls=${CONTROL_INFO} -info_psychosis=${PSYCHOSIS_INFO} -audio_controls=${CONTROL_AUDIOS} -audio_psychosis=${PSYCHOSIS_AUDIOS} -trans_controls=${CONTROL_TRANSCRIPTIONS} -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}