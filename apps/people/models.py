from django.db import models
from django.db.models.signals import post_save
from django.db.models.query_utils import Q

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.utils import DatabaseError
from django.contrib.contenttypes import generic 



POLITICAL_PARTIES = (
                     (0, "Republican"),
                     (1, "Democrat"),
                     (2, "Conservative"),
                     (3, "Working Families"),
                     (4, "Independence"),
                     (5, "Green Party"),
                     )

class UserProfile(models.Model):
    '''Used to extend contrib.auth.models.User'''
    birth_month = models.IntegerField(max_length=2, blank=True, null=True)
    birth_day = models.IntegerField(max_length=2, blank=True, null=True)
    pin=models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(User)
    email_prefix = models.CharField(blank=True, null=True, max_length=80, unique=True)
    contact_info = models.OneToOneField('contact.ContactInfo', blank=True, null=True)
    political_party = models.IntegerField(choices=POLITICAL_PARTIES, blank=True, null=True)
    
    '''
    We are thinking of two more fields for contacts.
    Not sure whether they go with all users or only some subclass.
    They are "relationships," whereby we can ForeignKey them to User through a ManyToMany,
    and "Activity," which describes their involvement with SlashRoot (ie, "We designed a website for them.")
    '''  
    
    def __unicode__(self):
        if self.user.get_full_name():
            return unicode(self.user.get_full_name())
        else:
            return self.user.username
    
    def sessions(self):
        '''
        Returns a list of the times members login and logout.  
        '''
        sessions = []
        for session in Session.objects.all():
            try:
                if self.id == session.get_decoded()['_auth_user_id']:
                    sessions.append(session) 
            except (AttributeError, KeyError):
                pass
        return sessions


class Client(User):
    '''
    Justin says: I hate this model.  Let's not use it. Client will most likely end up as a method on UserProfile. 
    '''    
    comments=models.TextField()
    
class Member(models.Model):
    rank = models.ForeignKey('pigs.Rank', blank=True, null=True)
    inducted = models.ForeignKey('mooncalendar.Moon')
    user = models.OneToOneField(User)
    
   
    def purposes(self):
        '''
        BROKEN: Supposed to return a list of the instances of the members purposes (ie: Work Coffee bar, Dev, etc.)
        '''
        purposes = []
        for session in Session.objects.all():
            try:
                if self.id == session.get_decoded()['_auth_user_id']:
                    purposes.append(session.get_decoded()['presence']) 
            except (AttributeError, KeyError):
                pass
        return purposes
    
    def __unicode__(self):
        return self.user.get_full_name()
    
    
class Sabbatical(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    description = models.TextField()
    member = models.ForeignKey(Member)
## Lines 95-134 copy and pasted from group_rework branch
class Group(models.Model):
    '''
This is our replacement for django.contrib.auth.models.Group
We can haz methods?
'''
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
    
    
class Role(models.Model):
    '''
A role that someone has.
'''
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
    

class RoleInGroup(models.Model):
    '''
The presence of a particular role in a particular group.
'''
    role = models.ForeignKey('people.Role', related_name="groups")
    group = models.ForeignKey('people.Group', related_name="roles")
    users = models.ManyToManyField('auth.User', through="people.UserInGroup")
    
    class Meta:
        unique_together = ['role', 'group']
    
    def __unicode__(self):
        return '%s %s' %(self.role, self.group)
    
    

class RoleProgeny(models.Model):
    '''
For a particular group, a role may be part of a larger role, ie, all banana experts are fruit experts.
'''
    parent = models.ForeignKey(Role, related_name="children")
    child = models.ForeignKey(Role, related_name="parents")
    jurisdiction = models.ForeignKey(Group, related_name="role_progenies")


class RoleHierarchy(models.Model):
    '''
For a particular group, a role may be subordinant to another role, ie, the banana experts report to the starfruit experts, because starfruit is freaking amazing.
(For the record, I don't actually care for starfruit)
'''
    lower_role = models.ForeignKey(Role, related_name="higher_roles")
    higher_role = models.ForeignKey(Role, related_name="lower_roles")
    jurisdiction = models.ForeignKey(Group, related_name="role_hierarchies")
    
    
class UserInGroup(models.Model):
    '''
    A user's actual involvement in a group.
    '''
    user = models.ForeignKey(User, related_name="what_groups") #Related name can't be 'groups' because that will conflict with the "groups" field on auth.User
    role = models.ForeignKey(RoleInGroup)
    
    def __unicode__(self):
        return '%s %s' %(self.user, self.role)
    
    def add_user(self):
        pass
        
class Team(Group): 
    '''
    Needs to be re-thought. It's intention of having a team of members can probably be taken care of right in Group since members are included in Group. 
    '''   
    contact = models.ForeignKey(User, blank=True, null=True)
    members = models.ManyToManyField('people.Member', related_name="teams")    
    
class CommerceGroup(Group):
    '''
    A group that engages in commerce.
    '''
    description = models.TextField(blank=True, null=True)
    contact_info = models.OneToOneField('contact.ContactInfo', blank=True, null=True)
    
    def get_full_name(self):
        '''
        This method avoids an error when it's called to distinguish between a user and a commerce group. 
        '''
        return self.name
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        '''
        Makes sure the list is returned in order of name rather id or some other thing. 
        '''
        ordering = ['name']

class GenericPartyManager(models.Manager):
    '''
    A special manager to override the .get() for GenericParty.
    '''
    def get(self, *args, **kwargs):
        '''
        The basic functionality we want is to allow them to .get() for a "party," even though there's no single field called "party."
        When they do, we want to create a new object if none exists (essentially converting .get() to .get_or_create() if the query is for a party)
        '''
        try:    
            object = kwargs['party'] #Not asking for permission; we'll ask for forgiveness below.        
            if not len(kwargs) == 1: #Errr... Why are you specifying party *and* something else with get?  Party is unique, dude.
                raise self.model.DoesNotExist('Either specify only party or no party at all.  Boo on you.') #Yeah, seriously.
            else:
                #Here's the story for the next four lines:  Either they are looking for a User or a Group, which they specified in "party."
                #Either way, we'll get_or_create the type of object they want.
                #...and if you think about it, this model only really makes sense using get_or_create - the underlying entity already exists.
                #We're just making sure that they are reflected as a GenericParty.                     
                if object.__class__ == User: 
                    return super(GenericPartyManager, self).get_or_create(user=object)[0]  
                elif object.__class__ == Group:
                    return super(GenericPartyManager, self).get_or_create(group=object)[0]
                else: #Why they'd inquire about a GenericParty for any other object is beyond me, but let's at least give them a graceful prodding.
                    raise AttributeError('GenericParty must be either a User or a Group') 
        except KeyError: #Forgiveness for the 'party' dict issue.
            return self.get_query_set().get(*args, **kwargs)#There's no 'party' in the kwargs, so we'll just let them conduct a .get() as per usual.  Not sure what use that will be, but this at least keeps the behavior consistent.


class GenericParty(models.Model):
    '''
    The hotly contested model of any entity, be they a group or a User.
    
    Pass "party" as a kwarg to .get() in order to get-or-create.
    
    Yes, it's bad that user parties have a null value in the group column and vice-versa, but it's still faster than an ordinary generic relation.
    '''
    user = models.OneToOneField(User, blank=True, null=True)
    group = models.OneToOneField(Group, blank=True, null=True)
    
    objects = GenericPartyManager()
    
    messages = generic.GenericRelation('social.TopLevelMessage')
    
    budget_perspectives = models.ManyToManyField('commerce.BudgetPerspective', blank=True, null=True, help_text="This entity's view of the relationship between RealThings and BudgetLines.")
    
    def clean(self):
        if self.user and self.group:
            raise ValidationError('CommerceParty must refer to either a user or a group - not both.')
        
        if not self.user and not self.group:
            raise ValidationError('CommerceParty must have either a user or a group.')
    
    def name(self):
        if self.user:
            return self.user.get_full_name()
        else:
            return self.group.name
        
    def lookup(self):
        if self.user:
            return self.user
        else:
            return self.group
        
    def contact_info(self):
        if self.user:
            return self.user.userprofile.contact_info
        else:
            return self.group.contact_info
        
     
             
        
    
    def __unicode__(self):
        return str(self.lookup())
    
    class Meta:
        verbose_name_plural = "Generic Parties"
    
    
        

def createGenericParty(sender, instance, **kwargs):
    party = GenericParty.objects.get(party=instance) #Will create the GenericParty instance.                
    
    
    #Create new Generic Parties every time a user or group is created.
post_save.connect(createGenericParty, sender=User)
post_save.connect(createGenericParty, sender=Group)
    