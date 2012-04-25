from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Group(models.Model):
    name = models.CharField()
    
class RoleInGroup(models.Model):
    name = models.CharField()
    
class UserInGroup(models.Model):
    user = models.ForeignKey(User)
    role = models.ForeignKey(RoleInGroup)
    group = models.ForeignKey(Group)
    
    