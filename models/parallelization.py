import os
import time
import threading
import subprocess

from io     import TextIOWrapper
from typing import Dict, List, Tuple

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

    TMP_DIRECTORY = './tmp_condor/'

    def __init__(self, machines : List[Machine], timestamp_id : str, wait_seconds : float, max_jobs_per_machine : float) -> None:
        self.machines               : List[Machine] = machines
        self.timestamp_id           : str           = timestamp_id
        self.wait_seconds           : float         = wait_seconds
        self.max_jobs_per_machine   : float         = max_jobs_per_machine

        # Scripts Management
        self.scripts_stack      : List[ExecutionScript]                 = []
        self.current_scripts    : Dict[Hostname, List[ExecutionScript]] = { (machine.get_hostname(), []) for machine in self.machines }
        self.concluded_scripts  : Dict[Hostname, List[ExecutionScript]] = { (machine.get_hostname(), []) for machine in self.machines }

    def add_script_to_queue(self, script_id : str, script_path : FilePath) -> None:
        execution_script = ExecutionScript(script_id, script_path)
        self.scripts_stack.append(execution_script)

    def machines_available(self) -> List[Machine]:
        available_machines  : List[Machine] = []
        for machine in self.machines:
            if len(self.current_scripts[machine.get_hostname()]) < self.max_jobs_per_machine:
                available_machines.append(machine)

        return available_machines

    def run(self) -> None:

        def get_filepaths(self : ParallelizationManager, process_id : str) -> Tuple[TextIOWrapper, TextIOWrapper]:
            log_path = os.path.join(self.TMP_DIRECTORY, self.timestamp_id)
            if not os.path.exists(log_path) or not os.path.isdir(log_path):
                os.makedirs(log_path)

            out_path = os.path.join(log_path, f'parallelization.err.{process_id}.log')
            err_path = os.path.join(log_path, f'parallelization.err.{process_id}.log')

            out_file = open(out_path, 'w')
            err_file = open(err_path, 'w')

            return (out_file, err_file)

        def run_process_in_thread(self : ParallelizationManager, on_exit_callback, execution_script : ExecutionScript, machine : Machine):
            command = f"ssh {machine.get_hostname()} {execution_script.get_file_path()}"
            out_file, err_file = get_filepaths(self, execution_script.get_execution_id())

            self.current_scripts[machine.get_hostname()].append(execution_script)
            proc = subprocess.Popen(command, stdout=out_file, stderr=err_file, shell=True, preexec_fn=os.setsid)

            proc.wait()
            out_file.close()
            err_file.close()
            on_exit_callback(self, execution_script, machine)
            return

        def on_process_exit(self : ParallelizationManager, execution_script : ExecutionScript, machine : Machine):

            current_scripts_machine = self.current_scripts[machine.get_hostname()]
            filtered_current_scripts = list(filter(lambda script_iter: script_iter.get_execution_id() != execution_script.get_execution_id(), current_scripts_machine))
            self.current_scripts = filtered_current_scripts

        # Submit jobs
        while len(self.scripts_stack) != 0:

            # Check for and get available machines
            available_machines = self.machines_available()
            if len(available_machines) == 0:
                time.sleep(self.wait_seconds)
                continue
            selected_machine : Machine = available_machines[0]

            # Execute script
            execution_script = self.scripts_stack.pop(0)
            thread = threading.Thread(target=run_process_in_thread, args=(on_process_exit, execution_script, selected_machine))
            thread.start()
            
    
