#!/bin/bash
CURRENT_DIR=`pwd`
NOW=$(date +"%Y.%m.%d %H.%M.%S")

typeset -i WAIT_SECONDS=20
typeset -i MAX_JOBS_PER_MACHINE=3

CONTROL_INFO="../data/control_info.xlsx"
PSYCHOSIS_INFO="../data/psychosis_info.xlsx"
BIPOLAR_INFO="../data/bipolar_info.xlsx"

CONTROL_AUDIOS="../data/recordings_converted/controls/"
PSYCHOSIS_AUDIOS="../data/recordings_converted/psychosis/"
BIPOLAR_AUDIOS="../data/recordings_converted/bipolars/"

CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
BIPOLAR_TRANSCRIPTIONS="../data/fixed_transcriptions/bipolars/"

PARALLELIZATION_DIRECTORY="${CURRENT_DIR}/tmp_parallelization/${NOW}/scripts/"
mkdir -p "${PARALLELIZATION_DIRECTORY}"

VARIATION_KEY="simple"

python3 model_second.py                                                                                                                     \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \
    -parallelization_key="FEATURE_EXTRACTION"                                                                                               \
    -timestamp="${NOW}"                                                                                                                     \
    -variations_key=${VARIATION_KEY}

python3 ./parallelization.py -timestamp="${NOW}" -execution="init" -wait_seconds=${WAIT_SECONDS} -max_jobs_per_machine=${MAX_JOBS_PER_MACHINE}
ret=$?
if [ $ret -ne 0 ]; then exit; fi

echo
echo "🚀 Developing solution variations ..."
typeset -i number_of_variations=$(cat "./tmp/${NOW}/tmp_number_variations.txt")
for parallel_index in $(seq 0 $(expr $number_of_variations - 1)); do
    process_id=$(printf "second_variation_%05d" $parallel_index)
    script_file="${PARALLELIZATION_DIRECTORY}${process_id}.sh"

    echo "#!/bin/bash" > "${script_file}"
    echo "cd ${CURRENT_DIR}"                                                                                                                                >> "${script_file}"
    echo "source ./venv/bin/activate"                                                                                                                       >> "${script_file}"
    echo "python3 model_second.py		                                                                                                                \\" >> "${script_file}"
    echo "      -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \\" >> "${script_file}"
    echo "      -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \\" >> "${script_file}"
    echo "      -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \\" >> "${script_file}"
    echo "      -parallelization_key=\"RUN_MODELS\"         -parallelization_index=${parallel_index}                                                    \\" >> "${script_file}"
    echo "      -timestamp=\"${NOW}\"                                                                                                                   \\" >> "${script_file}"
    echo "      -variations_key=\"${VARIATION_KEY}\""                                                                                                       >> "${script_file}"                                                                                                                      >> "${script_file}"

    chmod a+x "${script_file}"
    python3 ./parallelization.py -timestamp="${NOW}" -execution="add" -execution_id="${process_id}" -execution_file="${script_file}"
	ret=$?
	if [ $ret -ne 0 ]; then exit; fi
done

python3 ./parallelization.py -timestamp="${NOW}" -execution="run"
ret=$?
if [ $ret -ne 0 ]; then exit; fi

python3 model_second.py                                                                                                                      \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \
    -parallelization_key="RUN_FINAL"                                                                                                        \
    -timestamp="${NOW}"                                                                                                                     \
    -variations_key=${VARIATION_KEY}
