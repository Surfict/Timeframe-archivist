from ast import Dict
from dotenv import load_dotenv
from enum import Enum
import logging
from logging import Logger
import os
from pathlib import Path
from pydantic import BaseModel, validator, ValidationError
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
                Event(event_start=yaml_data["events"][event]["event_start"], event_stop=yaml_data["events"][event]["event_stop"], complex_naming=yaml_data["events"][event]["complex_naming"], 
                      video_title=yaml_data["events"][event]["video_title"], 
                      complex_name_format_helper=yaml_data["events"][event]["complex_name_format_helper"], end_with_date=yaml_data["events"][event]["end_with_date"])
                    )

    return events


def main(
    log_level: int = logging.INFO,
) -> None:
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    logger.info(f"Script has been launched")
    logger.info(f"Value of env file is : {os.getenv('value1')}")
    e : ty.List[Event] = yaml_data_to_events(EVENTS_YAML_PATH)
    print(e)
    



if __name__ == "__main__":
    typer.run(main)