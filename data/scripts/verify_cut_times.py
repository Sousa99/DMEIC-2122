import re
import os
import json
import math
import argparse

import pandas   as pd

from typing     import Any, Dict, List, Tuple, Union

# =================================== IGNORE CERTAIN ERRORS ===================================

# ======================================= FLAGS PARSING =======================================

parser = argparse.ArgumentParser()
parser.add_argument("-times", required=True, nargs='+', help="path to various curring times")
parser.add_argument("-old_format", action='store_true', default=False, help="path to various curring times")
args = parser.parse_args()

if (not args.times):
    print("🙏 Please provide at least one 'times' filepath")
    exit(1)

# =================================== CONSTANTS DEFINITIONS ===================================

GROUP_MAPPING : Dict[str, str] = {
    'b': {  'title': 'Bipolar',     'folder': 'bipolars'    },
    'c': {  'title': 'Control',     'folder': 'controls'    },
    'p': {  'title': 'Psychosis',   'folder': 'psychosis'   }
}

BLACKLISTED_ROWS : List[str] = ['template']
AUTO_INDENT_WORDS : List[Tuple[str, int]] = [ (' {', 1), ('"Task1"', 0), ('"Task2"', 0), ('"Task3"', 0), ('"Task4"', 0), ('"Task5"', 0), ('"Task6"', 0), ('"Task7"', 0), (' }', 1)]

# ===================================== CLASS DEFINITIONS =====================================

# ==================================== AUXILIARY FUNCTIONS ====================================

def read_cut_times(file_path: str, blacklist_rows: List[str]) -> pd.DataFrame:
    dataframe = pd.read_json(file_path, orient='index', precise_float=True)
    dataframe = dataframe.drop(blacklist_rows)

    return dataframe

def convert_df_old_format(old_df: pd.DataFrame) -> pd.DataFrame:
    def map_optional_list_to_mandatory(old_list: Union[str, List[float], List[List[float]]]) -> List[List[float]]:
        if isinstance(old_list, str) or (isinstance(old_list, list) and len(old_list) == 0): return [[]]
        elif isinstance(old_list[0], float): return [old_list]
        elif isinstance(old_list[0], int): return [ map(lambda elem: float(elem), old_list) ]
        else: return old_list

    def map_old_timestamp(old_ts: float) -> str:
        minutes = math.floor(old_ts / 1)
        seconds = round((old_ts - minutes) * 100)

        return f'{minutes}.{seconds:02}.000'

    def map_old_timeinterval(old_time_intervals: List[List[float]]) -> List[List[str]]:
        new_intervals : List[List[str]] = []
        for old_interval in old_time_intervals:
            new_interval = list(map(lambda timestamp: map_old_timestamp(timestamp), old_interval))
            new_intervals.append(new_interval)

        return new_intervals

    new_df = old_df.copy(deep=True)
    new_df = new_df.applymap(lambda cell: map_optional_list_to_mandatory(cell))
    new_df = new_df.applymap(lambda cell: map_old_timeinterval(cell))

    return new_df

def write_new_format(cut_times_df: pd.DataFrame, save_path: str, texts_to_ident: List[Tuple[str, int]]) -> None:
    result = cut_times_df.to_json(orient="index")
    parsed = json.loads(result)
    json_dumped = json.dumps(parsed, indent=4)

    json_dumped = re.sub('\s{8,}', ' ', json_dumped)
    json_dumped = re.sub('\[\s\[', '[[', json_dumped)
    json_dumped = re.sub('\]\s\]', ']]', json_dumped)
    json_dumped = re.sub('\s{5,}}', ' }', json_dumped)

    json_dumped_lines = json_dumped.split('\n')

    def space_text_to_common(text_indent: Tuple[str, int], lines: List[str], multiple: int) -> List[str]:
        max_index = 0
        for line in lines:
            index = line.find(text_indent[0])
            index_fixed = index + text_indent[1]
            if index != -1 and index_fixed > max_index: max_index = index_fixed
        index_indented = multiple * math.ceil(max_index / multiple)

        new_lines : List[str] = []
        for line in lines:
            current_index = line.find(text_indent[0])
            if current_index == -1:
                new_lines.append(line)
                continue

            current_index_fixed = current_index + text_indent[1]
            index_difference = index_indented - current_index_fixed
            
            line_start = line[:current_index_fixed]
            line_end = line[current_index_fixed:]
            extra_spaces = ''
            for _ in range(index_difference):
                extra_spaces = extra_spaces + ' '

            new_line = line_start + extra_spaces + line_end
            new_lines.append(new_line)

        return new_lines

    for text_to_ident in texts_to_ident:
        json_dumped_lines = space_text_to_common(text_to_ident, json_dumped_lines, 4)

    save_file = open(save_path, 'w')
    save_file.write('\n'.join(json_dumped_lines))
    save_file.close()

# ====================================== TESTS DEFINITION ======================================

# ===================================== MAIN FUNCTIONALITY =====================================

parsed_times : List[Any] = []
for cut_times_path in args.times:

    if not os.path.exists(cut_times_path) or not os.path.isfile(cut_times_path):
        raise Exception(f"🚨 Cut time path '{cut_times_path}' does not correspond to a valid file")
    print(f"🚀 Processing cut times file '{cut_times_path}' into dataframe")
    cut_times_pandas = read_cut_times(cut_times_path, [])

    if args.old_format:
        print(f"🚀 Converting cut times file '{cut_times_path}' into new format")
        cut_times_pandas = convert_df_old_format(cut_times_pandas)
        print(f"🚀 Saving cut times file '{cut_times_path}' in new format")
        write_new_format(cut_times_pandas, cut_times_path, AUTO_INDENT_WORDS)