from .forms import DrawAttentionAjaxForm, MessageForm
from .models import DrawAttention, TopLevelMessage, Acknowledgement, \
    FileAttachedToMessage, TopLevelMessageManager
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.utils import simplejson
from what_apps.do.models import Task, TaskResolution
from what_apps.people.models import UserProfile, GenericParty, Group
from what_apps.presence.models import AnchorTime, MediaURL
from what_apps.social.functions import get_messages_for_user
import datetime
import json


def draw_attention_ajax(request):
    form = DrawAttentionAjaxForm(request.POST)
    
    form.full_clean()
    
    if form.is_valid():
    
        app_name = form.cleaned_data['app']
        object_type = form.cleaned_data['model']
        object_id = form.cleaned_data['object_id']
        Model=ContentType.objects.get(app_label=app_name, model=object_type.lower()).model_class()
        object = Model.objects.get(id=object_id)
        
    
        target = form.cleaned_data['share_with']
    
        DrawAttention.objects.create(
                                         creator = request.user,
                                         target = target,
                                         content_object = object,
                                         )
        
        object.save() #Cause any post-save hooks to fire.
        
        alert_message = "You have alerted %s to %s." % (target, object)
        response_dict = dict(success=True, alert=alert_message)
        response_dict_json = json.dumps(response_dict)
        
        return HttpResponse(response_dict_json)
    
    else:
        errors = []
        for error in form.errors:
            errors.append(error)
        dumps = simplejson.dumps(errors)
        return HttpResponse(dumps)


@login_required
def dashboard(request):
    tasks = Task.objects.filter(ownership__owner=request.user, resolutions__isnull = True).reverse()[:5]
    completed = TaskResolution.objects.filter(creator=request.user, type=2).reverse()[:10]
    points_aggregate = Task.objects.filter(resolutions__creator=request.user, resolutions__type=2).aggregate(Sum('weight'))
    points = points_aggregate['weight__sum']
    anchors = AnchorTime.objects.filter(member=request.user)
    count = get_messages_for_user(request.user)
    inbox_messages = get_messages_for_user(request.user)[-5:]
    try:
        media = MediaURL.objects.get(pk=1)
    except:
        pass 
    unnecessary = True #Removes the login box without affecting the entire brown_and_bubble_driven template so that it looks more appealing in the dashboard
    
    user_party = GenericParty.objects.get(party=request.user)
    
    log_for_user = TopLevelMessage.objects.complete_log(party=user_party).order_by('-created')[:10]
    
    return render(request, 'social/dashboard.html', locals())


def profile(request, username):        
    person = get_object_or_404(User, username = username)
    completed = TaskResolution.objects.filter(creator=person, type=2).reverse()[:10]
    return render(request, 'social/profile.html',locals())


def post_top_level_message(request, object_info):
    app_name = object_info.split('__')[0]
    model_name = object_info.split('__')[1]
    object_id = object_info.split('__')[2]
    Model = ContentType.objects.get(app_label=app_name, model=model_name.lower()).model_class()
    object = Model.objects.get(id=object_id)
    
    if request.POST['message']:
        message = TopLevelMessage.objects.create(content_object = object, creator=request.user, message=request.POST['message'])
        
    if request.FILES:
       
        for filename, file_object in request.FILES.items():            
            FileAttachedToMessage.objects.create(message=message, creator=request.user, file=file_object)
            
    return HttpResponseRedirect(object.get_absolute_url())


def acknowledge_notification(request, attention_id):
    attention = DrawAttention.objects.get(id=attention_id)
    attention.acknowledge()
    
    
    #TODO: Maybe the pushy stuff?
    
    return HttpResponse(json.dumps({'success': True}))

@login_required
def log(request, username=None, group_name=None):
    
    if request.POST: #they are trying to post a log.
        form = MessageForm(request.POST)
        if form.is_valid():
            message_kwargs = { #This will become the kwargs of our create method.
                              'user': request.user,
                              'message': form.cleaned_data['message']
                              }
            
             
            
            if group_name: #They're trying to post to a group.        
                group = get_object_or_404(Group, name=group_name) #Let's make sure the group exists.
                message_kwargs['group'] = group #Add the group to the message kwargs.
     
            message = TopLevelMessage.objects.make_log(**message_kwargs)
            
            if not message: #message will be False if the User is not a member of the group.
                return HttpResponseForbidden()
        
    else: #No POST.
        form = MessageForm()
        #Three scenarios: They specified a group, or a user, or neither.  For neither, we give them the log landing page.

#TODO:
#        if not username and not group_name:
#            return render(request, 'social/log_landing.html', locals())        
        if group_name:
            log_owner = get_object_or_404(Group, name=group_name)
            if not request.user in log_owner.users().all():
                return HttpResponseForbidden()
        if username:
            if username == request.user.username:
                log_owner = User.objects.get(username=username)
            else:
                return HttpResponseForbidden()
        
        log_party = GenericParty.objects.get(party=log_owner)
            
        
    return render(request, 'social/log.html', locals())
    
def media_player(request):
    return render(request, 'social/media_player.html', locals())
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    