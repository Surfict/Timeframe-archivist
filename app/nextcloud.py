import xml.etree.ElementTree as ET
import json
import os
import pprint
import requests
from requests.auth import HTTPBasicAuth
import typer
import typing as ty

#
from definitions import Inputs, VideoInfosWrapper, NextCloudInfos
from utils import normalize_folders_path


# TODO test on different user folder
# TODO account with limited rights on ownclouds

def get_nextcloud_infos() -> NextCloudInfos:
    """
    Return nextcloud infos from env file like login, pwd, url, and formated urls for webdav and OCS APIs
    """
    
    nextcloud_base_url = normalize_folders_path(os.getenv("NEXTCLOUD_BASE_URL")) #remove ending / if present
    nextcloud_user = os.getenv("NEXTCLOUD_USER")
    nextcloud_password = os.getenv("NEXTCLOUD_PASSWORD")
    nextcloud_webdav_url = f"{nextcloud_base_url}/remote.php/dav/files/{nextcloud_user}"
    nextcloud_ocs_url = f"{nextcloud_base_url}/ocs/v2.php/apps/files_sharing/api/v1"
    nextcloud_infos = NextCloudInfos(user=nextcloud_user, password=nextcloud_password, base_url=nextcloud_base_url, webdav_url=nextcloud_webdav_url, ocs_url=nextcloud_ocs_url)
    
    return nextcloud_infos 



def create_public_shares(file_paths: ty.List[str]) -> ty.List[str]:
    """
    Create a public share for the given nextcloud files
    file_paths : for a link in the following form : https://{website}/remote.php/dav/files/{user_root_folder}/one_folder/one_file.txt, desired path would only be "/one_folder/one_file.txt"
    """
    
    share_links = []
    nextcloud_infos = get_nextcloud_infos()
    
    for file_path in file_paths:
        ocs_url = f"{nextcloud_infos.ocs_url}/shares"
        headers = {
            "OCS-APIRequest": "true",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'path': file_path,
            'shareType': 3,  # 3 for public link
            'permissions': 1  # Read permissions
        }
        response = requests.post(ocs_url, headers=headers, data=data, auth=HTTPBasicAuth(nextcloud_infos.user, nextcloud_infos.password))
        
        # OCS doesn't follow HTTP code responses and always return 200 even in case of problems...
        # To parse OCS's return code, we have to parse the HTTP request response in XML

        if response.status_code in [200, 201]:
            
            # Parse OCS response which is in XML
            response_to_xml = ET.fromstring(response.text)
            status_code = response_to_xml.find('.//statuscode').text
            
            if status_code == "200":
                # Navigate to the token element (link for share)
                token_element = response_to_xml.find('.//token').text
                if token_element is not None:
                    share_links.append(f"{nextcloud_infos.base_url}/s/{token_element}")
                else:
                    raise ValueError(f"Failed to retrieve the share link for {file_path} (token value not present)")
            else:
                status = response_to_xml.find('.//status').text
                message = response_to_xml.find('.//message').text
                raise ValueError(f"Failed to create share. Error in the request to the OCS API : Status code = {status_code} - Status = {status} - message = {message}")
                
                             
        else:
            raise ValueError(f"Failed to create share. Status code: {response.status_code}, Response: {response.text}")
        
    return share_links
        
        
    
    


def create_folders_if_they_do_not_exist(folders_path : str):
    
    """
    This function create all the folder in folders_path if they do not exist
    A folder can't be created if it parent does not exist.
    """
    
    nextcloud_infos = get_nextcloud_infos()
    next_cloud_webdav_url = f"{nextcloud_infos.webdav_url}"
    # Split the path to handle each folder
    folders = folders_path.split('/')
    path_to_create = ''
    for folder in folders:
        if folder:
            path_to_create += '/' + folder
            full_url = f"{next_cloud_webdav_url}{path_to_create}/"
            
            response = requests.request('PROPFIND', full_url, auth=HTTPBasicAuth(nextcloud_infos.user, nextcloud_infos.password))
            
            if response.status_code == 404:  # 404 means folder does not exist
                # Try to create the folder
                response = requests.request('MKCOL', full_url, auth=HTTPBasicAuth(nextcloud_infos.user, nextcloud_infos.password))
                if response.status_code == 201:
                    typer.echo(f"Folder {path_to_create} created successfully")
                else:
                    raise ValueError(f"Failed to create the folder {path_to_create}. Status code: {response.status_code}. Response: {response.text}")
                
            elif response.status_code == 207:  # Assuming 207 means folder exists
                #TODO log already exist
                test = 1
            else:
                raise ValueError(f"Error checking the folder {path_to_create}. Status code: {response.status_code}. Response: {response.text}")
            


def upload_file_to_nextcloud(videos: ty.List[VideoInfosWrapper], inputs_result: Inputs) -> ty.List[str]:
    
    """
    This function upload the list of videos in parameter into nextcloud.
    It return the list of the files's location on Nextcloud after having been uploaded.
    
    """
    
    nextcloud_infos = get_nextcloud_infos()
    nextcloud_folder = normalize_folders_path(inputs_result.event.nextcloud_folder)
    create_folders_if_they_do_not_exist(nextcloud_folder)
    files_locations = []
    
    for video in videos:
    # Open the local file
        with open(video.wsl_full_path, 'rb') as file_data:
            # Prepare the full URL (concatenating the remote file path)
            full_url = f"{nextcloud_infos.webdav_url}/{nextcloud_folder}/{video.new_name}"
            print(full_url)

            # Make a PUT request to upload the file
            response = requests.put(full_url, data=file_data, auth=HTTPBasicAuth(nextcloud_infos.user, nextcloud_infos.password))

            # Check if the upload was successful
            if response.status_code == 201:
                typer.echo(f"File {video.new_name} uploaded successfully. Go to {full_url} Status code: {response.status_code}, Response: {response.content}")
                files_locations.append(f"{nextcloud_folder}/{video.new_name}")                
            elif response.status_code == 204:
                 typer.echo(f"File {video.new_name} overwritten successfully. Go to {full_url}")  
                 files_locations.append(f"{nextcloud_folder}/{video.new_name}")    
            else: 
                raise ValueError(f"Failed to upload file {video.new_name} Status code: {response.status_code}, Response: {response.content}")
                
    return files_locations