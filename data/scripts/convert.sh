#!/bin/bash

RECORDINGS_CONTROLS_PATH=../recordings/controls/
CONVERSION_CONTROLS_PATH=../recordings_converted/controls/

RECORDINGS_PSYCHOSIS_PATH=../recordings/psychosis/
CONVERSION_PSYCHOSIS_PATH=../recordings_converted/psychosis/

RECORDINGS_BIPOLARS_PATH=../recordings/bipolars/
CONVERSION_BIPOLARS_PATH=../recordings_converted/bipolars/

# progress bar function
prog() {
    local w=80 p=$1;  shift
    # create a string of spaces, then change them to dots
    printf -v dots "%*s" "$(( $p*$w/100 ))" ""; dots=${dots// /.};
    # print those dots on a fixed-width space plus the percentage etc.
    printf "\r\e[K|%-*s| %3d %% %s" "$w" "$dots" "$p" "$*";
}

if [ ! -d "$CONVERSION_CONTROLS_PATH" ]; then mkdir $CONVERSION_CONTROLS_PATH; fi

echo "🚀 Processing Controls ..."
CONTROLS=( $(ls ${RECORDINGS_CONTROLS_PATH}))
NUMBER_CONTROLS=${#CONTROLS[@]}
count=0
prog 0
for subject_folder in "${CONTROLS[@]}"; do
	
        if [ ! -d "${CONVERSION_CONTROLS_PATH}${subject_folder}" ]
        then mkdir "${CONVERSION_CONTROLS_PATH}${subject_folder}/"
        fi

        for task_folder in `ls ${RECORDINGS_CONTROLS_PATH}${subject_folder}`; do

                if [ ! -d "${CONVERSION_CONTROLS_PATH}${subject_folder}/${task_folder}/" ]
                then
                
                        mkdir "${CONVERSION_CONTROLS_PATH}${subject_folder}/${task_folder}/"

                        for file in `ls ${RECORDINGS_CONTROLS_PATH}${subject_folder}/${task_folder}`; do

                                INPUT_FILE=${RECORDINGS_CONTROLS_PATH}${subject_folder}/${task_folder}/$file
                                OUTPUT_FILE=${CONVERSION_CONTROLS_PATH}${subject_folder}/${task_folder}/${file%.*}.wav

                                ffmpeg -hide_banner -loglevel error -i $INPUT_FILE $OUTPUT_FILE

                        done

                fi
        done

	(( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_CONTROLS ))
        prog $current_prog
done
echo

if [ ! -d "$CONVERSION_PSYCHOSIS_PATH" ]; then mkdir $CONVERSION_PSYCHOSIS_PATH; fi

echo "🚀 Processing Psychosis ..."
PSYCHOSIS=( $(ls ${RECORDINGS_PSYCHOSIS_PATH}))
NUMBER_PSYCHOSIS=${#PSYCHOSIS[@]}
count=0
prog 0
for subject_folder in "${PSYCHOSIS[@]}"; do

        if [ ! -d "${CONVERSION_PSYCHOSIS_PATH}${subject_folder}" ]
        then mkdir "${CONVERSION_PSYCHOSIS_PATH}${subject_folder}/"
        fi
        
        for task_folder in `ls ${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}`; do

                if [ ! -d "${CONVERSION_PSYCHOSIS_PATH}${subject_folder}/${task_folder}/" ]
                then

                        mkdir "${CONVERSION_PSYCHOSIS_PATH}${subject_folder}/${task_folder}/"

                        for file in `ls ${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}/${task_folder}`; do

                                INPUT_FILE=${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}/${task_folder}/$file
                                OUTPUT_FILE=${CONVERSION_PSYCHOSIS_PATH}${subject_folder}/${task_folder}/${file%.*}.wav

                                ffmpeg -hide_banner -loglevel error -i $INPUT_FILE $OUTPUT_FILE

                        done

                fi
        done

        (( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_PSYCHOSIS ))
        prog $current_prog
done
echo

if [ ! -d "$CONVERSION_BIPOLARS_PATH" ]; then mkdir $CONVERSION_BIPOLARS_PATH; fi

echo "🚀 Processing Bipolars ..."
BIPOLARS=( $(ls ${RECORDINGS_BIPOLARS_PATH}))
NUMBER_BIPOLARS=${#BIPOLARS[@]}
count=0
prog 0
for subject_folder in "${BIPOLARS[@]}"; do

        if [ ! -d "${CONVERSION_BIPOLARS_PATH}${subject_folder}" ]
        then mkdir "${CONVERSION_BIPOLARS_PATH}${subject_folder}/"
        fi

        for task_folder in `ls ${RECORDINGS_BIPOLARS_PATH}${subject_folder}`; do

                if [ ! -d "${CONVERSION_BIPOLARS_PATH}${subject_folder}/${task_folder}/" ]
                then
                        
                        mkdir "${CONVERSION_BIPOLARS_PATH}${subject_folder}/${task_folder}/"

                        for file in `ls ${RECORDINGS_BIPOLARS_PATH}${subject_folder}/${task_folder}`; do

                                INPUT_FILE=${RECORDINGS_BIPOLARS_PATH}${subject_folder}/${task_folder}/$file
                                OUTPUT_FILE=${CONVERSION_BIPOLARS_PATH}${subject_folder}/${task_folder}/${file%.*}.wav

                                ffmpeg -hide_banner -loglevel error -i $INPUT_FILE $OUTPUT_FILE

                        done
                
                fi
        done

        (( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_BIPOLARS ))
        prog $current_prog
done
echo
