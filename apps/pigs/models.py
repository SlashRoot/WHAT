from django.db import models
from people.models import Member

# Create your models here.
class Task(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=800)
    

class Accomplishment(models.Model):
    member=models.ForeignKey(Member)
    task=models.ForeignKey(Task)
    created=models.DateTimeField(auto_now_add=True)
    comments=models.CharField(max_length=200, null=True, blank=True)


class Badge(models.Model):
    """ As opposed to pigs.Rank, Badges are non-linear accomplishments of members.
    Badges are wholly objective - their requirements are quantifiable and testable.
    Terence and Justin think they are just hilarious.
        
    """
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=800)    
    requirements=models.ManyToManyField(Task) #There may be many tasks (or many repetitions of a task) required to complete a particular badge. 
    
    
    def requirement_check(self, member):
        for task in self.requirements:
            if not task.members__in == member: #TODO: Make this work. 
                return False
        
        return True #If we make it all the way through the loop, all the tasks have been accomplished, and thus, the member has earned this badge.
    
class Rank(models.Model):
    name=models.CharField(max_length=20)
    number=models.SmallIntegerField()
    color=models.CharField(max_length=7)
    strip=models.CharField(max_length=7, blank=True, null=True)
    
    def __unicode__(self):
        return self.name