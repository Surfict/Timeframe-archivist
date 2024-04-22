import requests
from requests.auth import HTTPBasicAuth

def upload_file_to_nextcloud(local_file_path, remote_file_path):
    # Open the local file
    with open(local_file_path, 'rb') as file_data:
        # Prepare the full URL (concatenating the remote file path)
        full_url = f"{nextcloud_url}{remote_file_path}"

        # Make a PUT request to upload the file
        response = requests.put(full_url, data=file_data, auth=HTTPBasicAuth(username, password))
        
        # Check if the upload was successful
        if response.status_code == 201:
            print("File uploaded successfully.")
        else:
            print("Failed to upload file. Status code:", response.status_code, "Response:", response.text)