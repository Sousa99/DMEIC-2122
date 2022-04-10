#!/bin/bash
TEMP_CONDOR_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}"
TEMP_CONDOR_LOGS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/logs/"
TEMP_CONDOR_SCRIPTS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/scripts/"

CONDOR_PROCESSES_PER_OWNER="10000"

# Deal with Condor Directories
if [ ! -d "${TEMP_CONDOR_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_LOGS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_LOGS_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_SCRIPTS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_SCRIPTS_DIRECTORY}"; fi

echo "🚀 Running extract extractions ..."
extract_lines=( `grep -n "<ext" ./corpora/CETEMPublico/CETEMPublicoAnotado2019.txt | cut -f1 -d:` )
number_extracts=${#extract_lines[@]}

extracts_per_run=$(( ( ${number_extracts} + ${CONDOR_PROCESSES_PER_OWNER} - 1 ) / ${CONDOR_PROCESSES_PER_OWNER} ))

for ((extract_index = 0; extract_index < ${#extract_lines[@]} ; extract_index += ${extracts_per_run} )); do
    extract_line=${extract_lines[extract_index]}
    process_id=$(printf "extract_%05d" $extract_line)
    script_file="${TEMP_CONDOR_SCRIPTS_DIRECTORY}${process_id}.sh"

    echo "#!/bin/bash" > "${script_file}"
    echo "source ./venv/bin/activate"                                                   >> "${script_file}"
    echo "python3 ./extraction_dictionary.py -extracts_per_run ${extracts_per_run}  \\" >> "${script_file}"
    echo "    -parallelization_key extract -parallelization_index ${extract_line}"      >> "${script_file}"
    chmod a+x "${script_file}"

    # Fix Files for Condor Old Syntax
    output="${TEMP_CONDOR_LOGS_DIRECTORY}condor.out.${process_id}.log"
    error="${TEMP_CONDOR_LOGS_DIRECTORY}condor.err.${process_id}.log"
    log="${TEMP_CONDOR_DIRECTORY}extracts_condor.log"

    condor_submit \
            -a "Executable = ${script_file}"    \
            -a "Output = ${output}"             \
            -a "Error = ${error}"               \
            -a "Log = ${log}"                   \
            `pwd`/condor.config;
done

echo "🚀 Waiting for extractions to finish ..."
condor_wait "${TEMP_CONDOR_DIRECTORY}extracts_condor.log"

python3 extraction_dictionary.py -parallelization_key final
