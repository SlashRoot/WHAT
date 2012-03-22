from django.db.models.signals import post_save

from push.functions import push_with_template

from do.models import Task, TaskHierarchy


def notifyNewChildTask(sender, instance, **kwargs):
    parent = instance.parent
    child = instance.child
    push_with_template('do/task_row_detailed.html', {'task': child}, "/do/new_child/" + str(parent.id))
    

post_save.connect(notifyNewChildTask, sender=TaskHierarchy)

def notifyNewTask(sender, instance, **kwargs):
    
    for parent in instance.parents.all():
        push_with_template('do/task_row_detailed.html', {'task': parent}, "/do/new_chlid/" + parent.id)
    #Notify parents
                    

#Create new Generic Parties every time a user or group is created.
post_save.connect(notifyNewTask, sender=Task)