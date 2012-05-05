from django.db import models
from django.contrib.auth.models import User

class BlastMessage(models.Model):
    '''
    This is the model whose fields will be a part of the Blast Form
    '''
    subject = models.CharField(max_length=60)
    message = models.TextField()
    role = models.ForeignKey('people.RoleInGroup')
    group = models.ForeignKey('people.Group')
    send_to_higher_roles = models.BooleanField(default=True)    