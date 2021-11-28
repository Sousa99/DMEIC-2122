#!/bin/bash

CONTROL="../data/control_info.xlsx"
PSYCHOSIS="../data/psychosis_info.xlsx"
CONTROL_RECORDS="../data/recordings/controls/"
PSYCHOSIS_RECORDS="../data/recordings/psychosis/"
CONTROL_TRANSCRIPTIONS="../data/recordings_transcribed_results/controls_transcribed_results/"
PSYCHOSIS_TRANSCRIPTIONS="../data/recordings_transcribed_results/psychosis_transcribed_results/"

NOW=$(date +"%Y.%m.%d %H.%M.%S")
DIR="./records/${NOW}/"
mkdir "$DIR"

# run completeness analysis
echo "📊 Completeness Analysis"
OUTPUT_FILE="$DIR${NOW} - completeness"
python3 ./completeness.py -save "${OUTPUT_FILE}" -controls_data "${CONTROL}" -psychosis_data "${PSYCHOSIS}"
echo

# run pre-distribution analysis
echo "📊 Pre Distribution Analysis"
OUTPUT_FILE="$DIR${NOW} - pre-distribution"
python3 ./pre-distribution.py -controls_data "${CONTROL}" -psychosis_data "${PSYCHOSIS}" -controls_rec "${CONTROL_RECORDS}" -psychosis_rec "${PSYCHOSIS_RECORDS}" -controls_trans "${CONTROL_TRANSCRIPTIONS}" -psychosis_trans "${PSYCHOSIS_TRANSCRIPTIONS}" -save "${OUTPUT_FILE}"
echo