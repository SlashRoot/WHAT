from django.db import models
from django.db.models.signals import post_save
from push.functions import push_with_json

STATUS_CHOICES = (
          (0, 'cool'),            #Everything is cool.
          (1, 'not cool'),        #Problems with staging only.
          (2, 'fuck all.')       #Problems with production.
          )

class StatusLog(models.Model):
    '''
    A snapshot of a particular status at a particular time.
    '''
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    creator = models.ForeignKey('auth.User', blank=True, null=True)
    
class StatusDescription(models.Model):
    '''
    Used only when failures require a description.
    '''
    incident = models.OneToOneField('meta.StatusLog')
    description = models.TextField()
    
def update_heartbeat(sender, instance, created, **kwargs):
    dict_to_push = {'id':instance.id, 'created':instance.created.isoformat()}
    push_with_json(dict_to_push, '/heartbeat')
    
post_save.connect(update_heartbeat, sender=StatusLog)