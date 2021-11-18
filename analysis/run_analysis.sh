#!/bin/bash

CONTROL="control_info"
PSYCHOSIS="psychosis_info"

NOW=$(date +"%Y.%m.%d %H.%M.%S")

# run completeness analysis
CONTROL_OUTPUT_FILE="${NOW} - completeness - control"
PSYCHOSIS_OUTPUT_FILE="${NOW} - completeness - psychosis"
python3 ./completeness.py -save "${CONTROL_OUTPUT_FILE}" -data $CONTROL
python3 ./completeness.py -save "${PSYCHOSIS_OUTPUT_FILE}" -data $PSYCHOSIS -psychosis