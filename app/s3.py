import boto3
from botocore.exceptions import NoCredentialsError
import os

from definitions import Event, Inputs


def create_s3_client():
    """
    Create an S3 client using explicit credentials.
    """
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

def upload_file_to_s3(inputs: Inputs):
    """
    Upload a file to an S3 bucket in the choosen storage class.
    """
    object_name = "test.mov"

    # Create an S3 client
    s3_client = create_s3_client()
    
    try:
        # Upload the file
        s3_client.upload_file(object_name, os.getenv("S3_BUCKET"), object_name, ExtraArgs={f'StorageClass': '{inputs}'})
        print("File uploaded successfully.")
        return True
    except FileNotFoundError:
        print("The file was not found.")
        return False
    except NoCredentialsError:
        print("Credentials not available.")
        return False
