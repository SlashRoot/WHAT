import datetime

from django.db import models
from django.contrib.auth.models import User, Group 
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.localflavor.us.forms import USPhoneNumberField


from social.models import Link
from people.models import UserProfile
from comm.models import CommunicationInvolvement

BICYCLE_DAY = datetime.datetime(1943, 4, 19) #I can explain, but I don't want to.


class ContactInfo(models.Model):
    '''
    This is contact information that may go with an individual or entity.
    Notice that 'email' is missing as this is part of auth.User or any model describing an entity.
    This model basically requires incoming relationships to have any kind of normal life.
    For example, people.userprofile has a 1to1 to this.
    '''
    address = models.CharField(max_length=200, blank=True, null=True)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)    
    websites = models.ManyToManyField(Link, blank=True, null=True, related_name='operators') 
    image = models.ImageField(blank=True, null=True, upload_to="public/images/profile")

    def __unicode__(self):
        try:
            return str(self.userprofile.user.get_full_name())
        except UserProfile.DoesNotExist:
            return self.list_phone_numbers_as_string()
        
    def list_phone_numbers_as_string(self):
        phone_numbers = ""
        for phone in self.phone_numbers.all():
            phone_numbers += phone.number + ","
            
        return phone_numbers
    
    def get_absolute_url(self):
        return '/contact/contact_profile/%s/' % str(self.id)
            
PHONE_NUMBER_TYPES = (
            ('mobile', 'mobile'),
            ('home', 'home'),
            ('business', 'business'),
            ('fax', 'fax'), #"Yeah.... in 1988"
            ('voip', 'voip'), #Skype and such
            ('robo-dialer', 'robo-dialer'),
            ('unknown', 'unknown'),
            ('other', 'other'),
            
            #We'll use this to indicate that we want to dial this person as a VOIP client, with their username as the client's ID token.
            #Typical use case is giving a twilio device an incoming capability token with the username in question.
            ('username_as_client_id', 'username_as_client_id'), 
            
            )

class PhoneNumberManager(models.Manager):
    def get_blank_number(self):
        return self.get_or_create(number="+10000000000")       


class PhoneNumber(models.Model):
    type = models.CharField(choices=PHONE_NUMBER_TYPES, max_length=20)
    number = PhoneNumberField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('ContactInfo', related_name="phone_numbers", blank=True, null=True)
    
    objects = PhoneNumberManager()
    
    def __unicode__(self):
        if self.owner:
            return "%s (%s)" % (self.owner, self.type)
        elif self.number == "+10000000000":
            return "Blank Number"
        else:
            return "Unknown Caller #%s" % self.id
        
    
    def save(self, owner=None, *args, **kwargs):
        if owner:
            #Sometimes we pass the owner in manually.  If that's the case, assign that owner as the new owner.
            self.owner = owner

        #We're having a problem with phone numbers mysteriously becoming dis-associated from their owner.  This is an attempt to figure out why so that we can write a test against it.
        if self.id is not None: #This is already in the database - let's see what the database thinks the owner is.
            current = PhoneNumber.objects.get(id=self.id)
            if current.owner: #We want the cases where there is indeed a current owner.....
                if not self.owner: #But there is no new owner.
                    #Holy shit!  Why are we erasing the owner?
                    from meta.alerts import local_red_alert
                    import inspect
                    message = "Phone number has disappeared!\n  Phone number %s previous belonged to %s \n\n Stack Trace:\n\n %s" % current.id, current.owner, str(inspect.stack())
                    local_red_alert(message)
                    
        super(PhoneNumber, self).save(*args, **kwargs)
        
        
        self.populate_calls()
        return self
    
    def get_absolute_url(self):
        return '/contact/phone_number_profile/%s' % self.id
    
    def call_url(self):
        return '/comm/outgoing_call_menu/?phone_number=' + self.id
    
    def remove_dashes(self):
        n = self.number
        return n[0:3] + n[4:7] + n[8:12]
    
    def populate_calls(self):
        '''
        method to assign a user to all calls which have this phone number.
        Of course, this will only work if only one user has this number.
        If that is the case, we'll return True.
        Otherwise, we'll return False.
        '''
        #First the calls TO this user
        calls = self.calls_to.all()
        counter = 0
        for call in calls:
            new = call.participants.get_or_create(person=self.user(), direction="to")[1]
            if new:
                counter += 1
            
        
        #Now the calls FROM this user
        calls = self.calls_from.all()
        for call in calls:
            new = call.participants.get_or_create(person=self.user(), direction="from")[1]
            if new:
                counter += 1
                        
        return counter
    
    def user(self):
        try:
            return self.owner.userprofile.user
        except AttributeError:
            return False


class PhoneProvider(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name
    
    def get_response_object(self):
        if self.name == "Twilio":
            from twilio import twiml
            return twiml.Response()
        
        if self.name == "Tropo":
            from tropo import Tropo
            return Tropo()

class AdditionalEmail(models.Model):
    '''
    Assume that the email associated with their django User object is the primary.  This gives them a secondary.
    '''
    email = models.EmailField(unique=True)
    contact_info = models.ForeignKey('contact.ContactInfo', related_name="additional_emails")


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User)
    type = models.IntegerField(choices=( (0, "General Inquiries"), (1, "Tech Support"), (2, "Member Services") ) )


#This model will have links to other models for whom a distinctly named model method will constitute the "action" to be taken.
class MailHandlerAction(models.Model):
    name = models.CharField(max_length=80)    
    
class MailHandler(models.Model):
    address = models.CharField(max_length=200)
    actions = models.ManyToManyField(MailHandlerAction, blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True, null=True)

class MailMessage(models.Model):
    subject=models.TextField()
    body=models.TextField()
    recipient=models.CharField(max_length=200)
    sender=models.CharField(max_length=200)
    
    

    
def adopt_contact_info(user):
    p = user.userprofile
    c = ContactInfo(address = p.address, address_line2 = p.address_line2, city = p.city, state = p.state, postal_code = p.postal_code, image = p.image  )
    c.save()
    p.contact_info = c
    p.save()
    

class DialList(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name
    
    def get_active_numbers(self):
        #TODO: Make this query more efficient
        active = self.numbers.all()
        return active
        
    def make_call(self, twilio_response_object, caller_id, dial_action_url=None, number_url=None):
        '''
        Takes a twilio response object, caller id and action URL.
        Returns a twilio_response_object with addDial to each of the numbers in this dial list. 
        '''
        if dial_action_url:
            dial = twilio_response_object.addDial(callerId = caller_id, record=True, action=dial_action_url)
        else:
            dial = twilio_response_object.addDial(callerId = caller_id, record=True)
            
        active_numbers = self.get_active_numbers()
        
        for number in active_numbers:
            if number_url:
                dial.addNumber(number.number.number, url = number_url)
            else:
                dial.addNumber(number.number.number)
                
        for client in self.clients.all():
            dial.client(client.user.username)
            
    

class DialListParticipation(models.Model):
    '''
    Participation of a particular phone number in a dial list.
    '''
    number = models.ForeignKey('contact.PhoneNumber', related_name="dial_lists" )
    list = models.ForeignKey('contact.DialList', related_name="numbers")
    created = models.DateTimeField(auto_now_add=True)
    green_phone = models.BooleanField(help_text="Bypass confirmation to answer calls.")
    
    def __unicode__(self):
        return str(self.number.owner if self.number.owner else self.number) + ' on ' + str(self.list)
    
    def actual_phone_number(self):
        return self.number.number
    
    class Meta:
        unique_together = ['number', 'list']


class DialListClientParticipation(models.Model):
    '''
    Participation of software clients (such as the twilio client or voxeo softphone) in a diallist.
    '''
    user = models.ForeignKey('auth.User', related_name="dial_lists_as_client")
    list = models.ForeignKey('contact.DialList', related_name="clients")
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'list']

    def __unicode__(self):
        return str(self.user.username) + ' on ' + str(self.list)