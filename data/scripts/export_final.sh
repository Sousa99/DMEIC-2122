#!/bin/bash

NOW=$(date +"%Y.%m.%d %H.%M.%S")
EXPORT_DATA_OUTPUT_FILE="./exports/${NOW} - data.zip"
EXPORT_TRANSCRIBED_FIX_OUTPUT_FILE="./exports/${NOW} - transcribed fixed.zip"

# Files to compress
DATA_DIR="./recordings"
DATA_XLSX=("control_info.xlsx" "psychosis_info.xlsx" "bipolar_info.xlsx" "to_identify.xlsx")
TRANSCRIBED_FIX_DIR="./fixed_transcriptions"
cd ..

echo "📚 Compressing Data ..."
7z a -tzip "${EXPORT_DATA_OUTPUT_FILE}" $DATA_DIR ${DATA_XLSX[@]}
echo "📚 Compressing Transcribed Fixed ..."
7z a -tzip "${EXPORT_TRANSCRIBED_FIX_OUTPUT_FILE}" $TRANSCRIBED_FIX_DIR