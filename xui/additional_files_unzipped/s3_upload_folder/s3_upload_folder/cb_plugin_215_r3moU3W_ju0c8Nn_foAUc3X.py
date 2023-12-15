from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile

# Global Variables
logger = ThreadLogger(__name__)


def inbound_web_hook_post(*args, parameters={}, files, **kwargs):
    """
    Upload an entire folder
        :param resource_id: The ID of the s3 storage bucket resource
        :param bucket_name: The name of the s3 storage bucket
        :param folder_path: The current location for the folder to upload to
        :files request.FILES: The files uploaded with the request
                     file[#]: The file data
                file[#].path: The file path with folder
    """
    try:
        user = get_current_userprofile()
        resource_id = parameters.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id)
        bucket_name = parameters.get("bucket_name", None)
        folder_path = parameters.get("folder_path")

        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        for file in files:
            key = parameters.get(file + ".path")
            item = files.get(file)
            if folder_path:
                key = folder_path + key
            s3_client.put_object(Body=item, Bucket=bucket_name, Key=key)

        # Log this action
        logger.info(
            "User %s uploaded folder %s to S3 bucket: %s"
            % (user, folder_path, resource.name)
        )

        return {"status": True, "message": "Successfully Uploaded Folder"}

    except Exception as e:
        error_message = e.args[0]
        logger.exception(
            "User %s failed to upload folder %s to S3 bucket: %s"
            % (user, folder_path, resource.name)
        )
        return {"status": False, "message": error_message}
