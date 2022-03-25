#!/bin/bash

TRIBUS_LOC=/tmp/miamoto/tribus.sh

RECORDINGS_CONTROLS_PATH=../recordings/controls/
TRANSCRIBE_CONTROLS_PATH=../recordings_transcribed/controls/

RECORDINGS_PSYCHOSIS_PATH=../recordings/psychosis/
TRANSCRIBE_PSYCHOSIS_PATH=../recordings_transcribed/psychosis/

RECORDINGS_BIPOLARS_PATH=../recordings/bipolars/
TRANSCRIBE_BIPOLARS_PATH=../recordings_transcribed/bipolars/

prog() {
    local w=80 p=$1;  shift
    # create a string of spaces, then change them to dots
    printf -v dots "%*s" "$(( $p*$w/100 ))" ""; dots=${dots// /.};
    # print those dots on a fixed-width space plus the percentage etc.
    printf "\r\e[K|%-*s| %3d %% %s" "$w" "$dots" "$p" "$*";
}


if [ ! -d "$TRANSCRIBE_CONTROLS_PATH" ]; then mkdir $TRANSCRIBE_CONTROLS_PATH; fi

echo "🚀 Processing Controls ..."
CONTROLS=( $(ls ${RECORDINGS_CONTROLS_PATH}))
NUMBER_CONTROLS=${#CONTROLS[@]}
count=0
prog 0
for subject_folder in "${CONTROLS[@]}"; do
	
        for task_folder in `ls ${RECORDINGS_CONTROLS_PATH}${subject_folder}`; do
                        
                for file in `ls ${RECORDINGS_CONTROLS_PATH}${subject_folder}/${task_folder}`; do

			FILE_WITHOUT_EXT=$(echo "$file" | cut -f 1 -d '.')
                        if [ ! -d "${TRANSCRIBE_CONTROLS_PATH}data_tribus/${FILE_WITHOUT_EXT}" ]
		        then

				INPUT_FILE=${RECORDINGS_CONTROLS_PATH}${subject_folder}/${task_folder}/$file
                        	$TRIBUS_LOC --dir $TRANSCRIBE_CONTROLS_PATH $INPUT_FILE > /dev/null

			fi
                done
        done

	(( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_CONTROLS ))
        prog $current_prog
done
echo

if [ ! -d "$TRANSCRIBE_PSYCHOSIS_PATH" ]; then mkdir $TRANSCRIBE_PSYCHOSIS_PATH; fi

echo "🚀 Processing Psychosis ..."
PSYCHOSIS=( $(ls ${RECORDINGS_PSYCHOSIS_PATH}))
NUMBER_PSYCHOSIS=${#PSYCHOSIS[@]}
count=0
prog 0
for subject_folder in "${PSYCHOSIS[@]}"; do

        for task_folder in `ls ${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}`; do

                for file in `ls ${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}/${task_folder}`; do

			FILE_WITHOUT_EXT=$(echo "$file" | cut -f 1 -d '.')
                        if [ ! -d "${TRANSCRIBE_PSYCHOSIS_PATH}data_tribus/${FILE_WITHOUT_EXT}" ]
                        then

                                INPUT_FILE=${RECORDINGS_PSYCHOSIS_PATH}${subject_folder}/${task_folder}/$file
                                $TRIBUS_LOC --dir $TRANSCRIBE_PSYCHOSIS_PATH $INPUT_FILE > /dev/null

			fi
                done
        done

        (( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_PSYCHOSIS ))
        prog $current_prog
done
echo

if [ ! -d "$TRANSCRIBE_BIPOLARS_PATH" ]; then mkdir $TRANSCRIBE_BIPOLARS_PATH; fi

echo "🚀 Processing Bipolars ..."
BIPOLARS=( $(ls ${RECORDINGS_BIPOLARS_PATH}))
NUMBER_BIPOLARS=${#BIPOLARS[@]}
count=0
prog 0
for subject_folder in "${BIPOLARS[@]}"; do

        for task_folder in `ls ${RECORDINGS_BIPOLARS_PATH}${subject_folder}`; do

                for file in `ls ${RECORDINGS_BIPOLARS_PATH}${subject_folder}/${task_folder}`; do

                        FILE_WITHOUT_EXT=$(echo "$file" | cut -f 1 -d '.')
                        if [ ! -d "${TRANSCRIBE_BIPOLARS_PATH}data_tribus/${FILE_WITHOUT_EXT}" ]
                        then
			        
				INPUT_FILE=${RECORDINGS_BIPOLARS_PATH}${subject_folder}/${task_folder}/$file
                                $TRIBUS_LOC --dir $TRANSCRIBE_BIPOLARS_PATH $INPUT_FILE > /dev/null

			fi
                done
        done

        (( count++ ))
        current_prog=$(( $count * 100 / $NUMBER_BIPOLARS ))
        prog $current_prog
done
echo
