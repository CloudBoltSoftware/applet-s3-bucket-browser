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
    Rename an object on S3
        :param resource_id: The ID of the s3 storage bucket resource
        :param path: The current location of the item
        :param bucket_name: The name of the s3 storage bucket
        :param old_object_name: The original object name
        :param new_object_name: The new object name
    """
    try:
        user = get_current_userprofile()
        resource_id =  parameters.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id)
        old_object_name = os.path.join(
            parameters.get("path", None), parameters.get("old_object_name", None)
        )
        new_object_name = os.path.join(
            parameters.get("path", None), parameters.get("new_object_name", None)
        )
        bucket_name = parameters.get("bucket_name", None)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        copy_source = {"Bucket": bucket_name, "Key": old_object_name}
        s3_client.copy_object(
            CopySource=copy_source, Bucket=bucket_name, Key=new_object_name
        )
        s3_client.delete_object(Bucket=bucket_name, Key=old_object_name)
        # Log this action
        logger.info("User %s renamed %s to %s in S3 bucket: %s" % (user, old_object_name, new_object_name, bucket_name))

        return {"status": True, "message": "Successfully Renamed"}
    except Exception as e:
        error_message = e.args[0]
        # log error message with user 
        logger.exception("User %s failed to rename %s to %s in S3 bucket: %s" % (user, old_object_name, new_object_name, bucket_name))
        return {"status": False, "message": error_message}