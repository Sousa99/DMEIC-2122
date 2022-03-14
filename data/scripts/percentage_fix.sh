#!/bin/bash

# Folder to specify
CONTROL_TRANSCRIPTIONS_PATH="../recordings_transcribed_results/controls/"
PSYCHOSIS_TRANSCRIPTIONS_PATH="../recordings_transcribed_results/psychosis/"
CONTROL_TRANSCRIPTIONS_FIX_PATH="../fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH="../fixed_transcriptions/psychosis/"

# Function to print percentage
prog() {
    local w=80 p=$1;  shift
    # create a string of spaces, then change them to dots
    printf -v dots "%*s" "$(( $p*$w/100 ))" ""; dots=${dots// /.};
    # print those dots on a fixed-width space plus the percentage etc.
    printf "\r\e[K|%-*s| %3d %% %s" "$w" "$dots" "$p" "$*";
}

if [ ! -d "${CONTROL_TRANSCRIPTIONS_FIX_PATH}" ]; then mkdir -p "${CONTROL_TRANSCRIPTIONS_FIX_PATH}"; fi

echo "🔎 Checking Controls ..."
CONTROLS=( $(ls ${CONTROL_TRANSCRIPTIONS_PATH}))
count_controls=0
count=0
for subject_folder in "${CONTROLS[@]}"; do
	subject_path="${CONTROL_TRANSCRIPTIONS_PATH}${subject_folder}/"

    for task_folder in `ls ${subject_path}`; do
        task_path="${subject_path}${task_folder}/"
        check_path_audio="${CONTROL_AUDIOS}${subject_folder}/${task_folder}/"
        check_path_trans="${CONTROL_TRANSCRIPTIONS_FIX_PATH}${subject_folder}/${task_folder}/"

        (( count_controls++ ))
        if [ -d "${check_path_trans}" ]; then
            (( count++ ))
        fi

    done

done
current_prog=$(( $count * 100 / $count_controls ))
prog $current_prog
echo "( ${count} out of ${count_controls} )"

if [ ! -d "${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}" ]; then mkdir -p "${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}"; fi

echo "🔎 Checking Psychosis ..."
PSYCHOSIS=( $(ls ${PSYCHOSIS_TRANSCRIPTIONS_PATH}))
count_psychosis=0
count=0
for subject_folder in "${PSYCHOSIS[@]}"; do
	subject_path="${PSYCHOSIS_TRANSCRIPTIONS_PATH}${subject_folder}/"

    for task_folder in `ls ${subject_path}`; do
        task_path="${subject_path}${task_folder}/"
        check_path_audio="${PSYCHOSIS_AUDIOS}${subject_folder}/${task_folder}/"
        check_path_trans="${PSYCHOSIS_TRANSCRIPTIONS_FIX_PATH}${subject_folder}/${task_folder}/"

        (( count_psychosis++ ))
        if [ -d "${check_path_trans}" ]; then
            (( count++ ))
        fi


    done

done
current_prog=$(( $count * 100 / $count_psychosis ))
prog $current_prog
echo "( ${count} out of ${count_psychosis} )"