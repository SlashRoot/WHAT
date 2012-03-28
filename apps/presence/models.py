"""
Let's have a little discussion about what this app is for, shall we?

The idea of the presence app is to understand what is happening: 
*inside the physical space of our store
*throughout the realm of our networks

Of course, in the web world, our primary beacon to the browser for tracking purposes is the session abstraction.
Thus, this app will use sessions in some weird ways to understand how our network and store is being utilized.

The main flow for user presence tracking is:

PresenceInstance --FK-=> SessionInfo <=-1/1-=> Session
        |-=> Presence Purpose
        

Or, to think about it from the perspective of a current session:

Session -=> SessionInfo -=> PresenceInstance -=> PresencePurpose

expressed like this:

session.sessioninfo.instances.all()[0].purpose

That will give you the first purpose (hence the [0]) for which a member reported logging in during a particular current session.

"""

from django.db import models
from people.models import Member
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore


from django.db.models import *
from django.db.models.signals import post_save, pre_delete, post_init,\
    post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
#from django.dispatch import receiver
import datetime
from django.dispatch.dispatcher import receiver
from push.functions import push_with_template, push_with_json
import socket

 


class PresencePurpose(models.Model):
    name=models.CharField(max_length=80)
    description=models.TextField()
    def __unicode__(self):
        return self.name

class PresenceInstance(models.Model):
    member = models.ForeignKey(Member)
    purpose = models.ForeignKey(PresencePurpose, related_name="instances")
    created = models.DateTimeField(auto_now_add=True)
    sessioninfo = models.ForeignKey('SessionInfo', related_name="instances") 
    
DAYSOFWEEK = (
              (0, 'Monday'),
              (1, 'Tuesday'),
              (2, 'Wednesday'),
              (3, 'Thursday'),
              (4, 'Friday'),
              (5, 'Saturday'),
              (6, 'Sunday'),
              )

class AnchorTime(models.Model):
    '''
    Describes an anchor time to which a member has committed.
    '''
    member=models.ForeignKey(Member)
    created=models.DateTimeField(auto_now_add=True)
    time=models.TimeField()
    dow=models.IntegerField(choices=DAYSOFWEEK)
    
    def __unicode__(self):
        return '%s %s - %s'% (self.get_dow_display(), self.time, self.member.user.username) 




class SessionInfo(models.Model):
    '''
    A little divided over what this class will become.
    For the moment, I'm picturing an enduring object that will store info about this session.
    As such, it will have repeated information, such as the associated user object.
    It's not exactly WET, as it instructs a slightly different piece of knowledge if you think about it:
    The session tells us which user *is currently* logged in; the SessionInfo tells us which user *was logged in* when the properties of this sessioninfo transpired.
    
    As a side note, this means that we can't rely on SessionInfo to tell us anything about the current state of the users logged into the app.
    It also means that the SessionInfo table will grow very quickly.
    Maybe cool, maybe not.
    '''
    #note: a OneToOneField with the name 'session' has been added as part of the inheritance
    created = models.DateTimeField(auto_now_add=True) #joined field is auto initialized with creation time
    destroyed = models.DateTimeField(blank=True, null=True)
    session_key = models.CharField(max_length=40, help_text = "Almost a ForeignKey, but we know that the session will disappear, so we'll just keep the key.")
    user = models.ForeignKey(User)
    ip = models.IPAddressField()
    hostname = models.CharField(max_length=40)
    
    def age(self):
        return (datetime.now() - self.created)


def user_login_listener(request, user, **kwargs):
    '''
    Listens for all user logins.
    This will probably be sliced into separate functions for Everyone, Members, etc.
    '''
        
    #request comes from the signal - use it to figure out the session object.
    session = Session.objects.get(session_key=request.session.session_key)
    
    try:
        session_info = SessionInfo.objects.get(session_key=session.session_key) #Does a SessionInfo exist already for this session?  If so, our work here is done.
    except SessionInfo.DoesNotExist: #There is no SessionInfo for this session yet; let's make one.   
        #the session object we just grabbed goes into the sessioninfo object.
        session_info = SessionInfo(session_key=session.session_key) 
        session_info.user = user
        try:
            session_info.ip = request.META['REMOTE_ADDR']
            session_info.hostname = socket.gethostbyaddr(session_info.ip)[0].split('.')[0]
        except KeyError:
            session_info.ip = "0.0.0.0"
            session_info.hostname = "unknown"
        except:
            session_info.ip = request.META['REMOTE_ADDR']
            session_info.hostname = "unknown"
        session_info.save()
        
        dict_to_push = {
                        'session_key' : session.session_key,
                        'get_decoded': session.get_decoded(),
                        'created': session_info.created.isoformat(),
                        'user': session_info.user.username
                        
                        }
        
        push_with_json(dict_to_push, "/feeds/presece/json") #TODO: Make this better.

user_logged_in.connect(user_login_listener)

def session_destroy_listener(sender, instance, **kwargs):    
    session = instance
    try:
        session_info = SessionInfo.objects.get(session_key=session.session_key)
        session_info.destroyed = datetime.datetime.now() #Set the time of destruction
        session_info.save()
        push_with_json({'item': session_info.user.username}, "/feeds/do/llamas/walruses/activity") #TODO: Make this better.
    except SessionInfo.DoesNotExist:
    #Send signal - did user logout?  Or was session destroyed by maintenance?  Or destroyed manually by the user?
        pass
    
post_delete.connect(session_destroy_listener, sender=Session)

class Location(models.Model):
    name=models.CharField(max_length=40)
    
class LocationStatePrototype(models.Model):
    name=models.CharField(max_length=40)
    color=models.CharField(max_length=6)
    created=models.DateTimeField(auto_now_add=True)
    
class LocationStateLog(models.Model):
    '''
    SlashRoot Security Advisory System State
    '''
    state = models.ForeignKey('presence.LocationStatePrototype')
    location = models.ForeignKey('presence.Location')
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User')
    
class MediaURL(models.Model):
    media = models.URLField()
    
    def __unicode__(self):
        return self.media
    

class AfterHoursTidiness(models.Model):
    '''
    Boolean fields to be called by the AfterHoursActivityForm for the tidiness section of the form.
    '''
    bar = models.BooleanField()
    backroom = forms.BooleanField
    tech_deck = forms.BooleanField
    other = forms.CharField(max_length=150)
    
class AfterHoursApplication(models.Model):
    pass #fields go here
    

    
