import urlparse
import os
import json
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User

from comm.models import PhoneCall
from comm.call_functions import get_or_create_nice_number
from comm.rest import PhoneProviderRESTObject

from do.functions import get_tasks_in_prototype_related_to_object
from utility.models import FixedObject
from utility.forms import get_bool_from_html
from private import resources
from contact.models import PhoneNumber, PhoneProvider

comm_logger = logging.getLogger('comm')

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
    
    member_role = FixedObject.objects.get(name="RoleInGroup__slashroot_holder").object
    eligible_members = member_role.users()
    
    eligible_numbers = []
    
    for member in eligible_members:
        for phone_number in member.userprofile.contact_info.phone_numbers.all():
            eligible_numbers.append([phone_number.id, phone_number.type, member.username, phone_number.number])
    
    #Hardcode the house line for now.
    eligible_numbers.append([687, 'house', 'SlashRoot', '845-418-5633'])
        
    return render(request, 'comm/outgoing_call_menu.html', locals()) 

def outgoing_call(request, phone_provider_name=None):
    '''
    Make an outgoing call.  Duh.  :-)
    
    TODO: Uncouple from Tropo
    '''
    if not phone_provider_name:
        #TODO: Get default phone provider
        pass
    else:
        phone_provider = PhoneProvider.objects.get(name=phone_provider_name)
    
    call_from_phone = PhoneNumber.objects.get(id=request.POST['callFrom'])
    call_to_phone = PhoneNumber.objects.get(id=request.POST['callTo'])

    from_number = resources.SLASHROOT_MAIN_LINE
    
    p = PhoneProviderRESTObject(phone_provider)
    
    call_id = p.place_new_call(call_from_phone, call_to_phone)
    
    call = PhoneCall.objects.create(service=tropo_provider, call_id=call_id, dial=True, from_number=call_from_phone, to_number=call_to_phone)
    
    task = call.resolve_task()
    task.ownership.create(owner=request.user)
        
    #Creating the call will have created a call task.
    
    return HttpResponseRedirect(task.get_absolute_url())

@permission_required('comm.change_phonecall')
def watch_calls(request):
    
    
    calls=PhoneCall.objects.filter(dial=False).order_by('created').reverse()
    paginator = Paginator(calls, 15)
    
    page = request.GET.get('page')
    try:
        watch_calls = paginator.page(page)
    
    except PageNotAnInteger:
        watch_calls = paginator.page(1)
    
    except EmptyPage:
        watch_calls = paginator.page(paginator.num_pages)
    
    return render(request, 'comm/watch_calls.html', locals() )

@permission_required('comm.change_phonecall')
def resolve_calls(request):
    comm_logger.info('Resolve Calls was accessed by %s.' % request.user.username)
    
    types_of_callers = ['client',
                        'member',
                        'other_known_caller',
                        'unknown_caller',
                        ]
    clients = User.objects.filter(genericparty__service__isnull=False)
    
    member_role = FixedObject.objects.get(name="RoleInGroup__slashroot_holder").object
    members = member_role.users()
    
    unknown_callers = PhoneNumber.objects.filter(owner__isnull=True)

    if not 'submitted_filter_form' in request.GET:
        calls = PhoneCall.objects.unresolved()
    
    else:
        filter_form_results = {}
        
        for direction in ['from', 'to']:
            for c in types_of_callers:
                try:
                    filter_form_results["%s_%s" % (c, direction)] = get_bool_from_html(request.GET["%s_%s" % (c, direction)])
                except KeyError:
                    filter_form_results["%s_%s" % (c, direction)] = False
                    
        try:
            filter_form_results['include_without_recordings'] = get_bool_from_html(request.GET['include_without_recordings'])
        except KeyError:
            filter_form_results['include_without_recordings'] = False
    
        if False not in filter_form_results.values():
            calls_universe = PhoneCall.objects.unresolved()
        else:
            if not filter_form_results['include_without_recordings']:
                calls_universe = PhoneCall.objects.unresolved().exclude(recordings__isnull=True)
            else:
                calls_universe = PhoneCall.objects.unresolved()
        calls = set() 
        
        #We're being subtractive, so if *both* are checked, we can move on.
        #Client
        if filter_form_results['client_to'] or filter_form_results['client_from']:
            clients = User.objects.filter(genericparty__service__isnull=False)
            calls = calls.union(calls_universe.involving(user_list=clients, 
                                            include_to=filter_form_results['client_to'],
                                            include_from=filter_form_results['client_from'],
                                            ))
            
        if filter_form_results['member_to'] or filter_form_results['member_from']:            
            calls = calls.union(calls_universe.involving(user_list=members,
                                            include_to=filter_form_results['member_to'],
                                            include_from=filter_form_results['member_from'],
                                            ))
        
        if filter_form_results['other_known_caller_to'] or filter_form_results['other_known_caller_from']:
            #Doing this by PhoneNumber.  Is there a (better?) way to do it by User?
            numbers = PhoneNumber.objects.exclude(owner__userprofile__user__in=members).exclude(owner__userprofile__user__in=clients).exclude(owner__isnull=True)
            
            if filter_form_results['other_known_caller_to']:
                calls = calls.union(calls_universe.filter(to_number__in=numbers))
            
            if filter_form_results['other_known_caller_from']:
                calls = calls.union(calls_universe.filter(from_number__in=numbers))
                
        if filter_form_results['unknown_caller_to'] or filter_form_results['unknown_caller_from']:
            if filter_form_results['unknown_caller_to']:
                calls = calls.union(calls_universe.filter(to_number__in=unknown_callers))
            
            if filter_form_results['unknown_caller_from']:
                calls = calls.union(calls_universe.filter(from_number__in=unknown_callers))
                

    paginator = Paginator(list(calls), 15)
    page = request.GET.get('page')
    
    try:
        resolve_calls = paginator.page(page)
    
    except PageNotAnInteger:
        resolve_calls = paginator.page(1)
    
    except EmptyPage:
        resolve_calls = paginator.page(paginator.num_pages)
        
    return render(request, 
                  'comm/resolve_calls.html', 
                  {
                   'resolve_calls':resolve_calls,
                   'caller_types':types_of_callers,
                   } 
                  )
    

@permission_required('comm.change_phonecall')
def resolve_call(request):
    call_id = request.POST['call_id']
    call = PhoneCall.objects.get(id=call_id)    
    
    if request.POST['complete'] == 'true':
        status = 2
    else:
        status = 1
    
    resolve_task = call.resolve_task()
    resolve_task.set_status(status, request.user)

    return HttpResponse(status)

@permission_required('comm.change_phonecall')
def phone_call_details(request, phone_call_id):
    call = PhoneCall.objects.get(id=phone_call_id)
    return render(request, 'comm/call_alert.html', locals())

def review_calls_with_user(request, user_id):
    subject_user = User.objects.get(id=user_id)
    tech_jobs = get_tasks_in_prototype_related_to_object(251, subject_user)
    return render(request, 'comm/review_calls_with_user.html', locals())