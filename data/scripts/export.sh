#!/bin/bash

NOW=$(date +"%Y.%m.%d %H.%M.%S")
EXPORT_OUTPUT_FILE="./exports/${NOW} - data.zip"

# Files to compress
RECORDINGS_DIR="./recordings"
INFO_PATHS=(
    "control_info.xlsx"
    "psychosis_info.xlsx"
    "bipolar_info.xlsx"
    "to_identify_info.xlsx"
)

cd ..
zip -r "${EXPORT_OUTPUT_FILE}" $RECORDINGS_DIR ${INFO_PATHS[@]}