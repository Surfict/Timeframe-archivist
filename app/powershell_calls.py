from datetime import datetime, timedelta
import json
import os
import sys
import subprocess
import typer
import typing as ty

from definitions import VideoBasicInfos, Inputs, PowershellCommandParameter

from datetime import datetime, timedelta
import pytz


# TODO check if stdout can be parsed as JSON object, if not print error

def call_powershell_script(day: str, event_start: str, event_stop: str, event_timezone: str, command: PowershellCommandParameter) -> str | None:
    windows_destination_folder = os.getenv("WINDOWS_DESTINATION_FOLDER")
    try:
        # Using subprocess.run to execute the command
        result = subprocess.run(f"powershell.exe -ExecutionPolicy Bypass -File ../timeframe_archivist.ps1 -day {day} -event_start {event_start} -event_stop {event_stop} -event_timezone '{event_timezone}' -command {command.value} -files_destination_path '{windows_destination_folder}' ", shell=True, text=True, capture_output=True, check=True)
        
        stdout = result.stdout
        # Printing the stderr of the command, if any
        if result.stderr:
            print("Standard Error:")
            print(result.stderr)
        return stdout
    except subprocess.CalledProcessError as e:
        # Handling errors that occur during the command execution
        print("An error occurred while executing the shell command:", e.stderr)    
    
    
def copy_videos_to_windows(inputs_result: Inputs):
    # Copy files to computer
    results_copy = call_powershell_script(inputs_result.day, inputs_result.event.event_start, inputs_result.event.event_stop, inputs_result.event.event_timezone, PowershellCommandParameter.COPY_FILES)
    results_json = json.loads(results_copy)
    if isinstance(results_json, str): # Thanks to https://stackoverflow.com/questions/25613565/python-json-loads-returning-string-instead-of-dictionary
        results_json = json.loads(results_json)
    if isinstance(results_json, dict) and "Error" in results_json:
        raise ValueError(f'{results_json["Error"]}')
    else:
        typer.echo(f"Videos have been transferred to {os.getenv('WINDOWS_DESTINATION_FOLDER')} with success !")
        
        
def check_available_videos(inputs_result: Inputs) -> ty.List[VideoBasicInfos]:
    available_videos = call_powershell_script(inputs_result.day, inputs_result.event.event_start, inputs_result.event.event_stop, inputs_result.event.event_timezone, PowershellCommandParameter.LIST_VIDEOS)
    available_videos_json = json.loads(available_videos)
    if isinstance(available_videos_json, str): 
        available_videos_json = json.loads(available_videos_json) # Thanks to https://stackoverflow.com/questions/25613565/python-json-loads-returning-string-instead-of-dictionary
    if available_videos_json == []:
        raise ValueError(f"No video found for the given parameters (Day: {inputs_result.day}, Start : {inputs_result.event.event_start} Stop : {inputs_result.event.event_stop} Timezone : {inputs_result.event.event_timezone})")
    elif isinstance(available_videos_json, dict) and "Error" in available_videos_json:
        raise ValueError(f'{available_videos_json["Error"]}')
    else:
        # Order videos by date created asc
        sorted_videos = sorted(available_videos_json, key=lambda x: x['creation_date'])
        video_basic_infos_list = []
        for video in sorted_videos:
            video_basic_infos_list.append(VideoBasicInfos(size_mb=video["size_mb"], creation_date=video["creation_date"], original_name=video["original_name"]))
        return video_basic_infos_list