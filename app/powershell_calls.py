from datetime import datetime, timedelta
import os
import sys
import subprocess
import typing as ty

from utils import Event, Inputs

from datetime import datetime, timedelta
import pytz



def call_powershell_script(day: str, event_start: str, event_stop: str, event_timezone: str, command: str) -> str | None:
    windows_destination_folder = os.getenv("WINDOWS_DESTINATION_FOLDER")
    try:
        # Using subprocess.run to execute the command
        result = subprocess.run(f"powershell.exe -ExecutionPolicy Bypass -File timeframe_archivist.ps1 -day {day} -event_start {event_start} -event_stop {event_stop} -event_timezone '{event_timezone}' -command {command} -files_destination_path '{windows_destination_folder}' ", shell=True, text=True, capture_output=True, check=True)
        
        # Printing the stdout of the command
        stdout = result.stdout
        # Printing the stderr of the command, if any
        if result.stderr:
            print("Standard Error:")
            print(result.stderr)
        return stdout
    except subprocess.CalledProcessError as e:
        # Handling errors that occur during the command execution
        print("An error occurred while executing the shell command:", e.stderr)    
    