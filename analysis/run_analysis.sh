#!/bin/bash

CONTROL="../data/control_info.xlsx"
CONTROL_RECORDS="../data/recordings/controls/"
PSYCHOSIS="../data/psychosis_info.xlsx"
PSYCHOSIS_RECORDS="../data/recordings/psychosis/"

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
python3 ./pre-distribution.py -controls_data "${CONTROL}" -psychosis_data "${PSYCHOSIS}" -controls_rec "${CONTROL_RECORDS}" -psychosis_rec "${PSYCHOSIS_RECORDS}" -save "${OUTPUT_FILE}"
echo