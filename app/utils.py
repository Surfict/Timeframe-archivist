from pydantic import BaseModel, Field, validator, ValidationError, root_validator
import re
from typing import Any, Optional, TypedDict

class Event(BaseModel):
    event_start: str
    event_stop: str
    complex_naming: bool
    video_title: str
    complex_name_format_helper: str | None 
    title_end_with_date: bool
    event_timezone: str
    validation_videos_found: bool
    S3_upload: bool
    S3_storage_class: str | None
    
    
    @validator('complex_name_format_helper', always=True, pre=True)
    def check_simple_name_value_based_on_complex_naming(cls, v: Any, values: dict[str, Any]):
        if 'complex_naming' in values and values['complex_naming']:
            if not v:
                raise ValueError('complex_name_format_helper is mandatory when complex_naming is True')
        return v
    
    @validator('S3_storage_class', always=True, pre=True)
    def check_S3_storage_class_value_based_on_S3_upload(cls, v: Any, values: dict[str, Any]):
        if 'S3_upload' in values and values['S3_upload']:
            if not v:
                raise ValueError('S3_storage_class is mandatory when S3_upload is True')
        return v
    
class Inputs(BaseModel):
    day: str
    complex_title_end: str | None
    event: Event
    
    # complex_title_end can't be empty if event.complex_naming = true
    @root_validator(pre=True)
    def check_complex_title_end_based_on_event_complex_naming(cls, values: dict[str, Any]):
        event = values.get('event')
        complex_title_end = values.get('complex_title_end')
        if event and event.complex_naming and not complex_title_end:
            raise ValueError('complex_title_end is required when complex_naming is True in the event')
        return values
    
class InputsDataWrapper(BaseModel):
    inputs: Inputs
    windows_title: str
    common_title: str
    wsl_full_path: str    
    
    
def windows_to_wsl2_path(windows_path: str) -> str:
    """
    Converts a Windows path to a WSL2 compatible path.

    Args:
    windows_path (str): A Windows-style file path (e.g., 'C:\\Users\\Username\\file.txt').

    Returns:
    str: A WSL2-style path (e.g., '/mnt/c/Users/Username/file.txt').
    """
    # Regex to capture the drive letter and the rest of the path
    match = re.match(r"([a-zA-Z]):\\(.*)", windows_path)
    if not match:
        raise ValueError("Invalid Windows path format")

    drive, path_remainder = match.groups()
    # Convert backslashes to forward slashes separately
    path_remainder = path_remainder.replace('\\', '/')
    wsl2_path = f"/mnt/{drive.lower()}/{path_remainder}"
    return wsl2_path


def get_extension(filename: str) -> str:
    """
    Extracts and returns everything after the last period in the filename.
    
    Args:
    filename (str): The filename from which to extract the extension.
    
    Returns:
    str: The file extension or an empty string if no extension is found.
    """
    match = re.search(r'.*\.(.*)', filename)
    if match:
        return match.group(1)  # Return the captured group which is the extension
    else:
        return ""  # Return an empty string if no period was found