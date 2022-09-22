#!/bin/bash

CONTROL="../data/control_info.xlsx"
PSYCHOSIS="../data/psychosis_info.xlsx"
BIPOLARS="../data/bipolar_info.xlsx"

CONTROL_RECORDS="../data/recordings/controls/"
PSYCHOSIS_RECORDS="../data/recordings/psychosis/"
BIPOLARS_RECORDS="../data/recordings/bipolars/"

CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
BIPOLARS_TRANSCRIPTIONS="../data/fixed_transcriptions/bipolars/"

NOW=$(date +"%Y.%m.%d %H.%M.%S")
DIR="./records/${NOW}/"
mkdir "$DIR"

# run completeness analysis
echo "📊 Completeness Analysis"
OUTPUT_FILE="$DIR${NOW} - completeness"
python3 ./completeness.py -save "${OUTPUT_FILE}" \
    -controls_data "${CONTROL}" -psychosis_data "${PSYCHOSIS}" -bipolars_data "${BIPOLARS}"
echo

# run pre-distribution analysis
echo "📊 Pre Distribution Analysis"
OUTPUT_FILE="$DIR${NOW} - pre-distribution"
python3 ./pre-distribution.py -save "${OUTPUT_FILE}" \
    -controls_data "${CONTROL}" -psychosis_data "${PSYCHOSIS}" -bipolars_data "${BIPOLARS}" \
    -controls_rec "${CONTROL_RECORDS}" -psychosis_rec "${PSYCHOSIS_RECORDS}" -bipolars_rec "${BIPOLARS_RECORDS}" \
    -controls_trans "${CONTROL_TRANSCRIPTIONS}" -psychosis_trans "${PSYCHOSIS_TRANSCRIPTIONS}" -bipolars_trans "${BIPOLARS_TRANSCRIPTIONS}"
echo

# run microphone and fix analysis
echo "📊 Microphone and Fix Analysis"
OUTPUT_FILE="$DIR${NOW} - microphone and fix"
python3 ./microphone_differences.py -save "${OUTPUT_FILE}" \
    -controls_trans "${CONTROL_TRANSCRIPTIONS}" -psychosis_trans "${PSYCHOSIS_TRANSCRIPTIONS}" -bipolars_trans "${BIPOLARS_TRANSCRIPTIONS}"
echo