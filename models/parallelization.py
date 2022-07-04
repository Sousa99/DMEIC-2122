import os
import time
import pickle
import argparse
import warnings
import threading

from io     import TextIOWrapper
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm

warnings.filterwarnings(action='ignore', module='paramiko')
import paramiko

# =================================================== CONSTANTS DEFINITION ===================================================

TMP_DIRECTORY = './tmp_parallelization/'
LOGS_DIRECTORY = 'logs/'
FILE_SAVE_NAME = 'parallelization_manager.pkl'

load_dotenv()

SSH_USER = os.getenv('SSH_USER')
SSH_KEY = os.getenv('SSH_KEY')

if SSH_USER is None or SSH_KEY is None:
    exit("🚨 Please create a '.env' file with 'SSH_USER' and 'SSH_KEY' defined")

# =================================================== CLASSES DEFINITION ===================================================

Hostname = str
FilePath = str

class Machine():

    def __init__(self, hostname : Hostname, address : str) -> None:
        self.hostname   : Hostname  = hostname
        self.address    : str       = address

    def get_hostname(self) -> Hostname: return self.hostname
    def get_address(self) -> str: return self.address

class ExecutionScript():

    def __init__(self, execution_id : str, file_path : FilePath) -> None:
        self.execution_id   : str       = execution_id
        self.file_path      : FilePath  = file_path

    def get_execution_id(self) -> str: return self.execution_id
    def get_file_path(self) -> FilePath: return self.file_path

class ParallelizationManager():

    TMP_DIRECTORY = TMP_DIRECTORY
    FILE_SAVE_NAME = FILE_SAVE_NAME

    def __init__(self, machines : List[Machine], timestamp_id : str, wait_seconds : float, max_jobs_per_machine : float) -> None:
        self.machines               : List[Machine] = machines
        self.timestamp_id           : str           = timestamp_id
        self.wait_seconds           : float         = wait_seconds
        self.max_jobs_per_machine   : float         = max_jobs_per_machine

        # Scripts Management
        self.scripts_stack      : List[ExecutionScript]                 = []
        self.current_scripts    : Dict[Hostname, List[ExecutionScript]] = dict((machine.get_hostname(), []) for machine in self.machines)
        self.concluded_scripts  : Dict[Hostname, List[ExecutionScript]] = dict((machine.get_hostname(), []) for machine in self.machines)

        self.check_connectability()

    def add_script_to_queue(self, script_id : str, script_path : FilePath) -> None:
        if not os.path.exists(script_path) or not os.path.isfile(script_path):
            exit(f"🚨 File at '{script_path}' does not exist")
        execution_script = ExecutionScript(script_id, script_path)
        self.scripts_stack.append(execution_script)

    def machines_available(self) -> List[Machine]:
        available_machines  : List[Machine] = []
        for machine in self.machines:
            if len(self.current_scripts[machine.get_hostname()]) < self.max_jobs_per_machine:
                available_machines.append(machine)

        return available_machines

    def machines_unoccupied(self) -> List[Machine]:
        available_machines  : List[Machine] = []
        for machine in self.machines:
            if len(self.current_scripts[machine.get_hostname()]) == 0:
                available_machines.append(machine)

        return available_machines

    def check_connectability(self) -> None:

        for machine in self.machines:
            client = paramiko.SSHClient()
            client.load_system_host_keys()

            try:
                client.connect(machine.get_address(), username=SSH_USER, password=SSH_KEY)
                client.close()
            except: exit(f"🚨 Connectability could not be established with '{machine.get_address()}'")

    def run(self) -> None:

        def get_filepaths(self : ParallelizationManager, process_id : str) -> Tuple[TextIOWrapper, TextIOWrapper]:
            log_path = os.path.join(self.TMP_DIRECTORY, self.timestamp_id, LOGS_DIRECTORY)
            if not os.path.exists(log_path) or not os.path.isdir(log_path):
                os.makedirs(log_path, exist_ok=True)

            out_path = os.path.join(log_path, f'parallelization.out.{process_id}.log')
            err_path = os.path.join(log_path, f'parallelization.err.{process_id}.log')

            out_file = open(out_path, 'w')
            err_file = open(err_path, 'w')

            return (out_file, err_file)

        def run_process_in_thread(self : ParallelizationManager, on_exit_callback, execution_script : ExecutionScript, machine : Machine, tracker : Optional[tqdm] = None):

            current_scripts = self.current_scripts[machine.get_hostname()]
            current_scripts.append(execution_script)
            self.current_scripts[machine.get_hostname()] = current_scripts
            out_file, err_file = get_filepaths(self, execution_script.get_execution_id())

            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.connect(machine.get_address(), username=SSH_USER, password=SSH_KEY)
            _stdin, _stdout, _stderr = client.exec_command(f"\"{execution_script.get_file_path()}\"", get_pty=True)

            _stdout._set_mode('b')
            _stderr._set_mode('b')

            for line in iter(lambda: _stdout.readline(2048), ""):
                out_file.write(line.read().decode('utf-8', errors='ignore'))
                out_file.flush()
                os.fsync(out_file.fileno())

            out_file.write(_stdout.read().decode('utf-8', errors='ignore'))
            err_file.write(_stderr.read().decode('utf-8', errors='ignore'))

            out_file.close()
            err_file.close()
            
            client.close()
            on_exit_callback(self, execution_script, machine, tracker)
            return

        def on_process_exit(self : ParallelizationManager, execution_script : ExecutionScript, machine : Machine, tracker: Optional[tqdm] = None):

            current_scripts_machine = self.current_scripts[machine.get_hostname()]
            filtered_current_scripts = list(filter(lambda script_iter: script_iter.get_execution_id() != execution_script.get_execution_id(), current_scripts_machine))
            self.current_scripts[machine.get_hostname()] = filtered_current_scripts
            if tracker is not None: tracker.update(1)

        print("🚀 Started execution of scripts...")
        progress_tracker_submitted = tqdm(total=len(self.scripts_stack), desc="⚙️  Submiting execution scripts", leave=True, position=0)
        progress_tracker_completed = tqdm(total=len(self.scripts_stack), desc="⚙️  Completed execution scripts", leave=True, position=1)

        # Submit jobs
        while len(self.scripts_stack) != 0:

            # Check for and get available machines
            available_machines = self.machines_unoccupied()
            if len(available_machines) == 0:
                available_machines = self.machines_available()
            if len(available_machines) == 0:
                time.sleep(self.wait_seconds)
                continue
            selected_machine : Machine = available_machines[0]

            # Execute script
            execution_script = self.scripts_stack.pop(0)
            thread = threading.Thread(target=run_process_in_thread, args=(self, on_process_exit, execution_script, selected_machine, progress_tracker_completed))
            progress_tracker_submitted.update(1)
            thread.start()

        # Wait for remaining jobs to finish
        while len(self.machines_unoccupied()) != len(self.machines): time.sleep(self.wait_seconds)
        progress_tracker_submitted.close()
        progress_tracker_completed.close()
        print("🚀 Finished execution of scripts...")

    def save_model(self) -> None:

        path = os.path.join(self.TMP_DIRECTORY, self.timestamp_id)
        if not os.path.exists(path) or not os.path.isdir(path): os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, self.FILE_SAVE_NAME)
        file = open(file_path, 'wb')
        pickle.dump(self, file)
        file.close()

# =================================================== AUXILIARY FUNCTIONS ===================================================

def load_manager(timestamp_id : str) -> ParallelizationManager:
    file_path = os.path.join(TMP_DIRECTORY, timestamp_id, FILE_SAVE_NAME)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        exit(f"🚨 File '{file_path}' does not exist")
    
    file = open(file_path, 'rb')
    parallelization_manager : ParallelizationManager = pickle.load(file)
    file.close()

    return parallelization_manager

# ===================================================== MAIN EXECUTION =====================================================

INITIALIZE_OPTION = 'init'
ADD_EXECUTION_OPTION = 'add'
RUN_OPTION = 'run'
EXECUTION_OPTIONS = [INITIALIZE_OPTION, ADD_EXECUTION_OPTION, RUN_OPTION]

parser = argparse.ArgumentParser()
parser.add_argument("-timestamp", required=True,    type=str,   help="key (timestamp) to uniquely identify execution")
parser.add_argument("-execution", required=True,    type=str,   help="execution type", choices=EXECUTION_OPTIONS)
# In case 'INITIALIZE_OPTION'
parser.add_argument("-wait_seconds",                type=int,   help="number of seconds to wait until its check again for queue availability")
parser.add_argument("-max_jobs_per_machine",        type=int,   help="maximum number of jobs to submit to each machine")
# In case 'ADD_EXECUTION_SCRIPT_OPTION'
parser.add_argument("-execution_id",                type=str,   help="id for the execution")
parser.add_argument("-execution_file",              type=str,   help="path for the execution script")

arguments = parser.parse_args()
arguments_dict = vars(arguments)

# Check argument groups
requirements : List[str] = ['wait_seconds', 'max_jobs_per_machine']
if arguments_dict['execution'] == INITIALIZE_OPTION and any(map(lambda argument: arguments_dict[argument] is None, requirements)):
    exit(f"🚨 For execution mode '{arguments_dict['execution']}' the following is required: '{requirements}'")
requirements : List[str] = ['execution_id', 'execution_file']
if arguments_dict['execution'] == ADD_EXECUTION_OPTION and any(map(lambda argument: arguments_dict[argument] is None, requirements)):
    exit(f"🚨 For execution mode '{arguments_dict['execution']}' the following is required: '{requirements}'")

# Declare machines to use
machines_cpu = [ Machine('x01', 'x01'), Machine('x02', 'x02'), Machine('x03', 'x03'), Machine('x04', 'x04'),
    Machine('x05', 'x05'), Machine('x06', 'x06'), Machine('x07', 'x07'), Machine('x08', 'x08'),
    Machine('x09', 'x09'), Machine('x10', 'x10'), Machine('x11', 'x11'), Machine('x12', 'x12') ]

# Run main code - Init
if arguments_dict['execution'] == INITIALIZE_OPTION:
    parallelization_manager = ParallelizationManager(machines_cpu, arguments_dict['timestamp'],
        arguments_dict['wait_seconds'], arguments_dict['max_jobs_per_machine'])
    parallelization_manager.save_model()
# Run main code - Add
elif arguments_dict['execution'] == ADD_EXECUTION_OPTION:
    parallelization_manager = load_manager(arguments_dict['timestamp'])
    parallelization_manager.add_script_to_queue(arguments_dict['execution_id'], arguments_dict['execution_file'])
    parallelization_manager.save_model()
# Run main code - Run
elif arguments_dict['execution'] == RUN_OPTION:
    parallelization_manager = load_manager(arguments_dict['timestamp'])
    parallelization_manager.run()
