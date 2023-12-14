import json
import time 
from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile
import boto3
import botocore

# Global Variables
logger = ThreadLogger(__name__)

def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Promotes a specific version of a file to the latest.

    Copies the version, then deletes the old referenced version.

        :param resource_id: The ID of the s3 bucket resource with the file
        :param key: Identifying key for the file to be restored
        :param version_id: The version_id string for the file version
    """
    user = get_current_userprofile()
    resource_id =  parameters.get("resource_id")
    resource = get_object_or_404(Resource, pk=resource_id)
    aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
    # Assume `aws` is an object that has the AWS credentials as attributes
    aws_access_key_id = aws.serviceaccount  # replace with how you access your credentials
    aws_secret_access_key = aws.servicepasswd  # replace with how you access your credentials

    # Creating a custom configuration
    s3_config = botocore.client.Config(signature_version='s3v4')

    # Creating the S3 client with the specified configuration
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=s3_config
    )
    key = parameters.get("key")
    version_id = parameters.get("version_id")
    bucket = resource.name
    copy_source = {"Bucket": resource.name, "Key": key, "VersionId": version_id}

    try:
        s3_client.copy_object(
            Bucket=bucket,
            CopySource=copy_source,
            Key=key,
        )
        # Introduce a wait time to let S3 catch up
        time.sleep(5)  # Pause execution for 5 seconds

        # Copying the source duplicates the item and all the versions
        # so we need to delete the original after a copy 
        s3_client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)

        # Log the user activity
        logger.info("User %s promoted version %s in S3 bucket: %s" % (user, version_id, resource.name))

        json_data = {
            "key": parameters.get("key"),
            "version_id": parameters.get("version_id"),
        }

        return {
            "status": True,
            "message": "Successfully promoted version",
            "data": json_data,
        }
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchVersion':
            logger.error(f"The specified version: {version_id} does not exist in S3 bucket: {resource.name}")
        else:
            # Re-raise the exception if it was not a 'NoSuchVersion' error
            raise e
    except Exception:
        logger.error(
            "User %s failed to promote version %s in S3 bucket: %s" % (user, version_id, resource.name)
        )
        logger.error(Exception)
        raise Exception