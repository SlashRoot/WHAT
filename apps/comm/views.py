from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.contrib.auth.decorators import user_passes_test, permission_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


from comm.comm_settings import SLASHROOT_EXPRESSIONS

from contact.models import PhoneNumber, DialList, PhoneProvider

import requests
import urlparse

from comm.models import PhoneCall, PhoneCallRecording, CommunicationInvolvement
from comm.services import get_provider_and_response_for_request,\
    standardize_call_info, random_tropo_voice,\
    discern_intention_to_connect_from_answerer,\
    discern_destination_from_tropo_request, \
    SLASHROOT_TWILIO_ACCOUNT, extract_transcription_as_text,\
    get_audio_from_provider_recording
from comm.call_functions import call_object_from_call_info, proper_verbage_for_final_call_connection, get_or_create_nice_number,\
    place_conference_call_to_dial_list
from people.models import UserProfile, Member
import datetime

from do.functions import get_tasks_in_prototype_related_to_object
from twilio import twiml
from utility.models import FixedObject
from django.core.mail.message import EmailMultiAlternatives


CUSTOMER_SERVICE_PRIVILEGE_ID = 8

from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType

from twisted.internet import reactor

import os
import json

#TODO: Un-hardcode email to SMS
PHONE_DISPATCH_RECIPIENTS = ['justin@justinholmes.com',
                             ]


@require_http_methods(["POST"])
@csrf_exempt
def answer(request, this_is_only_a_test=False):
    '''
    The first response to a basic incoming call.  Can take requests from multiple providers.
    '''
    #First, let's figure out which provider is making this request.
    provider, r = get_provider_and_response_for_request(request) #Now we have a response object that we can use to build our response to the provider.
    
    #Now we need a call object with the appropriate details, regardless of the provider.
    call_info = standardize_call_info(request, provider=provider)
    call = call_object_from_call_info(call_info) #Identify the call, saving it as a new object if necessary.
    
    
    r.say(SLASHROOT_EXPRESSIONS['public_greeting'], voice=random_tropo_voice()) #Greet them.
    
    r.conference_holding_pattern(call.call_id, call.from_number, "http://hosting.tropo.com/97442/www/audio/mario_world.mp3") #TODO: Vary the hold music
    
    dial_list = DialList.objects.get(name="SlashRoot First Dial")
    
    if not this_is_only_a_test:
        #if it is only a test users' phones will not ring
        reactor.callFromThread(place_conference_call_to_dial_list, call.id, dial_list.id) #Untested because it runs in twisted. TOOD: Ought to take a DialList as an argument

    return r.render()



@csrf_exempt
def conference_blast(request):
    '''
    Places the outgoing call to somebody who might pick up.
    We have a branch here regarding whether the picker-upper is a green phone.
    If they are and they pick up, connect them to the call quickly.
    If they aren't and they pick up, send a request to the alert_pickup function.
    '''
    provider, r = get_provider_and_response_for_request(request)
    
    try: #Prevent 500s from simply browsing to the URL.
        number_object, phone_call_object, is_green_phone = discern_destination_from_tropo_request(request)
    except ValueError:
        return HttpResponseNotAllowed(['POST'])
    
    nicer_number = number_object.number[0:3] + number_object.number[4:7] + number_object.number[8:12]
    
    r.call(to = nicer_number, timeout=24, caller_id='18456338330') #TODO: Capitalization is Tropo convention.  Abstract in response class.
    r.on("incomplete", next="/comm/alert_timeout/") #TODO: Slightly TROPO coupled.  Let's fix this.
    if is_green_phone:
        #If they are the green phone, don't make them say the confirmation phrase.
        r.on("continue", next="/comm/pickup_connect_auto/%s/%s/" % (number_object.id, phone_call_object.id))
    else:
        r.on("continue", next="/comm/alert_pickup/%s/%s/" % (number_object.id, phone_call_object.id))
    
    return r.render()

@csrf_exempt
def alert_pickup(request, number_id, call_id):
    '''
    Somebody has in has picked up a call - now they can decide whether to answer or not.
    '''
    provider, r = get_provider_and_response_for_request(request)
    call = PhoneCall.objects.get(id = call_id)
    
    inquiry = call.announce_caller()
        
    try:
        call_participants = call.participants.filter(direction="to")
        if call_participants:
            inquiry += "Also on the call: "
            voice = "Victor"
            for involvement in call_participants:
                inquiry += " %s, " % str(involvement.person.first_name)
        else:
            voice = "Allison"
        
    except PhoneCall.DoesNotExist:#    r.transfer('+1845-204-3574')
#    return r.render()
        pass #raise ReallyFuckedUpError or provide some kind of path to a decent outcome
    
    r.ask(choices = "0,1,2,3,4,5,6,7,8,9,%s" % SLASHROOT_EXPRESSIONS['phrase_to_answer_call'], timeout=10, name="response", say = inquiry, attempts=20, minConfidence=37, voice = voice)
    r.on(event = "continue", next ="/comm/pickup_connect/%s/%s/" % (number_id, call.id) ) #We need to tell them the number, call id, and number of current participants
    
    return r.render()

@csrf_exempt
def pickup_connect(request, number_id, call_id, connect_regardless=False):
    '''
    Checks to see if the answerer indicated that they wanted to answer, and creates a new call object and connects them if so.
    '''
    provider, r = get_provider_and_response_for_request(request)
    call = PhoneCall.objects.get(id = call_id)
    
    try: #This is somebody who is answering our call.  We damn well better know what this number is and to whom is belongs.
        answerer_number = PhoneNumber.objects.get(id=number_id)
        answerer_user = answerer_number.owner.userprofile.user 
    except (PhoneNumber.DoesNotExist, UserProfile.DoesNotExist), e:
        #raise ReallyFuckedUpError
        raise
    
    if not connect_regardless: #If connect regardless is false, we still might answer if they answered with the correct phrase.
        #TODO: Turn this into a "prevent default" decorator
        try: #Prevent 500s from simply browsing to the URL.
            affirmative_consent = discern_intention_to_connect_from_answerer(request, provider)
        except ValueError:
            return HttpResponseNotAllowed(['POST'])

        
    if connect_regardless or affirmative_consent:
        proper_verbage_for_final_call_connection(call, r) #Appends the appropriate say to the response
        
        if not call.has_begun():
            r.join_and_begin_conference(conference_id = call.call_id, number=answerer_number)
        else:
            r.conference(conference_id = call.call_id, number=answerer_number)
         
        #Create a participant object for this answerer (they are receiving the call, so it's "to" them)   
        call.participants.create(person=answerer_user, direction="to")
        
        #Make sure the answerer is an owner of the task and it's tagged "answered."
        task = call.resolve_task()
        task.ownership.create(owner=answerer_user)
        task.tags.add("answered") #TODO: Maybe move this into the branch above (call.has_begun()) so that we only tag the task once.
        
        #Send an email to this user with a link to the Task.
        
        #We want to include the caller in the subject, so we'll grab their PhoneNubmer object now.        
        caller_number = call.from_number
        subject = "Call from %s" % str(caller_number)
        from_email = "phonecalldispatch@slashrootcafe.com"
        recipient_list = [answerer_user.email]
        
        #We also want to inform the caller of the other unresolved calls.
        resolve_protoype = FixedObject.objects.get(name="TaskPrototype__resolve_phone_call").object
        number_of_unresolved_calls = resolve_protoype.instances.filter(resolutions__isnull=True).exclude(id=2686).count() #TODO: Explain to the people WHY the fuck we are excluding 2686.
        
        message = '<a href="http://slashrootcafe.com%s">Resolve This Call</a>\n\n<a href="http://slashrootcafe.com/comm/resolve_calls/">(%s other unresolved calls)</a>' % (task.get_absolute_url(), number_of_unresolved_calls)
        
        msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
        msg.attach_alternative(message, "text/html")
        msg.send()
        
    return r.render()


@csrf_exempt
def handle_hangup(request, conference_id, number_id):
    r = get_provider_and_response_for_request(request)[1]
    phone_call_object = PhoneCall.objects.get(call_id=conference_id)
    number_object = PhoneNumber.objects.get(id=number_id)
    
    #If the number object has an owner, their participation needs to be ended.
    if number_object.owner:
        participation = CommunicationInvolvement.objects.filter(communication__phonecall__call_id=conference_id, person=number_object.owner.userprofile.user).order_by('-created')[0]
        participation.destroyed = datetime.datetime.now()
        participation.save()
        
    #If the phone call object is that of the original caller, we can consider this phone call to be over.
    if number_object == phone_call_object.from_number:
        phone_call_object.ended = datetime.datetime.now()
        phone_call_object.save()
    
    return r.render()

@csrf_exempt
def simply_join_conference(request, conference_id, number_id):
    '''
    Just join the conference with this conference ID and start recording.
    We aren't asking for the call ID and lookup because we want to avoid the extra DB hit.  This can be hosted on Tropo scripting, cached with varnish, or whatever we might imagine.
    '''
    provider, r = get_provider_and_response_for_request(request)
    number = PhoneNumber.objects.get(id=number_id)
    r.conference(conference_id = conference_id, number=number, record=True)
    return r.render()

@csrf_exempt
def transcription_handler(request, object_type, id):
    provider, r = get_provider_and_response_for_request(request)
    transcription_text = extract_transcription_as_text(request, provider)
    
    #Now we need to figure out whether we already have a recording object to pair it with.
    if object_type == "recording":
        recording_object = PhoneCallRecording.objects.get(id=id)
    else:
        recording_object = PhoneCallRecording.objects.create(call_id = id)
    
    recording_object.transcription_text = transcription_text
    recording_object.save()
    
    return r.render()

@csrf_exempt
def recording_handler(request, object_type, id):
    '''
    Handles the mp3 file, send by tropo in the request.
    '''
    provider, r = get_provider_and_response_for_request(request)
    #First we'll save the MP3 file.
    file = get_audio_from_provider_recording(request, provider)
    
    #Now we need to figure out whether we already have a recording object to pair it with.
    if object_type == "recording":
        recording_object = PhoneCallRecording.objects.get(id=id)
    else:
        call = PhoneCall.objects.get(call_id=id)
        recording_object = PhoneCallRecording.objects.create(call=call)
    
    recording_object.audio_file = file.name
    recording_object.save()
    
    return r.render()

def simple_phone_lookup(request):
    phone_number, created = get_or_create_nice_number(request.GET['phone_number'])
    if phone_number.owner:
        return HttpResponse(str(phone_number.owner))
    else:
        if created:
            return HttpResponse('unlogged new number')
        else:
            return HttpResponse('unlogged old number')


def outgoing_call_menu(request):
    outgoing_number = request.GET['phone_number']
    outgoing_number_object = PhoneNumber.objects.get(id=outgoing_number)
    eligible_members = Member.objects.exclude(user__userprofile__contact_info__phone_numbers = None) #Members who have a phone number
    
    eligible_numbers = []
        
    for member in eligible_members:
        for phone_number in member.user.userprofile.contact_info.phone_numbers.all():
            eligible_numbers.append([phone_number.id, phone_number.type, member.user.username, phone_number.number])
    
    #Hardcode the house line for now.
    eligible_numbers.append([687, 'house', 'SlashRoot', '845-418-5633'])
        
    return render(request, 'comm/outgoing_call_menu.html', locals()) 

def outgoing_call(request):
    '''
    Make an outgoing call.  Duh.  :-)
    
    TODO: Uncouple from Tropo
    '''
    tropo_provider = PhoneProvider.objects.get(name="Tropo")
    
    call_from_phone = PhoneNumber.objects.get(id=request.POST['callFrom'])
    call_to_phone = PhoneNumber.objects.get(id=request.POST['callTo'])

    from_number = SLASHROOT_MAIN_LINE
    
    
    response = requests.post('https://api.tropo.com/1.0/sessions/', 
                      data={
                            'token':'0aaea1598824a846a340ea4b597fc9672cfa5734fc4a2edcf8c2de5101277f765ec7e8743d379495f7969bc7', 
                            'toNumber':call_to_phone.remove_dashes(), 
                            'fromNumber':call_from_phone.remove_dashes(),
                            }
                      )
    
    session_id = urlparse.parse_qs(response.content)['id'][0].rstrip()
    
    call = PhoneCall.objects.create(service=tropo_provider, call_id=session_id, dial=True, from_number=call_from_phone, to_number=call_to_phone)
    
    task = call.resolve_task()
    task.ownership.create(owner=request.user)
        
    #Creating the call will have created a call task.
    
    return HttpResponseRedirect(task.get_absolute_url())

@permission_required('comm.change_phonecall')
def watch_calls(request):
    calls=PhoneCall.objects.filter(dial=False).order_by('created').reverse()[:25]
    return render(request, 'comm/watch_calls.html', locals() )

@permission_required('comm.change_phonecall')
def resolve_calls(request):
    resolve_protoype = FixedObject.objects.get(name="TaskPrototype__resolve_phone_call").object #SOGGY AND DISGUSTING.  Too many instaces of this string.
    tasks = resolve_protoype.instances.filter(resolutions__isnull=True).order_by('created').exclude(id=2686)[:25]
    return render(request, 'comm/resolve_calls.html', locals() )

#@csrf_exempt
#def outgoing_callback(request):
#    
#    to_number_id = request.GET['phone_number']
#    to_number = PhoneNumber.objects.get(id=to_number_id)
#
#    r = twiml.Response()
#    r.addSay('Now connecting your call.')
#    r.addDial(to_number.number, record=True, timeOut=45)
#    return response(r, mimetype='text/xml')

@permission_required('comm.change_phonecall')
def phone_call_details(request, phone_call_id):
    call = PhoneCall.objects.get(id=phone_call_id)
    return render(request, 'comm/call_alert.html', locals())

@csrf_exempt
def voicemail(request):
    provider, r = get_provider_and_response_for_request(request)
    #Now we need a call object with the appropriate details, regardless of the provider.
    call_info = standardize_call_info(request, provider=provider)
    call = PhoneCall.objects.get(call_id=call_info['call_id'])
    voicemail_recording = PhoneCallRecording.objects.create(call=call)
    
    task = call.resolve_task()
    task.tags.add("voicemail")
        
    #TODO: Find the task for this call and tag it.
    prompt = 'No SlashRoot member is available to answer your call right now.  Please leave a message and a SlashRoot member will return your call.'
    r.prompt_and_record(call_id=call.id, recording_object = voicemail_recording, format="audio/mp3", url="", transcribe=True, prompt=prompt)
    return r.render()

def review_calls_with_user(request, user_id):
    subject_user = User.objects.get(id=user_id)
    tech_jobs = get_tasks_in_prototype_related_to_object(251, subject_user)
    return render(request, 'comm/review_calls_with_user.html', locals())

@csrf_exempt
def redirect_to_tropo(request):
    provider, r = get_provider_and_response_for_request(request)
    return answer(request)
#    r.transfer('+1845-204-3574')
#    return r.render()