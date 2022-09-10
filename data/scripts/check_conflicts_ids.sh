#!/bin/bash

# Files to check
INFO_PATHS=(
    "../control_info.xlsx"
    "../psychosis_info.xlsx"
    "../bipolar_info.xlsx"
    "../to_identify_info.xlsx"
)

python3 ./check_ids.py -files ${INFO_PATHS[@]}