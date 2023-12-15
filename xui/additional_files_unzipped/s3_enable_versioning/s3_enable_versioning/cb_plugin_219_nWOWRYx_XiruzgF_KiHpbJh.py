from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile

# Global Variables
logger = ThreadLogger(__name__)

def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Enable versioning on a bucket
        :param resource_id: The ID of the s3 resource bucket
    """
    try:
        user = get_current_userprofile()
        resource_id =  parameters.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        s3_client.put_bucket_versioning(
            Bucket=resource.name, VersioningConfiguration={"Status": "Enabled"}
        )
        # Log this action
        logger.info("User %s enabled versioning on S3 bucket %s" % (user, resource.name))
        return {"status": True, "message": "Successfully enabled"}
    except Exception as e:
        # log error by user 
        logger.exception("User %s failed to enable versioning on S3 bucket %s" % (user, resource.name))
        error_message = e.args[0]
        return {"status": False, "message": error_message}