import json
from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource
from utilities.logger import ThreadLogger
from utilities.get_current_userprofile import get_current_userprofile

# Global Variables
logger = ThreadLogger(__name__)

def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Delete given item(s)
        :param resource_id: The ID of the resource with the file
        :param all_files_path: Array of all file_paths for files being deleted
    """
    try:
        user = get_current_userprofile()
        resource_id =  parameters.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        s3_client = aws.get_boto3_client(None, "s3")
        file_path = parameters.get("all_files_path", [])
        all_files_path = json.loads(parameters.get("all_files_path", '[]'))
        files_to_delete = []
        for file_path in all_files_path:
            if not file_path["object_type"] == "Folder":
                files_to_delete.append(file_path["file_path"])
            else:
                all_folder_objects = s3_client.list_objects(
                    Bucket=resource.name, Prefix=file_path["file_path"]
                )
                [
                    files_to_delete.append(key)
                    for key in [
                        obj["Key"] for obj in all_folder_objects.get("Contents", [])
                    ]
                ]

        try:
            logger.info(f"Files to delete: {files_to_delete}")
            for name in files_to_delete:
                logger.info(f"Deleting file with key: {name}")

            res = s3_client.delete_objects(
                Bucket=resource.name,
                Delete={"Objects": [{"Key": name} for name in files_to_delete]},
            )
        except Exception as e:
            logger.error(e)
        # Log this action
        logger.info("User %s deleted %s from S3 bucket: %s" % (user, files_to_delete, resource.name))

    except Exception as e:
        error_message = e.args[0]
        logger.error(f'Failed to delete files from S3 bucket {resource.name} by user {user} with error {error_message}')