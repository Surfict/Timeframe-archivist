import re
    
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
   
   
 
# Function to validate date format DD/MM/AAAA
def validate_date_format(date_str):
    if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
        return True
    return False