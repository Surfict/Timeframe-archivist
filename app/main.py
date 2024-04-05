from ast import Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum
import logging
from logging import Logger
import os
from pathlib import Path
from pydantic import BaseModel, validator, ValidationError
import re
import typer
import typing as ty
from typing import Any, Optional, TypedDict
import yaml

# Load environment variables from the .env file
load_dotenv()

# Definitions

LOGGER = logging.getLogger(__name__)

EVENTS_YAML_PATH = Path("../events.yml")



class Event(BaseModel):
    event_start: str
    event_stop: str
    complex_naming: bool
    video_title: str
    complex_name_format_helper: Optional[str] = None
    end_with_date: bool
    
    
    @validator('complex_name_format_helper', always=True, pre=True)
    def check_simple_name_value_based_on_complex_naming(v: Any, values: dict[str, str]):
        if 'complex_naming' in values:
            # If complex_naming is True, complex_name_format_helper is not optional
            if values['complex_naming'] and v is None or v == "":
                raise ValueError('complex_name_format_helper is mandatory when complex_naming is True')
            # If complex_naming is False, complex_name_format_helper is mandatory
            else:
                return v
        return v
    
class Inputs(BaseModel):
    day: str
    complex_title_end: Optional[str] = None
    event: Event
    
    @validator('complex_title_end', always=True, pre=True)
    def check_complex_title_end_based_on_event_complex_naming(cls, v: Any, values: dict[str, Any]):
        print(values)
        print(v)
        if 'event' in values and values['event'].complex_naming:
            if v is None or v == "":
                raise ValueError('complex_title_end is required when complex_naming is True in the event')
        return v
    
    
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

    events: ty.List[Event] = []
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
                      end_with_date=yaml_data["events"][event]["end_with_date"])
                    )

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


def prompt_options(events: ty.List[Event]) -> Inputs:
    """
    This function prompt the user to obtain the following informations :
    - Which event occured
    - If the event has a complex title (title that needs to be completed), to complet it
    - Is the even from today, yesterday or a specific given date
    """
    
    # Pick event
    
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
            end_complex_title = str(typer.prompt("Please complete the title", type=str))
            complete_title = f"{chosen_event.video_title}{end_complex_title}"
            typer.echo(f"Complete title : {complete_title}")

            # Ask the user if they are satisfied with the title
            user_satisfied = typer.confirm("Are you happy with this title?", default=True)

            if user_satisfied:
                break  # Exit the loop if the user is satisfied
            else:
                typer.echo("Let's try completing the title again.") 
    else:
        end_complex_title = None
        
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
                
                
    inputs = Inputs(day=chosen_day, event=chosen_event, complex_title_end=None)
            
    return inputs
    


def main(
    log_level: int = logging.INFO,
) -> None:
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    typer.echo(f"Welcome to the Timeframe archivist !")
    #logger.info(f"")
    events : ty.List[Event] = yaml_data_to_events(EVENTS_YAML_PATH)   
    inputs_result = prompt_options(events)
    print(inputs_result)
    


if __name__ == "__main__":
    typer.run(main)