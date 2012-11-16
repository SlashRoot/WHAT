from .models import Task
from django.contrib.auth.models import User
from django.template import loader, Context


def get_tasks_in_prototype_related_to_object(prototype_id, object):
    from django.contrib.contenttypes.models import ContentType
    user_contenttype = ContentType.objects.get_for_model(object)
    return Task.objects.filter(prototype__id=prototype_id, related_objects__content_type=user_contenttype, related_objects__object_id=object.id)