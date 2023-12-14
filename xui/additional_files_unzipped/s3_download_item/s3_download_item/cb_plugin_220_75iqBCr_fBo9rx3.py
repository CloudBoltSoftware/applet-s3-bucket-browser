import os
import html
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
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
    Download a single item
        :param resource_id: The ID of the s3 bucket resource with the file
        :param path: The path or key of the file to be downloaded
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

    file_path = parameters.get("path", None)

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": resource.name, "Key": f"{file_path}"},
        ExpiresIn=3600,
    )
    # Log this action
    logger.info("User %s downloaded %s from S3 bucket: %s" % (user, file_path, resource.name))

    return {
        "status": 200,
        "url": mark_safe(f"{url}")
    }