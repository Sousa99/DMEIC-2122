#!/bin/bash

# Folder to specify
CONTROL_TRANSCRIPTIONS_PATH="../recordings_transcribed/controls/"
PSYCHOSIS_TRANSCRIPTIONS_PATH="../recordings_transcribed/psychosis/"
BIPOLARS_TRANSCRIPTIONS_PATH="../recordings_transcribed/bipolars/"

TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/"
CONTROL_TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/controls/"
PSYCHOSIS_TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/psychosis/"
BIPOLARS_TRANSCRIPTIONS_RESULTS_PATH="../recordings_transcribed_results/bipolars/"

# Other important consts
TRIBUS_EXPORT_PATH="exp_tribus/"
TRIBUS_RESULT_PATH="result/transcription.trs"
TRIBUS_RESULT_CTM="/ctm"
TRIBUS_RESULT_PCTM="/pctm"

if [ ! -d "${TRANSCRIPTIONS_RESULTS_PATH}" ]; then mkdir "${TRANSCRIPTIONS_RESULTS_PATH}"; fi

echo "Extracting results from Controls ..."
for taskFolder in `ls ${CONTROL_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}`; do
	
	task_path="${CONTROL_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}${taskFolder}/"
	file_in_trans_path=${task_path}${TRIBUS_RESULT_PATH}
	file_in_ctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_CTM}
	file_in_pctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_PCTM}
	
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

	dir_out_path="${CONTROL_TRANSCRIPTIONS_RESULTS_PATH}${subject_folder}/${task_folder}/"
	file_out_trans_path="${dir_out_path}${taskFolder}.trs"
	file_out_ctm_path="${dir_out_path}${taskFolder}.ctm"
	file_out_pctm_path="${dir_out_path}${taskFolder}.pctm"

	#echo
	#echo "Subject Path: ${subject_folder}"
        #echo "Task Folder: ${task_folder}"
	#echo "File Out Path: ${file_out_path}"
        #echo "Filename: ${filename}"

	if [ ! -d "${dir_out_path}" ]; then mkdir -p "${dir_out_path}"; fi

        if [ ! -f "${file_out_trans_path}" ]; then cp ${file_in_trans_path} ${file_out_trans_path}; fi
        if [ ! -f "${file_out_ctm_path}" ]; then cp ${file_in_ctm_path} ${file_out_ctm_path}; fi
        if [ ! -f "${file_out_pctm_path}" ]; then cp ${file_in_pctm_path} ${file_out_pctm_path}; fi
done

echo "Extracting results from Psychosis ..."
for taskFolder in `ls ${PSYCHOSIS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}`; do

        task_path="${PSYCHOSIS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}${taskFolder}/"
        file_in_trans_path=${task_path}${TRIBUS_RESULT_PATH}
        file_in_ctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_CTM}
        file_in_pctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_PCTM}

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

        dir_out_path="${PSYCHOSIS_TRANSCRIPTIONS_RESULTS_PATH}${subject_folder}/${task_folder}/"
        file_out_trans_path="${dir_out_path}${taskFolder}.trs"
        file_out_ctm_path="${dir_out_path}${taskFolder}.ctm"
        file_out_pctm_path="${dir_out_path}${taskFolder}.pctm"

        #echo
        #echo "Subject Path: ${subject_folder}"
        #echo "Task Folder: ${task_folder}"
        #echo "File Out Path: ${file_out_path}"
        #echo "Filename: ${filename}"

        if [ ! -d "${dir_out_path}" ]; then mkdir -p "${dir_out_path}"; fi

        if [ ! -f "${file_out_trans_path}" ]; then cp ${file_in_trans_path} ${file_out_trans_path}; fi
        if [ ! -f "${file_out_ctm_path}" ]; then cp ${file_in_ctm_path} ${file_out_ctm_path}; fi
        if [ ! -f "${file_out_pctm_path}" ]; then cp ${file_in_pctm_path} ${file_out_pctm_path}; fi
done

echo "Extracting results from Bipolars ..."
for taskFolder in `ls ${BIPOLARS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}`; do

        task_path="${BIPOLARS_TRANSCRIPTIONS_PATH}${TRIBUS_EXPORT_PATH}${taskFolder}/"
        file_in_trans_path=${task_path}${TRIBUS_RESULT_PATH}
        file_in_ctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_CTM}
        file_in_pctm_path=${task_path}${taskFolder}${TRIBUS_RESULT_PCTM}

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

        dir_out_path="${BIPOLARS_TRANSCRIPTIONS_RESULTS_PATH}${subject_folder}/${task_folder}/"
        file_out_trans_path="${dir_out_path}${taskFolder}.trs"
        file_out_ctm_path="${dir_out_path}${taskFolder}.ctm"
        file_out_pctm_path="${dir_out_path}${taskFolder}.pctm"

        #echo
        #echo "Subject Path: ${subject_folder}"
        #echo "Task Folder: ${task_folder}"
        #echo "File Out Path: ${file_out_path}"
        #echo "Filename: ${filename}"

        if [ ! -d "${dir_out_path}" ]; then mkdir -p "${dir_out_path}"; fi

        if [ ! -f "${file_out_trans_path}" ]; then cp ${file_in_trans_path} ${file_out_trans_path}; fi
        if [ ! -f "${file_out_ctm_path}" ]; then cp ${file_in_ctm_path} ${file_out_ctm_path}; fi
        if [ ! -f "${file_out_pctm_path}" ]; then cp ${file_in_pctm_path} ${file_out_pctm_path}; fi
done
