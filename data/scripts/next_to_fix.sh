#!/bin/bash

# Folder to specify
CONTROL_TRANSCRIPTIONS_PATH="../recordings_transcribed_results/controls_transcribed_results/"
PSYCHOSIS_TRANSCRIPTIONS_PATH="../recordings_transcribed_results/psychosis_transcribed_results/"
CONTROL_TRANSCRIPTIONS_FIX_PATH="../fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH="../fixed_transcriptions/psychosis/"

if [ ! -d "${CONTROL_TRANSCRIPTIONS_FIX_PATH}" ]; then mkdir -p "${CONTROL_TRANSCRIPTIONS_FIX_PATH}"; fi

echo "Checking Controls ..."
for subject_folder in `ls ${CONTROL_TRANSCRIPTIONS_PATH}`; do
	subject_path="${CONTROL_TRANSCRIPTIONS_PATH}${subject_folder}/"

    for task_folder in `ls ${subject_path}`; do
        task_path="${subject_path}${task_folder}/"
        check_path="${CONTROL_TRANSCRIPTIONS_FIX_PATH}${subject_folder}/${task_folder}/"

        if [ ! -d "${check_path}" ]; then
            mkdir -p "${check_path}"
            cp -a "${task_path}/"*.ctm "${check_path}"
            echo "🖨️  Copied task '${task_folder}' of 'control' subject '${subject_folder}' ..."
            exit 0
        fi

    done

done

if [ ! -d "${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}" ]; then mkdir -p "${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}"; fi

echo "Checking Psychosis ..."
for subject_folder in `ls ${PSYCHOSIS_TRANSCRIPTIONS_PATH}`; do
	subject_path="${PSYCHOSIS_TRANSCRIPTIONS_PATH}${subject_folder}/"

    for task_folder in `ls ${subject_path}`; do
        task_path="${subject_path}${task_folder}/"
        check_path="${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}${subject_folder}/${task_folder}/"

        if [ ! -d "${check_path}" ]; then
            mkdir -p "${check_path}"
            cp -a "${task_path}/"*.ctm "${check_path}"
            echo "🖨️  Copied task '${task_folder}' of 'psychosis' subject '${subject_folder}' ..."
            exit 0
        fi

    done

done

echo "✔️  All transcriptions fixed!"