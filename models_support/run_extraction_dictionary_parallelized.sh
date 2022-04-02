#!/bin/bash
TEMP_CONDOR_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}"
TEMP_CONDOR_LOGS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/logs/"
TEMP_CONDOR_SCRIPTS_DIRECTORY="./tmp_condor/${NOW_WITHOUT_SPACE}/scripts/"

# Deal with Condor Directories
if [ ! -d "${TEMP_CONDOR_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_LOGS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_LOGS_DIRECTORY}"; fi
if [ ! -d "${TEMP_CONDOR_SCRIPTS_DIRECTORY}" ]; then mkdir -p "${TEMP_CONDOR_SCRIPTS_DIRECTORY}"; fi

echo "🚀 Running extract extractions ..."
extract_lines=( `grep -n "<ext" ./corpora/CETEMPublico/CETEMPublico1.7.txt | cut -f1 -d:` )
for extract_line in "${extract_lines[@]}"; do
    process_id=$(printf "extract_%05d" $extract_line)
    script_file="${TEMP_CONDOR_SCRIPTS_DIRECTORY}${process_id}.sh"

    echo "#!/bin/bash" > "${script_file}"
    echo "source ./venv/bin/activate"                                                                               >> "${script_file}"
    echo "python3 ./extraction_dictionary.py -parallelization_key extract -parallelization_index ${extract_line}"   >> "${script_file}"
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
condor_wait condor.log

python3 extraction_dictionary.py -parallelization_key final
