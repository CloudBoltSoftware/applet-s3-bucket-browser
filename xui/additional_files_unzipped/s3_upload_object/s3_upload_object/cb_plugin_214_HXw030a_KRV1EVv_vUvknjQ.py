import os
from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile

# Global Variables
logger = ThreadLogger(__name__)


def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Upload a single item
        :param resource_id: The ID of the s3 storage bucket resource
        :param bucket_name: The name of the s3 storage bucket
        :param path: The current location for the item to upload to
        :param file_name: The name of the file being uploaded
        :param object_file: The file data
    """
    try:
        resource_id = parameters.get("resource_id")
        user = get_current_userprofile()

        resource = get_object_or_404(Resource, pk=resource_id)
        file_name = os.path.join(
            parameters.get("path", None), parameters.get("file_name", None)
        )
        bucket_name = parameters.get("bucket_name", None)
        file = parameters.get("object_file", None)

        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        s3_client.put_object(Body=file, Bucket=bucket_name, Key=file_name)

        # Log this action
        logger.info(
            "User %s uploaded file %s to S3 bucket: %s"
            % (user, file_name, resource.name)
        )
        return {"status": True, "message": "Successfully Uploaded"}

    except Exception as e:
        logger.exception(
            "User %s failed to upload file %s to S3 bucket: %s"
            % (user, file_name, resource.name)
        )
        error_message = e.args[0]
        return {"status": False, "message": error_message}
