#!/bin/bash

CONTROL="control_info"
CONTROL_RECORDS="../data/recordings/controls/"
PSYCHOSIS="psychosis_info"
PSYCHOSIS_RECORDS="../data/recordings/psychosis/"

NOW=$(date +"%Y.%m.%d %H.%M.%S")

# run completeness analysis
echo "📊 Completeness Analysis"
CONTROL_OUTPUT_FILE="${NOW} - completeness - control"
PSYCHOSIS_OUTPUT_FILE="${NOW} - completeness - psychosis"
python3 ./completeness.py -save "${CONTROL_OUTPUT_FILE}" -data $CONTROL
python3 ./completeness.py -save "${PSYCHOSIS_OUTPUT_FILE}" -data $PSYCHOSIS -psychosis
echo

# run pre-distribution analysis
echo "📊 Pre Distribution Analysis"
OUTPUT_FILE="${NOW} - pre-distribution - "
python3 ./pre-distribution.py -controls "${CONTROL_RECORDS}" -psychosis "${PSYCHOSIS_RECORDS}" -save "${OUTPUT_FILE}"
echo