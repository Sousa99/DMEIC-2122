#!/bin/bash
NOW=$(date +"%Y.%m.%d %H.%M.%S")

CONTROL_INFO="../data/control_info.xlsx"
PSYCHOSIS_INFO="../data/psychosis_info.xlsx"
CONTROL_AUDIOS="../data/recordings_converted/controls/"
PSYCHOSIS_AUDIOS="../data/recordings_converted/psychosis/"
CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
CONTROL_TRANSCRIPTIONS="../data/recordings_transcribed_results/controls/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
PSYCHOSIS_TRANSCRIPTIONS="../data/recordings_transcribed_results/psychosis/"

python3 model_first.py                                                                          \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    \
    -parallelization_key="FEATURE_EXTRACTION"                                                   \
    -timestamp="${NOW}"

echo
echo "🚀 Running solution variations ..."
typeset -i number_of_variations=$(cat "./tmp/${NOW}/tmp_number_variations.txt")
for parallel_index in $(seq 0 $(expr $number_of_variations - 1)); do
    python3 model_first.py                                                                          \
        -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               \
        -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            \
        -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    \
        -parallelization_key="RUN_MODELS"           -parallelization_index=${parallel_index}        \
        -timestamp="${NOW}"

done

python3 model_first.py                                                                          \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    \
    -parallelization_key="RUN_FINAL"                                                            \
    -timestamp="${NOW}"