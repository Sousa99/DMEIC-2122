import argparse

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-json", help="filename of 'json' file")
parser.add_argument("-csv", help="filename of 'csv' file")
args = parser.parse_args()

if ( not args.json or not args.csv):
    print("🙏 Please provide a 'json' and 'csv' filename")
    exit(1)

# ========================= MAIN EXECUTION =========================

DATA_PATH = "../data/"
JSON_EXT = ".json"
CSV_EXT = ".csv"

CSV_SEPARATOR = ','

dataframe = pd.read_json(DATA_PATH + args.json + JSON_EXT, orient='index')
dataframe.to_csv(DATA_PATH + args.csv + CSV_EXT, sep = CSV_SEPARATOR)