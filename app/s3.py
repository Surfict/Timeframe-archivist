import boto3
from botocore.exceptions import NoCredentialsError
import os
from mypy_boto3_s3 import S3Client
from boto3.s3.transfer import S3UploadFailedError
from definitions import Inputs, VideoInfosWrapper
from botocore.exceptions import NoCredentialsError, EndpointConnectionError 
import typer
import typing as ty



def create_s3_client() -> S3Client:
    """
    Create an S3 client using explicit credentials.
    """
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    
    
def upload_videos_to_s3(inputs: Inputs, videos_with_wrapped_data: ty.List[VideoInfosWrapper]) -> None:
    
    for video in videos_with_wrapped_data:
        upload_file_to_s3(inputs, video.new_name, video.wsl_full_path)
        
        

def upload_file_to_s3(inputs: Inputs, video_name: str, video_wsl_path: str):
    """
    Upload a file to an S3 bucket in the choosen storage class.
    """
    
    # Create an S3 client
    s3_client: S3Client = create_s3_client()
    if inputs.event.S3_folder:
        full_path: str = f"{inputs.event.S3_folder}/{video_name}"
    else:
        full_path = video_name
            
    try:
        # Upload the file
        s3_client.upload_file(video_wsl_path, inputs.event.S3_bucket, full_path, ExtraArgs={'StorageClass': inputs.event.S3_storage_class})  # type: ignore
        typer.echo(f"File {video_name} uploaded to S3 {inputs.event.S3_storage_class} successfully")
        
    except FileNotFoundError:
        raise ValueError("File not found")
    except NoCredentialsError:
        raise ValueError("Credentials not available")
    except EndpointConnectionError:
        raise ValueError(f"Error while connecting to the provided aws enpoint {os.getenv('AWS_REGION')}, check your AWS region")
    except S3UploadFailedError as e:
        if "Check your key and signing method" in str(e):
            raise ValueError(f"Error while using aws credientials, check your AWS Secret key")
        else: 
            raise ValueError(f"{e}")