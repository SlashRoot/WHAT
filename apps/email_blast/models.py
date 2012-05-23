from django.db import models
from people.models import Group, Role, RoleInGroup
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage


class BlastMessage(models.Model):
    '''
    This is the model whose fields will be a part of the Blast Form
    '''
    subject = models.CharField(max_length=60)
    message = models.TextField()
    role = models.ForeignKey('people.Role')
    group = models.ForeignKey('people.Group')
    send_to_higher_roles = models.BooleanField(default=True)
    creator = models.ForeignKey('auth.User', related_name='blasts_sent')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    sent = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def get_email_address(self):
        return "%s__%s@blasts.slashrootcafe.com" % (self.group.name, self.role.name) #TODO: Unhardcode slashrootcafe.com?
    
    def prepare(self):
        return self.subject, self.message, self.creator.email, self.populate_targets()
            
    def populate_targets(self):
        role_in_group = RoleInGroup.objects.get(role=self.role, group=self.group)
        users_in_group = role_in_group.users().all()
        user_emails = set()
        
        for user in users_in_group:
            user_emails.add(user.email)
        
        return user_emails
    
    def send_blast(self):
        preparation_tuple = self.prepare()
        blast_email_object = EmailMessage(*preparation_tuple, headers = {'Reply-To': self.get_email_address()})
        return blast_email_object.send()
