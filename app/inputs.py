from datetime import datetime, timedelta
from pathlib import Path
import typer
import typing as ty
import yaml

# Internal
from definitions import Event, Inputs,VideoBasicInfos

from utils import validate_date_format


def prompt_validation_videos_found(videos_infos: ty.List[VideoBasicInfos]) -> bool:
    """
    This function order videos_infos by ASC of date creation, 
    displays available videos found on the Iphone, then ask the user
    to validate if it corresponds to what he wants.
    """
    
    typer.echo("Video(s) found on the device : ")
    for video in videos_infos:
        video : VideoBasicInfos = video
        typer.echo(f"Size : {video.size_mb} Mb - Date created : {video.creation_date} - Name : {video.original_name}")
        
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
                          validation_videos_found=yaml_data["events"][event]["validation_videos_found"],
                          S3_upload=yaml_data["events"][event]["S3_upload"],
                          S3_storage_class=yaml_data["events"][event]["S3_storage_class"],
                          nextcloud_upload=yaml_data["events"][event]["nextcloud_upload"],
                          nextcloud_folder=yaml_data["events"][event]["nextcloud_folder"],
                          nextcloud_public_share=yaml_data["events"][event]["nextcloud_public_share"],
                          nextcloud_telegram_notification=yaml_data["events"][event]["nextcloud_telegram_notification"])
                        )
    except KeyError as e:
        raise KeyError(f"Missing expected key in the YAML config file: {e}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML config file: {e}")

    return events