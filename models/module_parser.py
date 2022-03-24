import argparse
from typing import Dict

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-info_controls",   help="path to info file from controls")
parser.add_argument("-info_psychosis",  help="path to info file from psychosis")
parser.add_argument("-info_bipolars",   help="path to info file from bipolars")
parser.add_argument("-audio_controls",  help="path to audio segments from controls")
parser.add_argument("-audio_psychosis", help="path to audio segments from psychosis")
parser.add_argument("-audio_bipolars",  help="path to audio segments from bipolars")
parser.add_argument("-trans_controls",  help="path to transcription files from controls")
parser.add_argument("-trans_psychosis", help="path to transcription files from psychosis")
parser.add_argument("-trans_bipolars",  help="path to transcription files from bipolars")
# Define Optional Arguments
parser.add_argument("-variations_key",          help="key for the generation of variations, by default all are created")
parser.add_argument("-timestamp",               help="key for the timestamp identifier, if not given current timestamp is used")
parser.add_argument("-parallelization_key",     help="key for the parallelized model, if not given is executed sequentially")
parser.add_argument("-parallelization_index",   help="key index for the parallelized model, must be given if task is to be parallelized")

# Define Requirements
arguments_requirements = [
    { 'key': 'info_controls',       'help': 'path to info file from controls'},
    { 'key': 'info_psychosis',      'help': 'path to info file from psychosis'},
    { 'key': 'info_bipolars',       'help': 'path to info file from bipolars'},
    { 'key': 'audio_controls',      'help': 'path to audio segments from controls'},
    { 'key': 'audio_psychosis',     'help': 'path to audio segments from psychosis'},
    { 'key': 'audio_bipolars',      'help': 'path to audio segments from bipolars'},
    { 'key': 'trans_controls',      'help': 'path to transcriptions files from controls'},
    { 'key': 'trans_psychosis',     'help': 'path to transcriptions files from psychosis'},
    { 'key': 'trans_bipolars',      'help': 'path to transcriptions files from bipolars'},
]

# Get Arguments and Map to Requirements
arguments = parser.parse_args()
arguments_dict = vars(arguments)
for requirement in arguments_requirements:
    requirement['arg'] = arguments_dict[requirement['key']]

# Check Requirements
if ( any(not req['arg'] for req in arguments_requirements) ):
    print("🙏 Please provide a:")
    for requirement in arguments_requirements:
        print('\t\'{}\': {}'.format(requirement['key'], requirement['help']))
    exit(1)

def get_arguments() -> argparse.Namespace: return arguments