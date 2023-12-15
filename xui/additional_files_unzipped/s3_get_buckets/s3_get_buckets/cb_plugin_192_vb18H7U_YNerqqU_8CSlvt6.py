from utilities.get_current_userprofile import get_current_userprofile
from resources.models import Resource, ResourceType


def inbound_web_hook_get(request):
    """
    Get a JSON list of buckets for the current user
    """
    up = get_current_userprofile()
    group_ids = [group.id for group in up.get_groups()]
    rt = ResourceType.objects.get(name="s3_bucket")
    buckets = (
        Resource.objects.filter(resource_type_id=rt.id)
        .filter(group_id__in=group_ids)
        .filter(lifecycle="ACTIVE")
        .order_by("-created")
    )
    bucket_info = [{"id": bucket.id, "name": bucket.name} for bucket in buckets]

    return {"bucket_info": bucket_info}
