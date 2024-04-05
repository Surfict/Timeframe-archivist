from datetime import datetime, timedelta
import os
import sys
import typing as ty

from utils import Event, Inputs

def check_video_files_for_given_interval(inputs: Inputs) -> ty.List[str]:
    """
    Lists videos created in the given date interval.

    :param directory: Directory to search for videos.
    :param start_date: Start of the date interval (inclusive).
    :param end_date: End of the date interval (inclusive).
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.mp4', '.mov')):
            filepath = os.path.join(directory, filename)
            creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if start_date <= creation_time <= end_date:
                print(f"Video: {filename}, Date: {creation_time}")c    
    

    