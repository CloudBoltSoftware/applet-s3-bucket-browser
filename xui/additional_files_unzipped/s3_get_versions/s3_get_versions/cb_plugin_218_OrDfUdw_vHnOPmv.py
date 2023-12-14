import shared_modules.aws_bucket_browser_operations as operations
from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile
import boto3
import botocore
import datetime

# Global Variables
logger = ThreadLogger(__name__)

def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Get the versions of a given object
        :param resource_id: the ID of the s3 storage bucket resource
        :param key: The key value of the item being checked for versions
    """
    try:
        user = get_current_userprofile()
        resource_id = parameters.get('resource_id')
        resource = get_object_or_404(Resource, pk=resource_id)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        key = parameters.get("key")
       
        # Assume `aws` is an object that has the AWS credentials as attributes
        aws_access_key_id = aws.serviceaccount  
        aws_secret_access_key = aws.servicepasswd  

        # Creating a custom configuration
        s3_config = botocore.client.Config(signature_version='s3v4')

        # Creating the S3 client with the specified configuration
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=s3_config
        )

        # Get a boto3 resource wrapper for "bucket"
        s3_bucket = s3_client.get_bucket_versioning(Bucket=resource.name)

        # Get the versions of an item
        response = s3_client.list_object_versions(Bucket=resource.name, Prefix=key)

        if s3_bucket['Status'] == "Enabled":
            versions = response.get('Versions', [])
            delete_markers = response.get('DeleteMarkers', [])

            response = []
            for version in versions:
                bucket_name = resource.name
                object_name = version.get('Key')
                version_id = version.get('VersionId')
                download_url = operations.create_presigned_url(bucket_name, object_name, aws, version_id=version_id)
                json_data = {
                    "is_latest": version.get('IsLatest'),
                    "Key": version.get('Key'),
                    "version_id": version.get('VersionId'),
                    "type": operations.get_file_type(version.get('Key')),
                    "last_modified": version.get('LastModified').strftime("%B %d, %Y, %I:%M %p"), 
                    "size": operations.format_size(version.get('Size')),  
                    "storage_class": version.get('StorageClass'),  
                    "download_url": download_url
                } 
                response.append(json_data)

            for marker in delete_markers:
                json_data = {
                    "Key": marker.get('Key'),
                    "version_id": marker.get('VersionId'),
                    "type": "Delete Marker",
                    "is_latest": marker.get('IsLatest'),
                    "last_modified": marker.get('LastModified').strftime("%B %d, %Y, %I:%M %p"),
                    "is_delete_marker": True,
                    "size": "N/A",
                    "storage_class": "N/A",
                    "download_url": "N/A"
                }
                response.append(json_data)
            response = sorted(response, key=lambda x: datetime.datetime.strptime(x['last_modified'], "%B %d, %Y, %I:%M %p"), reverse=True)
            return {"status": True, "message": "Successfully fetched", "data": response}
        logger.info('versioning not detected')
        logger.info(s3_bucket.BucketVersioning(resource.name).status)
        return {"status": True, "message": "Versioning disabled", "data": []}

    except Exception as e:
        error_message = e.args[0]
        # log error message with user 
        logger.error("User %s failed to get versions of %s" % (user, key))
        logger.error(error_message)
        return {"status": False, "message": error_message}