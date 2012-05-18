'''
Functions for extracting information from SIP / VOIP calls.
Attempts to be less gnostic with providers and rely instead on the implementations in services.py
'''

import json

from django.utils.datastructures import MultiValueDictKeyError


from comm.models import PhoneCall, CommunicationInvolvement
from comm import comm_settings


from do.models import Task, TaskPrototype, TaskRelatedObject, TaskAccessPrototype, TaskAccess
from utility.models import FixedObject
from people.models import UserProfile

from django.contrib.auth.decorators import permission_required
from comm.services import place_deferred_outgoing_conference_call
from django.db.models.signals import post_save
import datetime
import re

RESOLVE_PHONE_CALL = "TaskPrototype__resolve_phone_call" #TODO: There is an instance of this string in views.py.  Dehydrate.
ANSWER_PHONE_CALLS_PRIVILEGE = 3

from contact.models import PhoneNumber, PhoneProvider, DialList

from push.functions import push_with_template



def notifyCallSave(instance, **kwargs):
    '''
    When phone calls are saved, push to watch_calls
    ''' 
    if instance.__class__ == PhoneCall:
        call = instance
        
        if kwargs['created']:
            resolve_protoype = FixedObject.objects.get(name=RESOLVE_PHONE_CALL).object        
            resolve_task = resolve_protoype.instantiate()
            resolve_relationship = TaskRelatedObject.objects.create(task = resolve_task, object = call)
            try:
                access = TaskAccess.objects.create(task=resolve_task, prototype = FixedObject.objects.get(name="TaskAccessPrototype__answer_phone_calls").object)
            except FixedObject.DoesNotExist:
                #TODO: The FixedObject isn't in the DB yet.  Run the setup.
                raise
    if instance.__class__ == CommunicationInvolvement:
        call = instance.communication.phonecall #TODO: This will break when we introduce non-phonecall CommunicationInvolvement objects.
    push_with_template('comm/call_alert.html', {'call': call}, "/incomingCall")

post_save.connect(notifyCallSave, sender=PhoneCall)
post_save.connect(notifyCallSave, sender=CommunicationInvolvement)

def get_or_create_nice_number(incoming_number):
    '''
    A wrapper over get_or_create for a PhoneNumber object.  Gets or Creates a new PhoneNumber from various formats.
    '''
    try:
        number_as_list = re.findall(r"[0-9]", incoming_number) #No matter the format, grab only the numbers.
        
        #An unknown caller will produce a completely blank number.
        if not number_as_list:
            return PhoneNumber.objects.get_blank_number()
        
        if number_as_list[0] == '1': #If the first digit is a 1, we'll just pop it off.
            number_as_list.pop(0)
        if not len(number_as_list) == 10: #Now we expect to have exactly ten digits.
            raise TypeError("I wasn't able to discern exactly ten digits from the phone number you gave me.")
        incoming_number = ''.join(number_as_list) #Now our incoming number is properly formatted.
        
    except TypeError:
        raise RuntimeError("We expected this phone number to be a string.  It wasn't.  You suck.")

    phone_number = "+1" + str(incoming_number)
    nice_number = phone_number[2:5] + "-" + phone_number[5:8] + "-" + phone_number[8:] #parse the number to look like django wants it: ex. 845-633-8330
    phone_number_object, new = PhoneNumber.objects.get_or_create(number = nice_number)
    return phone_number_object, new
    
def call_object_from_call_info(call_info):
    '''
    Takes a standardized call info dict and extracts call objects from it. 
    '''
    #First let's get the call id of the call we're being asked about.    
    call_id = call_info['call_id']
    
    #Let's see if we already know about this call.
    try:
        call = PhoneCall.objects.get(call_id=call_id) #Set call to a phone call matching the call_id we just got.
        return call #We already know about this call.  Let's just dispense with the formalities and return the call.
    except PhoneCall.DoesNotExist, e: #This call does not exist in our database.
        #Start to populate our PhoneCall object                
        call = PhoneCall(
                         service        = call_info['provider'],
                         account_id     = call_info['account_id'], #TODO: No.
                         call_id        = call_id, #We grabbed this above.
                         )
        
    #Now, increasing difficulty: let's handle the From and To numbers.
    
    #Make a dict of incoming numbers.
    #In the future we might have more than two - forwarded from, forwarded to, transfered from, transfered to, etc.
    incoming_numbers = {
                        'caller' : call_info['from_caller_id'],
                        'recipient' : call_info['to_caller_id'],                        
                        }
    
    
    phone_numbers = {} #This is going to be the dictionary of the phone numbers pertaining to this call.
    
    #Are either of these already in the system?
    #If not we're going to make a number for them.
    #The number can be assigned to a ContactInfo object later.
    
    for (key, phone_number) in incoming_numbers.items(): #key will be 'caller', 'recipient', etc.  phone number will be the number.
        phone_number_object, is_this_a_new_number = get_or_create_nice_number(phone_number) 
        phone_numbers[key + '_nice'] = phone_number_object.number
        
        phone_numbers[key] = phone_number_object #Put this phone number object in the dict.            
        
        if not is_this_a_new_number:
            phone_numbers[key].unknown = True #This number is unknown.  We'll want to know that for the template.

    #Save the numbers (but not their owners) as part of the call.            
    call.from_number = phone_numbers['caller']
    call.to_number = phone_numbers['recipient']
  
    call.save()
    
    #Determine if there's a user with the same number as either the caller or the recipient and isolate them.    

    if phone_numbers['caller'].owner:
        #TODO: Handle situations where a user represents a party
        CommunicationInvolvement.objects.create(person=phone_numbers['caller'].owner.userprofile.user, communication=call, direction="from") 

    try:    
        CommunicationInvolvement.objects.create(person=phone_numbers['recipient'].owner.userprofile.user, communication=call, direction="to")
    except (UserProfile.DoesNotExist, AttributeError): #Either the owner is None or the UserProfile doesn't exist.
        pass
    
    #If this this is the first time we've seen the call marked completed, we'll set the ended date.
    if call_info['status'] == 'completed' and not call.ended:
        call.ended = datetime.datetime.now()

    return call

def place_conference_call_to_dial_list(call_id, dial_list_id):
    dial_list = DialList.objects.get(id=dial_list_id)
    call = PhoneCall.objects.get(id=call_id)
    provider = call.service
    active_numbers = dial_list.get_active_numbers() 
    
    for participant in active_numbers:  # Place a call to each active number
        place_deferred_outgoing_conference_call(provider=provider, participant=participant, conference_id=call.id)
    return True

def proper_verbage_for_final_call_connection(call, response_object, announce_caller=False):
    '''
    Dehydration function for language to speak to picker-upper of a phone call.
    
    announce_caller is defaulted to true here to let the answerer know who is calling...lets fix the issue that requires this to be true.
    
    Takes a call and a generic response, appends the response with the appropriate say.
    Returns True on success.
    '''
    final_warning = 'Connected. ' #Start constructing the final message to be delivered to the answerer.
    
    if announce_caller:
        final_warning += call.announce_caller()
        
    current_participants = call.participants.filter(direction="to")
    if current_participants: #If there are current participants, we want to make that clear to the answerer.
        final_warning += 'Also on the call:'
        for participant in current_participants:
            final_warning += str(participant.person.first_name) + ','                
        voice = "Victor"
    else:
        final_warning += comm_settings.SLASHROOT_EXPRESSIONS['first_answerer_alert']
        voice = "Allison"
        
    response_object.say(final_warning, voice = voice)
    return True

@permission_required('comm.change_phonecall')
def list_phone_calls_by_phone_number(request, phone_number_id):
    phone_number = PhoneNumber.objects.get(id = phone_number_id)

    calls = get_phone_calls_by_phone_number(phone_number)

    return render(request, 'comm/list_phone_calls.html', locals())
