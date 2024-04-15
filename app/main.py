from ast import Dict
from datetime import datetime, timedelta
from xmlrpc.client import boolean
from dotenv import load_dotenv
from enum import Enum
import json
import logging
from logging import Logger
from pathlib import Path
from pydantic import BaseModel, Field, validator, ValidationError, root_validator
import re
from rich.console import Console
import typer
import typing as ty
import yaml

import os


# Internal files
from powershell_calls import call_powershell_script
from utils import Event, Inputs

# Load environment variables from the .env file
load_dotenv(override=True) # Erase WSL2 env variable that were conflicting

# Definitions

LOGGER = logging.getLogger(__name__)
EVENTS_YAML_PATH = Path("../events.yml")
    
    
# Function to validate date format DD/MM/AAAA
def validate_date_format(date_str):
    if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
        return True
    return False
    


def yaml_data_to_events(
    events_filepath: Path
) -> ty.List[Event]:
    """
    This function parse yaml data from events.yml file and return a list of events
    """
    
    # Ensure file exists
    if not events_filepath.exists():
        raise FileNotFoundError(f"YAML config file not found at {events_filepath}")

    events: ty.List[Event] = []
    try:
        with open(events_filepath, "r") as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
            events_yaml = yaml_data["events"]
            for event in events_yaml:
                events.append(
                    Event(event_start=yaml_data["events"][event]["event_start"],
                          event_stop=yaml_data["events"][event]["event_stop"],
                          complex_naming=yaml_data["events"][event]["complex_naming"], 
                          video_title=yaml_data["events"][event]["video_title"], 
                          complex_name_format_helper=yaml_data["events"][event]["complex_name_format_helper"],
                          title_end_with_date=yaml_data["events"][event]["title_end_with_date"],
                          event_timezone=yaml_data["events"][event]["event_timezone"],
                          validation_videos_found=yaml_data["events"][event]["validation_videos_found"])
                        )
    except KeyError as e:
        raise KeyError(f"Missing expected key in the YAML config file: {e}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML config file: {e}")

    return events

def generic_prompt(number_start: int, number_end: int) -> int:
    valid_choice = False
    while not valid_choice:
        # Ask the user to choose an number
        chosen_number = int(typer.prompt("Please choose a number from the list above", type=int))

        # Ensure the chosen number is valid
        if number_start <= chosen_number <= number_end:
            valid_choice = True
        else:
            typer.echo("Invalid number chosen. Please choose a valid number.")
    return chosen_number


def prompt_validation_videos_found(videos_infos: str) -> boolean:
    """
    This function order videos_infos by ASC of date creation, 
    displays available videos found on the Iphone, then ask the user
    to validate if it corresponds to what he wants.
    """
    
    videos = json.loads(videos_infos)
    # Order videos by date created asc
    sorted_videos = sorted(videos, key=lambda x: x['CreationDate'])
    typer.echo("Videos found on the device : ")
    for video in sorted_videos:
        typer.echo(f"Size : {video['SizeMB']} - Date created : {video['CreationDate']} - Name : {video['Name']}")
        
    user_satisfied = typer.confirm("Do you want to continue ? ", default=True)
    
    if not user_satisfied:
        raise ValueError(f"User not satisfied with videos found on the Iphone")

    return user_satisfied


def prompt_options(events: ty.List[Event]) -> Inputs:
    """
    This function prompt the user to obtain the following informations :
    - Which event occured
    - If the event has a complex title (title that needs to be completed), to complet it
    - Is the even from today, yesterday or a specific given date
    And returns an Inputs object containing the user's answers.
    """
        
    # Display the list of video titles with numbers
    for i, event in enumerate(events, start=1):
        typer.echo(f"{i}: {event.video_title}")
    
    chosen_number = generic_prompt(1, len(events))
    chosen_event = events[chosen_number - 1]
    
    typer.echo(f"You picked: {chosen_number} - {chosen_event.video_title}")
    
    # If the event has a complex title, display the helper and ask to complete the title
    if chosen_event.complex_naming:
        while True:
            typer.echo("Your event has a complex naming (you need to complete it). The beginning of the title is :")
            typer.echo(f"{chosen_event.video_title}")
            typer.echo("It has to follow this format : ")
            typer.echo(f"{chosen_event.complex_name_format_helper}")
            complex_title_end = str(typer.prompt("Please complete the title", type=str))
            complete_title = f"{chosen_event.video_title}{complex_title_end}"
            typer.echo(f"Complete title : {complete_title}")

            # Ask the user if they are satisfied with the title
            user_satisfied = typer.confirm("Are you happy with this title?", default=True)

            if user_satisfied:
                break  # Exit the loop if the user is satisfied
            else:
                typer.echo("Let's try completing the title again.") 
    else:
        complex_title_end = None
        
    # Pick day when the even occured
    days = ["Today", "Yesterday", "Another day"]
    typer.echo(f"The event occured : ")
    for i, day in enumerate(days, start=1):
        typer.echo(f"{i}: {day}")
    chosen_number = generic_prompt(1, len(days))
    typer.echo(f"You picked: {chosen_number} - {days[chosen_number - 1]}")
    
    match chosen_number:
        case 1: # Today's date
            chosen_day = datetime.now().strftime("%d/%m/%Y")  # Today's date in DD/MM/YYYY format
        case 2:
            # Calculate yesterday's date
            yesterday_date = datetime.now() - timedelta(days=1)
            chosen_day = yesterday_date.strftime("%d/%m/%Y")  # Yesterday's date in DD/MM/YYYY format
        case 3: # A specific day has been chosen 
            while True:
                chosen_day = typer.prompt("Please specify the day in DD/MM/YYYY format")
                if validate_date_format(chosen_day):
                    typer.echo(f"You specified the day as: {chosen_day}")
                    break  # Exit the loop if the date is in the correct format
                else:
                    typer.echo("The date format is incorrect. Please use DD/MM/YYYY format.")
                
                
    inputs = Inputs(day=chosen_day, event=chosen_event, complex_title_end=complex_title_end)
            
    return inputs
    
def copy_videos_to_windows(inputs_result: Inputs):
    # Copy files to computer
    results_copy = call_powershell_script(inputs_result.day, inputs_result.event.event_start, inputs_result.event.event_stop, inputs_result.event.event_timezone, "copy_files")
    if results_copy:
        typer.echo(f"Videos have been transferred to {os.getenv('WINDOWS_DESTINATION_FOLDER')} with success !")
    else:
        raise ValueError(f"Error while copying files")
        
        
def check_available_videos(inputs_result: Inputs):
    available_videos = call_powershell_script(inputs_result.day, inputs_result.event.event_start, inputs_result.event.event_stop, inputs_result.event.event_timezone, "list_videos")
    available_videos_json = json.loads(json.loads(available_videos)) # Thanks to https://stackoverflow.com/questions/25613565/python-json-loads-returning-string-instead-of-dictionary
    if available_videos_json == {}:
        raise ValueError(f"No video founds for the given parameters (Day: {inputs_result.day}, Start : {inputs_result.event.event_start} Stop : {inputs_result.event.event_stop} Timezone : {inputs_result.event.event_timezone})")
    elif available_videos_json["Error"]:
        raise ValueError(f'{available_videos_json["Error"]}')
    else:
        return available_videos_json
    
    

def main(
    log_level: int = logging.INFO,
) -> None:
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    console = Console()
    typer.echo(f"Welcome to the Timeframe Archivist !")

    event =  Event(event_start="19:45",
                      event_stop="22:30",
                      complex_naming=False, 
                      video_title="Wednesday football", 
                      complex_name_format_helper="",
                      title_end_with_date=True,
                      event_timezone="Romance Standard Time",
                      validation_videos_found=True)
    inputs_result = Inputs(day="24/03/2024", event=event, complex_title_end="")
    try:
        #events : ty.List[Event] = yaml_data_to_events(EVENTS_YAML_PATH)   
        #inputs_result = prompt_options(events)
        available_videos = check_available_videos(inputs_result)
        if inputs_result.event.validation_videos_found:  
            prompt_validation_videos_found(available_videos)
        copy_videos_to_windows(inputs_result)

    except ValueError as e:
        console.print(f"Exiting due to an error: {e}", style="bold red")
        exit(1)        
    
    exit(0)
        



        

if __name__ == "__main__":
    typer.run(main)