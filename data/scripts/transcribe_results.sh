#!/bin/bash

# Folder to specify
CONTROL_TRANSCRIPTIONS_PATH="../recordings_transcribed/controls_transcribed/"
PSYCHOSIS_TRANSCRIPTIONS_PATH="../recordings_transcribed/psychosis_transcribed/"
TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/"
CONTROL_TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/controls_transcribed_results/"
PSYCHOSIS_TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/psychosis_transcribed_results/"
# Other important consts
TRIBUS_EXPORT_PATH="exp_tribus/"
TRIBUS_RESULT_PATH="result/transcription.trs"


if [ -d "${TRANSCRIPTIONS_RESULTS_PATH}" ]; then rm -rf "${TRANSCRIPTIONS_RESULTS_PATH}"; fi

echo "Extracting results from Controls ..."
for taskFolder in `ls ${CONTROL_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}`; do
	
	task_path="${CONTROL_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}${taskFolder}/"
	file_in_path=${task_path}${TRIBUS_RESULT_PATH}
	
	#echo "Task Folder: ${taskFolder}"
	#echo "Task Path: ${task_path}"
	#echo "File In Path: ${file_in_path}"
	
	IFS='_' read -r -a splitTaskFolder <<< "$taskFolder"
	code=${splitTaskFolder[0]}
	subject=${splitTaskFolder[1]}
	task_number=${splitTaskFolder[2]}
	file_term=${splitTaskFolder[3]}

	subject_folder="${code}_${subject}"
	task_folder="${code}_${subject}_${task_number}"
	filename="${taskFolder}.trs"

	dir_out_path="${CONTROL_TRANSCRIPTIONS_RESULTS_PATH}${subject_folder}/${task_folder}/"
	file_out_path="${dir_out_path}${filename}"

	#echo
	#echo "Subject Path: ${subject_folder}"
        #echo "Task Folder: ${task_folder}"
	#echo "File Out Path: ${file_out_path}"
        #echo "Filename: ${filename}"

	if [ ! -d "${dir_out_path}" ]; then mkdir -p "${dir_out_path}"; fi
	cp ${file_in_path} ${file_out_path}
done

echo "Extracting results from Psychosis ..."
for taskFolder in `ls ${PSYCHOSIS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}`; do

        task_path="${PSYCHOSIS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}${taskFolder}/"
        file_in_path=${task_path}${TRIBUS_RESULT_PATH}

        #echo "Task Folder: ${taskFolder}"
        #echo "Task Path: ${task_path}"
        #echo "File In Path: ${file_in_path}"

        IFS='_' read -r -a splitTaskFolder <<< "$taskFolder"
        code=${splitTaskFolder[0]}
        subject=${splitTaskFolder[1]}
        task_number=${splitTaskFolder[2]}
        file_term=${splitTaskFolder[3]}

        subject_folder="${code}_${subject}"
        task_folder="${code}_${subject}_${task_number}"
        filename="${taskFolder}.trs"

        dir_out_path="${PSYCHOSIS_TRANSCRIPTIONS_RESULTS_PATH}${subject_folder}/${task_folder}/"
        file_out_path="${dir_out_path}${filename}"

        #echo
        #echo "Subject Path: ${subject_folder}"
        #echo "Task Folder: ${task_folder}"
        #echo "File Out Path: ${file_out_path}"
        #echo "Filename: ${filename}"

        if [ ! -d "${dir_out_path}" ]; then mkdir -p "${dir_out_path}"; fi
        cp ${file_in_path} ${file_out_path}
done
