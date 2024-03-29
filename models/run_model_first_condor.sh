#!/bin/bash
NOW=$(date +"%Y.%m.%d %H.%M.%S")
NOW_WITHOUT_SPACE=$(tr ' ' ':' <<< $NOW)

CONTROL_INFO="../data/control_info.xlsx"
PSYCHOSIS_INFO="../data/psychosis_info.xlsx"
BIPOLAR_INFO="../data/bipolar_info.xlsx"

CONTROL_AUDIOS="../data/recordings_converted/controls/"
PSYCHOSIS_AUDIOS="../data/recordings_converted/psychosis/"
BIPOLAR_AUDIOS="../data/recordings_converted/bipolars/"

CONTROL_TRANSCRIPTIONS="../data/fixed_transcriptions/controls/"
PSYCHOSIS_TRANSCRIPTIONS="../data/fixed_transcriptions/psychosis/"
BIPOLAR_TRANSCRIPTIONS="../data/fixed_transcriptions/bipolars/"

VARIATION_KEY="simple"

TEMP_CONDOR_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}"
TEMP_CONDOR_LOGS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/logs/"
TEMP_CONDOR_SCRIPTS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/scripts/"

python3 model_first.py                                                                                                                      \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \
    -parallelization_key="FEATURE_EXTRACTION"                                                                                               \
    -timestamp="${NOW}"                                                                                                                     \
    -variations_key=${VARIATION_KEY}

# Deal with Condor Directories
if [ ! -d "${TEMP_CONDOR_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_LOGS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_LOGS_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_SCRIPTS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_SCRIPTS_DIRECTORY}"; fi

echo
echo "🚀 Running solution variations ..."
typeset -i number_of_variations=$(cat "./tmp/${NOW}/tmp_number_variations.txt")
for parallel_index in $(seq 0 $(expr $number_of_variations - 1)); do
    process_id=$(printf "first_variation_%05d" $parallel_index)
    script_file="${TEMP_CONDOR_SCRIPTS_DIRECTORY}${process_id}.sh"

    echo "#!/bin/bash" > "${script_file}"
    echo "source ./venv/bin/activate"                                                                                                                       >> "${script_file}"
    echo "python3 model_first.py		                                                                                                                \\" >> "${script_file}"
    echo "      -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \\" >> "${script_file}"
    echo "      -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \\" >> "${script_file}"
    echo "      -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \\" >> "${script_file}"
    echo "      -parallelization_key=\"RUN_MODELS\"         -parallelization_index=${parallel_index}                                                    \\" >> "${script_file}"
    echo "      -timestamp=\"${NOW}\"                                                                                                                   \\" >> "${script_file}"
    echo "      -variations_key=\"${VARIATION_KEY}\""                                                                                                       >> "${script_file}"

    chmod a+x "${script_file}"

    # Fix Files for Condor Old Syntax
    output="${TEMP_CONDOR_LOGS_DIRECTORY}condor.out.${process_id}.log"
    error="${TEMP_CONDOR_LOGS_DIRECTORY}condor.err.${process_id}.log"
    log="${TEMP_CONDOR_DIRECTORY}/first_variations_condor.log"

    condor_submit \
            -a "Executable = ${script_file}"    \
            -a "Output = ${output}"             \
            -a "Error = ${error}"               \
            -a "Log = ${log}"                   \
            `pwd`/condor_cpu.config;
done

echo "🚀 Waiting for models to finish ..."
condor_wait "${TEMP_CONDOR_DIRECTORY}/first_variations_condor.log"

python3 model_first.py                                                                                                                      \
    -info_controls=${CONTROL_INFO}              -info_psychosis=${PSYCHOSIS_INFO}               -info_bipolars=${BIPOLAR_INFO}              \
    -audio_controls=${CONTROL_AUDIOS}           -audio_psychosis=${PSYCHOSIS_AUDIOS}            -audio_bipolars=${BIPOLAR_AUDIOS}           \
    -trans_controls=${CONTROL_TRANSCRIPTIONS}   -trans_psychosis=${PSYCHOSIS_TRANSCRIPTIONS}    -trans_bipolars=${BIPOLAR_TRANSCRIPTIONS}   \
    -parallelization_key="RUN_FINAL"                                                                                                        \
    -timestamp="${NOW}"                                                                                                                     \
    -variations_key=${VARIATION_KEY}
