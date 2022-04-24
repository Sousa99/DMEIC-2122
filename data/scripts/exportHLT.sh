#!/bin/bash

NOW=$(date +"%Y.%m.%d %H.%M.%S")
EXPORT_CONVERTED_OUTPUT_FILE="./exports/${NOW} - converted.zip"
EXPORT_TRANSCRIBED_OUTPUT_FILE="./exports/${NOW} - transcribed.zip"
EXPORT_TRANSCRIBED_RESULTS_OUTPUT_FILE="./exports/${NOW} - transcribed results.zip"

# Files to compress
RECORDINGS_CONVERTED_DIR="./recordings_converted"
RECORDINGS_TRANSCRIBED_DIR="./recordings_transcribed"
RECORDINGS_TRANSCRIBED_RESULTS_DIR="./recordings_transcribed_results"

cd ..

echo "📚 Compressing Converted ..."
7z a -tzip "${EXPORT_CONVERTED_OUTPUT_FILE}" $RECORDINGS_CONVERTED_DIR
#echo "📚 Compressing Transcribed ..."
#7z a -tzip "${EXPORT_TRANSCRIBED_OUTPUT_FILE}" $RECORDINGS_TRANSCRIBED_DIR
echo "📚 Compressing Transcriptions Results..."
7z a -tzip "${EXPORT_TRANSCRIBED_RESULTS_OUTPUT_FILE}" $RECORDINGS_TRANSCRIBED_RESULTS_DIR
