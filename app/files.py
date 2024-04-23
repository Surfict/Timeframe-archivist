import os
import typing as ty

# Internal files
from definitions import Inputs,VideoBasicInfos, VideoInfosWrapper
from utils import windows_to_wsl2_path, get_extension



def check_files_correctly_copied(available_videos: ty.List[VideoBasicInfos]):
    """
    This function checks if the files copied with powershell script are present on Windows
    """
    for video in available_videos:
        wsl2_path = windows_to_wsl2_path(os.getenv("WINDOWS_DESTINATION_FOLDER"))
        file_exists = os.path.exists(wsl2_path + "/" + video.original_name)
        if not file_exists:
            raise ValueError(f"File {video.original_name} has not been correctly copied to {os.getenv('WINDOWS_DESTINATION_FOLDER')}\\{video.original_name}")
        
    
    
# TODO Check complex name is windows
          
def wrapp_data_to_videos(inputs_result: Inputs, videos : ty.List[VideoBasicInfos]) -> ty.List[VideoInfosWrapper]:
    """
    This function create the title and wsl full path of each videos
    and return an object wrapping them
    """   
    
    
    video_title = inputs_result.event.video_title
    wsl2_path = windows_to_wsl2_path(os.getenv("WINDOWS_DESTINATION_FOLDER"))
    if inputs_result.event.complex_naming:
        video_title = video_title + inputs_result.complex_title_end
    if inputs_result.event.title_end_with_date:
        video_title = video_title + " " + inputs_result.day.replace('/', '_')
        
    if len(videos) == 1:
        video_extension = get_extension(videos[0].original_name)
        video_title = f"{video_title}.{video_extension}"
        wsl_full_path=f"{wsl2_path}/{video_title}"
        videosInfosWrapper = VideoInfosWrapper(video_basic_infos=videos[0], new_name=video_title, wsl_full_path=wsl_full_path)
        return [videosInfosWrapper]

    else: 
        video_titles = []
        len_videos = len(videos)
        count = 1
        for video in videos:
            video_extension = get_extension(video.original_name)
            video_final_title = f"{video_title} (Part {count} of {len_videos}).{video_extension}"
            wsl_full_path=f"{wsl2_path}/{video_final_title}"
            videosInfosWrapper = VideoInfosWrapper(video_basic_infos=video, new_name=video_final_title, wsl_full_path=wsl_full_path)
            video_titles.append(videosInfosWrapper)
            count = count + 1
        return video_titles
    
    
def rename_videos_for_windows(videos : ty.List[VideoInfosWrapper]):
    """
    This function rename the videos with the desired selected options by the user on the Windows host
    """
    wsl2_path = windows_to_wsl2_path(os.getenv("WINDOWS_DESTINATION_FOLDER"))
    for video in videos:
        video_old_path = wsl2_path + "/" + video.video_basic_infos.original_name
        try:
            os.rename(video_old_path, video.wsl_full_path)
        except OSError as e:
            raise ValueError(f"Failed to rename {video_old_path} to {video.wsl_full_path}: {str(e)} \n This could be due to the use of forbidden caracters in the title of the video for windows files.")