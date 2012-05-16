from django.db import models
from django.contrib.auth.models import User

from people.models import Group, Role, RoleInGroup

class BlastMessage(models.Model):
    '''
    This is the model whose fields will be a part of the Blast Form
    '''
    subject = models.CharField(max_length=60)
    message = models.TextField()
    role = models.ForeignKey('people.Role')
    group = models.ForeignKey('people.Group')
    send_to_higher_roles = models.BooleanField(default=True)
    
    def populate_targets(self):
        role_in_group = RoleInGroup.objects.get(role=self.role, group=self.group)
        users_in_group = role_in_group.users.all()
        user_emails = set()
        
        for user_in_group in users_in_group:
            user_emails.add(user_in_group.user.email)
        
        return user_emails