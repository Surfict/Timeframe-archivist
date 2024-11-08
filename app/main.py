from ast import Dict
import asyncio
from datetime import datetime, timedelta
from xmlrpc.client import boolean
from dotenv import load_dotenv
from enum import Enum
import logging
from logging import Logger
from pathlib import Path
from pydantic import BaseModel, Field, validator, ValidationError, root_validator
import re
from rich.console import Console
import typer
import typing as ty


# Internal files
from files import check_files_correctly_copied, rename_videos_for_windows, wrapp_data_to_videos
from powershell_calls import check_available_videos, copy_videos_to_windows,delete_videos
from definitions import Event, Inputs,VideoBasicInfos, VideoInfosWrapper
from inputs import yaml_data_to_events, prompt_options, prompt_validation_videos_found
from telegram_bot import send_message_to_telegram_conversation, format_links_message
from s3 import upload_videos_to_s3
from nextcloud import upload_file_to_nextcloud, create_public_shares

# Load environment variables from the .env file
load_dotenv(override=True) # Erase WSL2 env variable that were conflicting

# Definitions

LOGGER = logging.getLogger(__name__)
EVENTS_YAML_PATH = Path("../events.yml")
    
    
#TODO log level in env
#TODO S3 upload, gemeral review of the code

def main(
    log_level: int = logging.ERROR,
) -> None:
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    console = Console()
    typer.echo(f"Welcome to the Timeframe Archivist !")

    event =  Event(event_start="16:45",
                      event_stop="22:30",
                      complex_naming=False, 
                      video_title="Wednesday football", 
                      complex_name_format_helper="",
                      title_end_with_date=True,
                      event_timezone="Romance Standard Time",
                      validation_videos_found=True,
                      delete_videos_from_iphone= True,
                      S3_upload=True,
                      S3_storage_class="DEEP_ARCHIVE",
                      S3_bucket="timeframe-archivist",
                      S3_folder="ufutsal",
                      nextcloud_upload=True,
                      nextcloud_folder="/test2/wollishofen/16",
                      nextcloud_public_share=True,
                      nextcloud_telegram_notification=True)
    #inputs_result = Inputs(day="17/04/2024", event=event, complex_title_end="") # 0 videos
    inputs_result = Inputs(day="12/05/2024", event=event, complex_title_end="") # 2 videos
    #inputs_result = Inputs(day="25/03/2024", event=event, complex_title_end="") # 2 videos

    try:
        #events : ty.List[Event] = yaml_data_to_events(EVENTS_YAML_PATH)   
        #inputs_result = prompt_options(events)
        available_videos : ty.List[VideoBasicInfos]  = check_available_videos(inputs_result)
        if inputs_result.event.validation_videos_found:  
            prompt_validation_videos_found(available_videos)
        copy_videos_to_windows(inputs_result)
        check_files_correctly_copied(available_videos)
        videos_with_wrapped_data: ty.List[VideoInfosWrapper] = wrapp_data_to_videos(inputs_result, available_videos)
        rename_videos_for_windows(videos_with_wrapped_data)
        #files_nextcloud_locations = upload_file_to_nextcloud(videos_with_wrapped_data, inputs_result)
        #shares = create_public_shares(files_nextcloud_locations)
        #if inputs_result.event.nextcloud_telegram_notification:  
        #    message = format_links_message(shares)
        #    asyncio.run(send_message_to_telegram_conversation(message))
        #S3
        #if inputs_result.event.S3_upload:  
        #    upload_videos_to_s3(inputs_result, videos_with_wrapped_data)
        if inputs_result.event.delete_videos_from_iphone:
            delete_videos(inputs_result)
            
      
        

    except ValueError as e:
        console.print(f"Exiting due to an error: {e}", style="bold red")
        exit(1)        
    
    exit(0)
        



        

if __name__ == "__main__":
    typer.run(main)