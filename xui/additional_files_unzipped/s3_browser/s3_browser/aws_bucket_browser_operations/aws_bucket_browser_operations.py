import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from utilities.logger import ThreadLogger
from django.shortcuts import get_object_or_404, render
from resources.models import Resource, ResourceType
from infrastructure.models import CustomField
from resourcehandlers.aws.models import AWSHandler
from orders.models import CustomFieldValue
import boto3
import botocore

# Global Variables
logger = ThreadLogger(__name__)


def format_size(size):
    """
    Formats the size from bytes to either bytes (B), Kilobytes (KB), or Megabytes (MB)
    """
    if size < 1024:  # less than 1 KB
        return f"{size} B"
    elif size < 1024 * 1024:  # less than 1 MB
        return f"{round(size / 1024, 1)} KB"
    else:  # size is 1 MB or more
        return f"{round(size / (1024 * 1024), 1)} MB"


def get_file_type(key):
    """
    Split the key and return the file extension
    """
    file_extension = key.rsplit(".", 1)[-1] if "." in key else "No extension"
    return file_extension


def get_folder_with_items(aws, bucket_name, main_folder, bucket_location, flat=True):
    return_list = []
    delimiter = "/"

    try:
        if flat:
            delimiter = ""

        # Assume `aws` is an object that has the AWS credentials as attributes
        aws_access_key_id = aws.serviceaccount
        aws_secret_access_key = aws.servicepasswd

        # Create an S3 client using the credentials from 'aws'
        s3_config = botocore.client.Config(signature_version="s3v4")

        # Creating the S3 client with the specified configuration
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=get_bucket_region(bucket_name, aws),
            config=s3_config,
        )

        # Now, use 's3_client' instead of 's3client' below
        result = s3_client.list_object_versions(
            Bucket=bucket_name, Prefix=main_folder, Delimiter=("" if flat else "/")
        )

        # result = s3_client.list_object_versions(Bucket=resource.name, Prefix=key, Delimiter=delimiter)

        result_files = (
            get_files(
                bucket_name, main_folder, result, flat, bucket_location, s3_client
            )
            if result.get("Versions")
            else []
        )
        result_folders = (
            get_folders(bucket_name, main_folder, delimiter, s3_client, True)
            if result.get("CommonPrefixes")
            else []
        )
        return_list.extend(result_files)  # return files and folders
        return_list.extend(result_folders)

    except Exception as e:
        logger.exception(
            "Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
    return return_list


def get_files(
    bucket_name,
    main_folder,
    result,
    flat,
    bucket_location,
    s3client=None,
    sort_a_z=True,
):
    try:
        versions = result.get("Versions")
        delete_markers = result.get("DeleteMarkers")

        # Create a dictionary where the key is the file key, and the value is a list of version dictionaries
        versions_by_key = {}

        for obj in versions:
            key = obj.get("Key")
            if key == main_folder:
                continue
            file_size = format_size(obj.get("Size")) if "Size" in obj else "Deleted"
            params = {
                "Bucket": bucket_name,
                "Key": key,
                "VersionId": obj.get("VersionId"),
            }
            download_url = (
                s3client.generate_presigned_url("get_object", Params=params)
                if obj.get("Size") is not None
                else None
            )
            version_dict = {
                "version_id": obj.get("VersionId"),
                "is_latest": obj.get("IsLatest", False),
                "last_modified": obj.get("LastModified"),
                "size": file_size,
                "download_url": download_url,
                "is_delete_marker": False,
                "storage_class": obj.get("StorageClass").title(),
                "e_tag": obj.get("ETag"),
                "owner_name": obj["Owner"].get("DisplayName")
                if obj["Owner"].get("DisplayName")
                else obj["Owner"].get("ID"),
                "object_url": "https://{0}.s3.{1}.amazonaws.com/{2}".format(
                    bucket_name, bucket_location, key.replace(" ", "+")
                ),
                "actual_size": obj.get("Size"),
            }

            if key not in versions_by_key:
                versions_by_key[key] = []

            versions_by_key[key].append(version_dict)

        if delete_markers:
            for marker in delete_markers:
                key = marker.get("Key")
                if key == main_folder:
                    continue

                marker_dict = {
                    "version_id": marker.get("VersionId"),
                    "is_latest": marker.get("IsLatest", False),
                    "last_modified": marker.get("LastModified"),
                    "size": "Deleted",
                    "storage_class": None,
                    "type": "Delete Marker",
                    "is_delete_marker": True,
                }

                if key not in versions_by_key:
                    versions_by_key[key] = []

                versions_by_key[key].append(marker_dict)

        files_list = []
        for key, versions in versions_by_key.items():
            item_type = key.split(".")[-1] if "." in key else "Unknown"
            file_name = key.split("/")[-1] if not flat else key
            latest_version = next(
                (v for v in versions if v["is_latest"]), versions[0]
            )  # get the latest version if available, otherwise use the first version
            item_type = get_file_type(
                file_name
            )  # Use the type of the latest version, or extract from the file name if not available
            file_dict = {
                "key": key,
                "url": key,
                "name": file_name,
                "path": key.replace(file_name, ""),
                "storage_class": versions[0].get("StorageClass"),
                "item_type": item_type,
                "s3_uri": "s3://{0}/{1}".format(bucket_name, key),
                "arn": "arn:aws:s3:::{0}/{1}".format(bucket_name, key),
                "versions": versions,
                "item_type": item_type,  # Use the type of the latest version
                "download_url": latest_version.get(
                    "download_url"
                ),  # Use the download_url of the latest version
                "latest_version": latest_version,
            }

            files_list.append(file_dict)

        return sorted(
            files_list, key=lambda k: str(k["key"]).lower(), reverse=not sort_a_z
        )

    except Exception as e:
        logger.exception(
            "Error on line {}: {} {}".format(
                sys.exc_info()[-1].tb_lineno, type(e).__name__, e
            )
        )


def get_folders(bucket_name, main_folder, delimiter, s3client, sort_a_z):
    # Get the common prefixes (folders) using the delimiter
    response_with_delimiter = s3client.list_object_versions(
        Bucket=bucket_name, Prefix=main_folder, Delimiter=delimiter
    )
    common_prefixes = response_with_delimiter.get("CommonPrefixes", [])
    # Get all delete markers without using the delimiter
    response_without_delimiter = s3client.list_object_versions(
        Bucket=bucket_name, Prefix=main_folder
    )
    delete_markers = response_without_delimiter.get("DeleteMarkers", [])

    # Create a set of deleted object keys that have the latest delete marker
    deleted_objects = {
        marker["Key"] for marker in delete_markers if marker.get("IsLatest", False)
    }

    try:
        files_list = []
        for obj in common_prefixes:
            folder_prefix = obj.get("Prefix")

            # Check if all objects within the folder are in the deleted_objects set
            is_folder_deleted = all(
                version["Key"] in deleted_objects
                for version in response_without_delimiter.get("Versions", [])
                if version["Key"].startswith(folder_prefix)
            )

            item_type = "Folder"  # for show template
            url = folder_prefix
            folder_obj = {
                "key": folder_prefix,
                "url": url,
                "name": folder_prefix.replace(main_folder, ""),
                "item_type": item_type,
            }
            if is_folder_deleted:
                folder_obj["is_delete_marker"] = True
            files_list.append(folder_obj)

        return sorted(
            files_list, key=lambda k: str(k["key"]).lower(), reverse=not sort_a_z
        )
    except Exception as e:
        logger.exception(
            "Error on line {}".format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )


def is_versioning_enabled(s3_client, resource_id, default_region):
    """
    Check if versioning is enabled for an S3 bucket linked to a specified resource.

    This function attempts to fetch a resource and its associated AWSHandler based on the provided
    `resource_id`. It then tries to access a custom field named "s3_bucket_region" and use its value
    (or a default) to create an S3 resource client. Finally, it checks whether versioning is enabled
    for the S3 bucket associated with the resource.

    Parameters:
    - s3_client (boto3.client): A boto3 S3 client.
    - resource_id (int or str): The ID of the resource which is linked to the S3 bucket.
    - default_region: default s3 region passed from the IWH S3 Browser

    Returns:
    bool: True if versioning is enabled for the S3 bucket, otherwise False.

    Note:
    The function returns False if any error/exception occurs during the process.
    """

    try:
        # Get the resource by ID
        resource = get_object_or_404(Resource, pk=resource_id)
        aws = get_object_or_404(AWSHandler, pk=resource.aws_rh_id)
        logger.info(
            f"Checking if Bucket Versioning is enabled for the bucket '{resource.name}' "
        )
        # Get the region from the resource
        s3rcf = CustomField.objects.get(name="s3_bucket_region")

        region_attribute = resource.attributes.get(field_id=s3rcf.id)
        # default_region set from bucket_location in the inbound web hook 'S3 Browser'
        region = (
            region_attribute.str_value
            if region_attribute and region_attribute.str_value
            else default_region
        )

        # Get a boto3 resource wrapper for "bucket"
        s3_bucket = aws.get_boto3_resource(region_name=region, service_name="s3")

        if s3_bucket.BucketVersioning(resource.name).status == "Enabled":
            return True
        return False

    except (CustomField.DoesNotExist, CustomFieldValue.DoesNotExist) as error:
        logger.warning("CustomField 's3_bucket_region' does not exist")
        logger.info(
            "This error can arise when s3 buckets are added from discovery and their s3_bucket_region parmeter is not set."
        )
        logger.info(
            f"As a backup, attempting to connect to the AWS Resource client using the default region='{default_region}'."
        )
        # Please make sure the default_region is a valid option for the AWS account
        s3_bucket = aws.get_boto3_resource(
            region_name=default_region, service_name="s3"
        )

        if s3_bucket.BucketVersioning(resource.name).status == "Enabled":
            logger.info("Connected to the AWS Resource client")
            return True
        return False
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {str(e)}")
        return False


def create_presigned_url(
    bucket_name, object_name, aws, expiration=3600, version_id=None
):
    # Ensure the AWS credentials are valid and accessible
    aws_access_key_id = aws.serviceaccount
    aws_secret_access_key = aws.servicepasswd

    # Determine the bucket's region
    region = get_bucket_region(bucket_name, aws)

    # Create a specific config
    s3_config = botocore.client.Config(signature_version="s3v4")

    # Create an S3 client with specific credentials and region
    s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=s3_config,
    )

    # Params for the presigned URL
    presigned_url_params = {"Bucket": bucket_name, "Key": object_name}

    # If a version ID was provided, include it in the params
    if version_id:
        presigned_url_params["VersionId"] = version_id

    # Generate a presigned URL for the object
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object", Params=presigned_url_params, ExpiresIn=expiration
        )
    except botocore.exceptions.ClientError as e:
        # Handle any error that occurred during the generation
        logger.exception(f"An error occurred: {e}")
        return None

    return presigned_url


def get_bucket_region(bucket_name, aws):
    # Extract credentials from the aws object
    aws_access_key_id = aws.serviceaccount
    aws_secret_access_key = aws.servicepasswd

    # Create an S3 client using the specific credentials
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # Get the bucket location
    bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)

    # The location constraint can be None for the default region (us-east-1)
    # AWS returns None instead of 'us-east-1'
    region = bucket_location["LocationConstraint"]
    if region is None:
        region = "us-east-1"

    return region
