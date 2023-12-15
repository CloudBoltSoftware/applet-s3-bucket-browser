import shared_modules.aws_bucket_browser_operations as operations
from utilities.get_current_userprofile import get_current_userprofile
from django.shortcuts import get_object_or_404
from resourcehandlers.aws.models import AWSHandler
from resources.models import Resource, ResourceType
from resources.serializers import ResourceSerializer
from utilities.logger import ThreadLogger
import boto3
import botocore

# Global Variables
logger = ThreadLogger(__name__)


def inbound_web_hook_post(*args, parameters={}, **kwargs):
    """
    Browse the contents of an S3 bucket linked to the specified resource.
        :param resource_id: The ID of the resource which is linked to the S3 bucket to browse.
        :param state: An optional dict to store state information
            (like 'full_path' - current folder location and 'flat' - Bool for flattened view)
    """
    resource_id = parameters.get("resource_id")
    state = parameters.get("state", {})
    # Fetch the specified resource, raising a 404 error if it doesn't exist
    resource = get_object_or_404(Resource, pk=resource_id)

    # Fetch the AWS handler linked to the resource, raising a 404 error if it doesn't exist
    aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)

    # Assume `aws` is an object that has the AWS credentials as attributes
    aws_access_key_id = (
        aws.serviceaccount
    )  # replace with how you access your credentials
    aws_secret_access_key = (
        aws.servicepasswd
    )  # replace with how you access your credentials

    # Creating a custom configuration
    s3_config = botocore.client.Config(signature_version="s3v4")

    # Creating the S3 client with the specified configuration
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=s3_config,
    )
    # Initialize the path to the S3 folder
    s3_path = ""

    # Initialize lists to hold directories and their contents
    path_dirs = []
    dir_list = []

    # Get the folder path and flat mode from the parameters, if provided
    folder_path = parameters.get("path", state.get("full_path", None))
    flat = parameters.get("flat", str(state.get("flat", "False"))) == "True"

    # If a folder path is provided, split it into segments and add each to path_dirs
    if folder_path:
        for p in folder_path.split("/"):
            if p:
                s3_path = f"{s3_path}{p}/"
                path_dirs.append({"name": p, "path": s3_path})
    else:
        # If no folder path is provided, add the root path to path_dirs
        path_dirs.append({"name": "", "path": ""})

    # Declare region as "bucket_location" and set default region (ships as 'us-east-1')
    bucket_location = ""
    try:
        location_obj = s3_client.get_bucket_location(Bucket=resource.name)
        bucket_location = (
            location_obj["LocationConstraint"]
            if not location_obj["LocationConstraint"] == None
            else "us-east-1"
        )
    except Exception as e:
        logger.exception("Could not set bucket_location. Please check s3 bucket region")

    # Get a list of all items in the S3 path
    s3_list = operations.get_folder_with_items(
        aws, resource.name, s3_path, bucket_location, flat
    )
    for dir_item in s3_list:
        dir_item["is_file"] = dir_item["key"][-1] != "/"
        if dir_item["is_file"] or not flat:
            # If the directory item has versions, sort them by 'last_modified' date
            if "versions" in dir_item:
                dir_item["versions"] = sorted(
                    dir_item["versions"], key=lambda v: v["last_modified"], reverse=True
                )
                # Get the latest version
                latest_version = dir_item["versions"][0]
                # Add information from the latest version to the dir_item
                for key, value in latest_version.items():
                    # Skip adding the download_url if the type is DeleteMarker
                    if (
                        key == "download_url"
                        and latest_version.get("type") == "DeleteMarker"
                    ):
                        continue
                    dir_item[key] = value
            dir_list.append(dir_item)

    # Sort the directory list first by type (folder or file) and then by name
    dir_list = sorted(dir_list, key=lambda i: (i["is_file"], i["name"]))

    # Sort versions in each file entry by last_modified in descending order
    for entry in dir_list:
        if entry["is_file"]:
            entry["versions"].sort(key=lambda x: x["last_modified"], reverse=True)
    # Log the browsing activity
    user = get_current_userprofile()
    logger.info(
        "User %s browsed %s in S3 bucket: %s" % (user, folder_path, resource.name)
    )
    # Clear the old data before updating the state
    state.clear()
    # Update the state with the directory list, path directories, full path, and flat mode
    state.update(
        {
            "dir_list": dir_list,
            "path_dirs": path_dirs,
            "full_path": folder_path or "",
            "flat": flat,
            "versioning_enabled": operations.is_versioning_enabled(
                s3_client, resource_id, default_region=bucket_location
            ),
        }
    )
    return {
        "state": state,
        "resource": ResourceSerializer().resource_dict(resource),
        "location": bucket_location,
    }
