from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail, EmailMessage
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from what_apps.people.models import GenericParty
from what_apps.utility.models import GenericPartyForeignKey
import mimetypes






'''Examples of Tags:

Object:
*live-events (Sector)
*Rick (Person)
*coffee (Product / Service)
*Wolf Moon (Time Period)


Non-object
*Awesome (adjective)
*Activism

Things that will be tagged
events, projects, links, announcements

'''


                


class Message(models.Model):
    creator = models.ForeignKey('auth.User', related_name="messages")
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    

    
    def service_log_display(self):
        return "Message from %s" % self.creator.username

    def get_latest_in_thread(self):
        try:
            #Is this a toplevel message?  If so, we're looking for the latest child.
            return self.toplevelmessage.children.latest('created')
        except ThreadedMessage.DoesNotExist:
            #See what happened here is that this is a toplevel message with no children.  Thus, we return this here message cuz it be the latest (in fact the only) in the thread.
            return self
        except TopLevelMessage.DoesNotExist:
            #OK, in this case, we have a threaded message.  We need to look at the latest in the thread of its parent.            
            return self.parent.get_latest_in_thread()
        
class TopLevelMessageManager(models.Manager):
    '''
    
    '''

    def make_log(self, user, message, group=None):
        '''
        creates and returns a log for a user.
        
        if group is specified, creates and returns a log if user is in the group otherwise returns False.
        '''
        
        if not group: #group wasn't specified.  Thus, they must want to make a log on a user.
            recipient_party = GenericParty.objects.get(party=user)            
        else: #They did specify a group!  Let's check if they are a member of that group.
            if not user in group.users().all():             
                return False #return False only for non-members
            else: #Yep! They're in there!  We'll set the group as the recipient.
                recipient_party = GenericParty.objects.get(party=group)#logs are TopLevelMessages only to GenericParty objects not to the actual user or group
        return self.create(creator=user, content_object=recipient_party, message=message) #Send it out (recipient party is now the GenericParty object of either a User or a Group).
    
    def complete_log(self, party):
        '''
        Logs GenericParty messages. TODO: Improve for basic user/group
        '''
        if party.user:
            params = Q(content_type__name='generic party', object_id=party.id)
            
            for user_in_group in party.user.what_groups.all():
                group_party = GenericParty.objects.get(party=user_in_group.role.group)
                params = params | Q(content_type__name='generic party', object_id=group_party.id)
                
            return self.filter(params)
        else:
            raise NotImplementedError()
        
class TopLevelMessage(Message):
    '''
    A message that relates to an object.
    '''
    content_type = models.ForeignKey(ContentType, help_text="The object to which this message is affixed.")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = TopLevelMessageManager()
    
      
    def is_log(self):        
        '''  
        For the moment we have decided that a log is a message whose content type is a GenericParty.
        
        returns True in such cases, otherwise False 
        '''
        return bool(str(self.content_type) == "generic party")
        
            
        
class ThreadedMessage(Message):
    '''
    A message that relates to another message.
    '''
    parent = models.ForeignKey('social.TopLevelMessage', related_name='children')


def message_threads_for_object(object):
    '''
    Returns a list of message threads for a particular object, ordered by the latest post
    '''
    pass

def message_threads_for_object_family(object):
    '''
    Takes a progeny-style object family, returns a list of top-level messages for the object and its downward progeny, ordered by latest post
    '''
    #TODO: Account for situations where improperly objects (ie. Phone Call Errors) raise AttrError probably in the future, let's raise ReallyFuckedUpError instead
    lookup_dict = {
              'content_type': ContentType.objects.get_for_model(object),
              'object_id': object.id,
    }
    
    top_level_messages = list(TopLevelMessage.objects.filter(**lookup_dict))
    
    for progeny in object.children.all():
        top_level_messages += list(message_threads_for_object_family(progeny.child))
    
    sorted_top_level_messages = sorted(top_level_messages, key=lambda message: message.get_latest_in_thread().created, reverse=False)
    
    return sorted_top_level_messages

class UserReadsMessage(models.Model):
    '''
    Marks a message 'read' by a particular user.
    '''
    creator = models.ForeignKey('auth.user', related_name="messages_read")
    message = models.ForeignKey('social.message', related_name="read_by_users")
    
    class Meta:
        unique_together = ('creator', 'message')
        unique_together = ('creator', 'message')
        

class Link(models.Model):
    url=models.URLField()
    description=models.TextField(blank=True, null=True)


class FileAttachedToMessage(models.Model):
    message = models.ForeignKey('social.message', related_name="files")
    file = models.FileField(upload_to="public/images/message_files")
    creator = models.ForeignKey('auth.user', related_name="files_uploaded")
    created = models.DateTimeField(auto_now_add=True)
    
    def get_file_type(self):
        path = str(self.file.path)
        mimetypes_tuple = mimetypes.guess_type(path)
        return mimetypes_tuple[0].split('/')[0] #The actual type, ie what comes before the slash - so this is the "image" in "image/jpeg" or whatever


class DrawAttentionManager(models.Manager):
    def unread(self, *args, **kwargs):
        '''
        Shows only unread DrawAttention objects.
        '''
        
        return super(DrawAttentionManager, self).filter(acknowledgement__isnull = True)
    
class DrawAttention(models.Model):
    '''
    Allows a person to communicate with a GenericParty that they want to Draw Attention to a particular object.
    
    The canonical example is a phone call - if a member answers the phone and takes a message for another member, they need to "Draw Attention" to the call.
    '''    
    target = GenericPartyForeignKey(related_name="notices")
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User')
        
    #The object to which attention is being drawn
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = DrawAttentionManager()
    
    def __unicode__(self):
        return "%s drew the attention of %s to %s" % (self.creator, self.target.name(), self.content_object)   
    
    def message(self):
        return '%s wants to draw your attention to <a href="http:/slashrootcafe.com%s">%s</a> on %s' % \
            (self.creator, self.content_object.get_absolute_url(), self.content_object, self.created)
            
    def acknowledge(self, user=None):
        if not user: #If we haven't gotten a user, we need to be acknowledging a DrawAttention to a user (we'll resolve it for that user.)
            if self.target.user:
                return Acknowledgement.objects.get_or_create(attention = self, creator = self.target.user)
            else:
                raise TypeError('This DrawAttention is not for a particular user - probably for a group.  Thus, you must tell me which member of the group is acknowledging by passing user to this method.')
        return Acknowledgement.objects.get_or_create(attention = self, creator = user)
        
    def is_somewhat_acknowledged(self):
        #At least one target user has acknowledged this.
        if self.target.user:
            return Acknowledgement.objects.filter(attention=self, creator=self.target.user).exists() #If an acknowledgement exists, we'll return True.
        
        if self.target.group:
            for user in self.target.group.user_set:
                if Acknowledgement.objects.filter(attention=self, creator=user).exists():
                    return True #If even one user has acknowledged, we're good to return True.
            return False #...otherwise False (nobody has acknowledged)
    
    def is_fully_acknowledged(self):
        #All target users have acknowledged.
        if self.target.group:
            for user in self.target.group.user_set:
                if not Acknowledgement.objects.filter(attention=self, creator=user).exists():
                    return False #If even one user hasn't acknowledged, we'll return False.
            return True
        
        if self.target.user:
            return self.is_somewhat_acknowledged() #For single user, the somewhat acknowlged logic is the same (ie, have they or have they not acknowledged this?
                    
            
def draw_attention_messenger(sender, instance, **kwargs):
    subject = str(instance.content_object)
    body = '%s wants to draw your attention to <a href="http:/slashrootcafe.com%s">%s</a> on %s \n\n' % \
            (instance.creator, instance.content_object.get_absolute_url(), instance.content_object, instance.created)
            
    try:
        for message in instance.content_object.messages.order_by('-created')[:3]: #The three most recent messages for this object.
            body +="\n\n %s said: \n\n %s" % (message.creator, message.message)
    except AttributeError: #This content_object doesn't have a GenericForeignKey to messages.
        pass
    
    party = instance.target.lookup()
    
    
    recipients = []
    if party.__class__ == User:        
        recipients.append(party.email)
    else:
        for user in party.users.all():
            recipients.append(party.email)
            
    
    
    msg = EmailMessage(subject, body, 'info@slashrootcafe.com', recipients)
    msg.content_subtype = "html"
    msg.send()
    
    
post_save.connect(draw_attention_messenger, sender=DrawAttention)
    
class Acknowledgement(models.Model):
    '''
    Acknowledge a DrawAttention object
    '''
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User')
    attention = models.OneToOneField(DrawAttention)
    
    class Meta:
        db_table = "social_acknowledge" #Backward compatibility.