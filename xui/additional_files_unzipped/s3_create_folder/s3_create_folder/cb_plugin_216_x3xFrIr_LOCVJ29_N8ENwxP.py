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
    Create a folder in an S3 bucket
        :param resource_id: The ID of the s3 storage bucket resource
        :param bucket_name: The name of the s3 storage bucket
        :param path: The current location (where the folder will be created)
        :param folder_name: The name of the folder being created
    """
    try:
        user = get_current_userprofile()
        resource_id =  parameters.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id)
        folder_path = os.path.join(
            parameters.get("path", None), parameters.get("folder_name", None)
        )
        bucket_name = parameters.get("bucket_name", None)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        s3_client.put_object(Bucket=bucket_name, Key=(folder_path + "/"))
        # Log this action
        logger.info("User %s created folder %s in S3 bucket: %s" % (user, folder_path, resource.name))
        return {"status": True, "message": "Successfully Created"}
    except Exception as e:
        # log error message with user 
        logger.exception("User %s failed to create folder %s in S3 bucket: %s" % (user, folder_path, resource.name))
        error_message = e.args[0]
        return {"status": False, "message": error_message}