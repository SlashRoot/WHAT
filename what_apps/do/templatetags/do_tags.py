from django.template import Library, Template, Context
from what_apps.do.models import Task


register = Library()

@register.filter(name='task_is_owned_by_user')
def task_is_owned_by_user(task, user):
    "Removes all values of arg from the given string"
    return task.is_owned_by_user(user)

@register.filter(name='top_level_tasks_in_verb_by_privilege')
def top_level_tasks_in_verb_by_privilege(verb, privilege):
    return verb.top_level_tasks_for_privilege(privilege)

@register.filter(name='tasks_in_verb_by_privilege')
def tasks_in_verb_by_privilege(verb, privilege):
    return verb.get_tasks_for_privilege(privilege)

@register.filter(name='count_tasks_in_verb_by_privilege')
def count_tasks_in_verb_by_privilege(verb, privilege):
    return verb.count_tasks_for_privilege(privilege)

@register.filter
def show_related_object(object):
    return 'do/related_objects/' + str(object._meta)