from .forms import TaskForm, TaskPrototypeNameForm, TaskPrototypeForm, \
    GenerateTaskForm, RestOfTheTaskPrototypeForm
from .models import Task, TaskProgeny, Verb, TaskPrototype, TaskPrototypeProgeny, \
    TaskOwnership, TaskResolution, TaskAccessPrototype, TaskAccess, Protocol
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max, Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader, Context, Template, RequestContext
from django.utils import simplejson
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.cache import never_cache
from what_apps.presence.models import SessionInfo
from taggit.models import Tag
from twilio.util import TwilioCapability
from what_apps.utility.forms import AutoCompleteField
from what_apps.mellon.models import Privilege, get_privileges_for_user
from what_apps.people.models import GenericParty
from what_apps.social.forms import DrawAttentionAjaxForm, MessageForm
from what_apps.social.models import TopLevelMessage
from what_apps.social.views import post_top_level_message
import stomp
import json








#from twilio.Utils import token

T = ContentType.objects.get_for_model(Task)

@login_required
def landing(request):
    tasks = Task.objects.can_be_seen_by_user(request.user).order_by('-created')
    manual_tasks = tasks.filter(ownership__isnull = True).exclude(creator__username = "AutoTaskCreator")[:10]
    task_messages = TopLevelMessage.objects.filter(content_type = T).order_by('-created')[:7]
    
    return render(request, 'do/do_landing.html', locals())

def public_list(request):
    '''
    Displays tasks that are viewable with the privilege "Anybody in <group_name>"
    '''
    
    if not request.user.is_authenticated():
        try:
            group_name = request.GET['group']
        except MultiValueDictKeyError:
            return HttpResponseRedirect('/presence/login?next=/do/public_list/')
        group = Group.objects.get(name=group_name)
        privilege = get_object_or_404(Privilege, prototype__name="Anybody", jurisdiction=group)
        access_objects = TaskAccess.objects.filter(prototype__privilege = privilege)
        verbs = Verb.objects.filter(prototypes__instances__resolutions__isnull = True).annotate(num_tasks=Count('prototypes__instances')).order_by('-num_tasks')
      
    else:
        verbs = Verb.objects.filter(prototypes__instances__resolutions__isnull = True).annotate(num_tasks=Count('prototypes__instances')).order_by('-num_tasks')
             
    tags = Tag.objects.filter(taggit_taggeditem_items__content_type = T).distinct() #TODO: Privileges
    
    
        
    
    return render(request, 
          'do/three_column_task_list.html', 
          locals()
          )

@never_cache
@login_required
def big_feed(request):
    '''
    Look at the big board! They're gettin' ready to clobber us!
    '''
    user_privileges = get_privileges_for_user(request.user)
    
    tasks = Task.objects.filter(access_requirements__prototype__privilege__in = user_privileges, resolutions__isnull = True).order_by('-created')[:10]
    
    
    ownerships = list(TaskOwnership.objects.filter(task__resolutions__isnull=True).order_by('-created')[:10])
    task_messages = list(TopLevelMessage.objects.filter(content_type = T))
    task_resolutions = list(TaskResolution.objects.order_by('-created')[:10])
    sessions = list(SessionInfo.objects.order_by('-created')[:10])
    
    task_activity = task_messages + task_resolutions + ownerships + sessions
    sorted_task_activity = sorted(task_activity, key=lambda item: item.created, reverse=True)[:10]
        
    activity_list = []
    
    for item in sorted_task_activity:
        activity_list.append((item, str(item._meta).split('.')[1]))
    
    return render(request,
                  'do/do_news_feed.html',
                  locals()
                  )
    

#def three_column_task_list(request):
#    
#    verbs = Verb.objects.annotate(tasks = Count('prototypes__instances')).order_by('-tasks')
#    
#    return render(request, 
#              'do/three_column_task_list.html', 
#              locals()
#              )

@login_required
def task_profile(request, task_id):
    
    
    task = get_object_or_404(Task, id = task_id)

    #It wasn't bad enough that the actual create form was wet and silly.  Now this too.  TODO: FIX THIS FUCKER.
    user_can_make_new_prototypes = True #TODO: Turn this into an actual privilege assessment
    task_prototype_name_form = TaskPrototypeNameForm()
    
    task_prototype_name_form.fields['name'].widget.attrs['class'] = "topLevel" #So that we can recognize it later via autocomplete.
    
    rest_of_the_task_prototype_form = RestOfTheTaskPrototypeForm()
    
    user_privileges = get_privileges_for_user(request.user)
    
    #Wet and silly.  TODO: Fix
    class SimpleChildForm(forms.Form):
        child = AutoCompleteField(models = (TaskPrototype,), name_visible_field=True)
    
    class SimpleParentForm(forms.Form):
        parent = AutoCompleteField(models = (TaskPrototype,), name_visible_field=True)
    
    task_prototype_form = TaskPrototypeForm()
    
    task_prototype_parent_form = SimpleParentForm()
    task_prototype_child_form = SimpleChildForm()
    
    draw_attention_ajax_form = DrawAttentionAjaxForm()
        
    if task.prototype.id == 251 or task.prototype.id == 7:
        
        has_outgoing_call = True
        disable_incoming_calls = True        
        account_sid = "AC260e405c96ce1eddffbddeee43a13004"
        auth_token = "fd219130e257e25e78613adc6c003d1a"
        capability = TwilioCapability(account_sid, auth_token)
        capability.allow_client_outgoing("APd13a42e60c91095f3b8683a77ee2dd05")
        
        
        #The text of the call recipient will be the name of the person in the case of a tech job.  It will be the output of the unicode method of the PhoneNumber in the case of a PhoneCall resolution.
        if task.prototype.id == 251:
            call_to_name = task.related_objects.all()[0].object.get_full_name()
            related_user = task.related_objects.all()[0].object
            phone_numbers = task.related_objects.all()[0].object.userprofile.contact_info.phone_numbers.all()
        if task.prototype.id == 7:
            phone_numbers = [task.related_objects.all()[0].object.from_number]            
            if task.related_objects.all()[0].object.from_number.owner:
                call_to_name = task.related_objects.all()[0].object.from_number.owner
            else:
                call_to_name = "Phone Number #%s" % (str(task.related_objects.all()[0].object.id))


    
    return render(request, 
                  'do/task_profile.html', 
                    locals() 
                  )
    

@login_required
def task_prototype_profile(request, task_prototype_id):
    '''
    Profile page for Task Prototypes.
    
    Allows editing, adding of children or parents, merging / evolving, etc.
    '''
    tp = get_object_or_404(TaskPrototype, id = task_prototype_id)
    
    task_prototype_form = TaskPrototypeForm(instance=tp)
    
    generate_form = GenerateTaskForm()
    
    return render(request, 'do/task_prototype_profile.html', locals())

#TODO: Security
def own_task(request, task_id):
    task = Task.objects.get(id=task_id)
    ownership, newly_owned = task.ownership.get_or_create(owner=request.user)
    
    t = loader.get_template('do/task_box.html')
    c = RequestContext(request, {'task':task})
    
    
    if not task.access_requirements.exists(): #We only want to push publically viewable tasks.
    
        #Pushy Stuff
        conn = stomp.Connection()
        conn.start()
        conn.connect()
    
        task_box_dict = {
                         'verb_id': task.prototype.type.id, 
                         'task_id': task.id, 
                         'box': t.render(c),
                         }
    
        conn.send(simplejson.dumps(task_box_dict), destination="/do/new_tasks")          

    
    response_json = { 'success': 1, 'newly_owned':newly_owned, 'task_id': task.id, 'box': t.render(c) } 
    
    
    
    return HttpResponse( json.dumps(response_json) )

def get_taskbox_toot_court(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'do/task_box.html', locals())
    
    

#TODO: Ensure permissions
def create_task(request):
    '''
    This is one of the worst views I have ever written.  -Justin
    '''
    user_can_make_new_prototypes = True #TODO: Turn this into an actual privilege assessment
    task_prototype_name_form = TaskPrototypeNameForm()
    
    task_prototype_name_form.fields['name'].widget.attrs['class'] = "topLevel" #So that we can recognize it later via autocomplete. TODO: DO this in the form object.
    
    rest_of_the_task_prototype_form = RestOfTheTaskPrototypeForm() #TODO: Can we please. please.  please make this one object.
    
    #Wet and silly.  TODO: Fix
    class SimpleChildForm(forms.Form):
        child = AutoCompleteField(models = (TaskPrototype,), name_visible_field=True)
    
    class SimpleParentForm(forms.Form):
        parent = AutoCompleteField(models = (TaskPrototype,), name_visible_field=True)
    
    task_prototype_form = TaskPrototypeForm()
    
    task_prototype_parent_form = SimpleParentForm()
    task_prototype_child_form = SimpleChildForm()
    
    user_privileges = get_privileges_for_user(request.user)
    
    try: #WHAT ON GODS GREEN FUCKING SERVER IS HAPPENING HERE
        task_prototype_form.fields['name'].initial = request.GET['name']
    except:
        pass
    
    return render(request, 'do/create_task_prototype.html', locals())

def task_form_handler(request):
    '''
    Deal with the task form.  There's a lot of stuff that needs tweaking in here.
    '''
    
    task_prototype_name_form = TaskPrototypeNameForm()
    
    name = request.POST['lookup_name'] #Set the name to the actual lookup field TODO: Yeah... have we checked that this form is valid?  Do we care?
    
    #Now let's figure out if they are trying to create a new prototype or just a new task.
    try:
        this_tp = TaskPrototype.objects.get(name=name)
        new = False
    except TaskPrototype.DoesNotExist:
        verb = Verb.objects.get(id=request.POST['type'])
        this_tp = TaskPrototype.objects.create(name=name, type=verb, creator=request.user)
        new = True
        
    if not new:
        #If this TaskPrototype is not new, all we're going to do is generate its task.
        task = this_tp.instantiate(request.user) #Generate the task with the current user as the creator
    if new:
        #Figure out the relations that were entered.  We'll only do that for existing TaskPrototypes.
        relations = ['parent', 'child']        
        for relation in relations:
            counter = 1
            suffix = relation #For the first iteration, we need it to just say "parent"
            while True:
                try:                
                    if request.POST['lookup_' + suffix]:
                        autocompleted_object = task_prototype_name_form.fields['name'].to_python(request.POST[suffix]) #Use the autocopmlete field's to_python method to grab the object 
                        if autocompleted_object: 
                            related_object = autocompleted_object
                        else: #They didn't successfully autocomplete; looks like we're making an object up unless the name happens to be an exact match.
                            what_they_typed = request.POST['lookup_' + suffix]
                            related_object, is_new = TaskPrototype.objects.get_or_create(name =  what_they_typed, defaults={'type': this_tp.type, 'creator': request.user})
                        
                            
                        
                        #At this point in the function, we now know for sure what the related object is.  Either they autocompleted, typed a name that matched but didn't autocopmlete, or they're making a new one.
                        
                        if relation == "child":                    
                            parent = this_tp
                            child = related_object
                            priority = (counter * 5)                            
                        if relation == "parent":
                            parent = related_object
                            child = this_tp
                            current_max_priority_ag = related_object.children.all().aggregate(Max('priority'))
                            current_max_priority = current_max_priority_ag['priority__max']
                            try:
                                priority = int(current_max_priority) + 5 #Try setting the priority to the highest priority plus 5
                            except TypeError:
                                priority =  5 #Fuck it, there is no priority at all; we'll start it at 5        
                            
                        TaskPrototypeProgeny.objects.create(parent = parent, child = child, priority = priority )
                                                    
                    else:
                        break
                except MultiValueDictKeyError:
                    break
                
                counter += 1
                suffix = relation + str(counter) #Preparing for the second iteration, it says "parent1"
        try:
            if request.POST['no_generate']: #They clicked 'prototype only,' so they don't want us to run .instantiate()
                pass
        except: #They didn't click "prototype only," thus they want the Task to be generated.
            task = this_tp.instantiate(request.user) #Generate the task with the current user as the creator
            
            #Now we'll deal with the access requirements.
            privilege = Privilege.objects.get(id = request.POST['access_requirement'])        
            task_access_prototype = TaskAccessPrototype.objects.get_or_create(privilege = privilege, type=5)[0] #Hardcoded 5 - this ought to be an option in the form
            task_access = TaskAccess.objects.create(prototype=task_access_prototype, task = task)
        
        #I mean, seriously, shouldn't this be a post-save hook?            
        if task:
            messages.success(request, 'You created <a href="%s">%s</a>.' % (task.get_absolute_url(), this_tp.name)) #TODO: Distinguish messages between creation of TaskPrototype and Task objects.
        else:
            messages.success(request, 'You created %s.' % this_tp.name) #TODO: Distinguish messages between creation of TaskPrototype and Task objects.
        
    #We may have arrived here from the Task Profile form or some other place where at least one parent is certain.  Let's find out.
    try:
        parent_ipso_facto_id = request.POST['parentIdIpsoFacto']
        parent_task = Task.objects.get(id=parent_ipso_facto_id) #By jove, it's tru!  Our new task already has a parent Task.
        
        current_max_priority_ag = parent_task.children.all().aggregate(Max('priority'))
        current_max_priority = current_max_priority_ag['priority__max']
        
        try: #TODO: Boy, it's started to feel like we need a max_priority method, eh?
            priority = int(current_max_priority) + 5 #Try setting the priority to the highest priority plus 5
        except TypeError:
            priority =  5 #Fuck it, there is no priority at all; we'll start it at 5     
        
        task_progeny = TaskProgeny.objects.create(parent=parent_task, child=task, priority = priority)
        return HttpResponseRedirect(parent_task.get_absolute_url())
    except MultiValueDictKeyError:
        pass #Nope, guess not.
    
    return HttpResponseRedirect('/do/create_task') #TODO: Dehydrate this using the reverse of the create task view.
    
@login_required
def new_child_ajax_handler(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        #First create the child task.
        new_child_task = form.save()
        
        #Now create the relationship to the parent.
        try:
            parent_id = request.POST['parent_id']
            parent_task = Task.objects.get(id = parent_id)
            
            siblings = parent_task.children.all() #Siblings of the task we just created
            highest_order_rank = siblings.aggregate(Max('order_rank'))['order_rank__max']
            if highest_order_rank:
                new_order_rank = highest_order_rank + 1
            else:
                new_order_rank = 1
            
            hierarchy = TaskProgeny.objects.create(child = new_child_task, parent = parent_task, order_rank = new_order_rank)
            
            return HttpResponse(1)
        
        except IndexError:
            raise RuntimeError('The Parent ID got yanked from the form.  Not cool.')
            
        
        
        
    else:
        #TODO: This is an exact repeat of the invalid handler in utility.views.submit_generic.  DRY it up.
        errors = []
        for error in form.errors:
            errors.append(error)
        dumps = simplejson.dumps(errors)
        return HttpResponse(dumps)

#TODO: Check that the user has proper authority
def task_family_as_checklist_template(request):
    '''
    Takes a Task or TaskPrototype and returns the children as a checklist template. 
    
    I don't love this function.  It can be far more generic and helpful with a little tinkering.  -Justin
    
    '''
    is_prototype = request.GET['is_prototype'] #Are we looking for a Task or a TaskPrototype?
    id = request.GET['id']
    
    try:
        number_to_show = request.GET['limit'] #Maybe they specified a number of children to list....
    except KeyError:
        number_to_show = False #....maybe they didn't.
    
    task_maybe_prototype_model = TaskPrototype if is_prototype else Task
    task_maybe_prototype = task_maybe_prototype_model.objects.get(id=id)
    model_name = task_maybe_prototype_model.__name__
    
    progeny_objects = task_maybe_prototype.children.all()
    
    if number_to_show:
        progeny_objects = progeny_objects.limit(number_to_show)
        
    return render(request, 'do/children_checklist.html', locals())

def task_prototype_list(request):
    
    task_prototypes = TaskPrototype.objects.all()

    return render(request, 'do/task_prototype_list.html', locals())


def get_people_for_verb_as_html(request, verb_id):
    '''
    Shows peoples' names in the public list page.
    '''
    verb = Verb.objects.get(id=verb_id)
    people = verb.users_who_have_completed_tasks()
    
    
    return render(request, 'do/people_list.html', locals() )


def get_tasks_as_html(request, object_id, by_verb=True, mix_progeny=False):
    '''
    Ajax specialized method that returns, in HTML, all the tasks to which a user has access within a specific verb or tag.
    
    If verb is true, get by task.  Otherwise, by tag.
    
    Typical use case is a refresh signal sent by the push module or a click on the "three columns" page.
    '''
    if not by_verb:
        tag = Tag.objects.get(id=object_id)
        tagged_tasks = tag.taggit_taggeditem_items.filter(content_type = T) #TODO: Apply privileges
    
    
    if not request.user.is_authenticated():
        group_name = request.GET['group']
        group = Group.objects.get(name=group_name)
        privilege = get_object_or_404(Privilege, prototype__name="Anybody", jurisdiction=group)
        access_objects = TaskAccess.objects.filter(prototype__privilege = privilege)
        access_tasks = Task.objects.filter(access_requirements__in = access_objects, resolutions__isnull=True).distinct()
        
        if by_verb:
            verb = Verb.objects.get(id=object_id)        
            tasks = access_tasks.filter(prototype__type = verb)
        else:
            tasks_from_tag = tagged_tasks.filter(task__access_requirements__in = access_objects, resolutions__isnull=True).distinct()
            tasks = set()
            for task_from_tag in tasks_from_tag:
                tasks.add(task_from_tag.content_object)
        
    else: #They're logged in.
        if by_verb:
            verb = Verb.objects.get(id=object_id)        
            tasks = verb.get_tasks_for_user(request.user)    
        else:
            tasks_from_tag = tagged_tasks #TODO: Again, privileges
            tasks = set()  
            for task_from_tag in tasks_from_tag:
                if task_from_tag.content_object.resolutions.count() == 0:
                    tasks.add(task_from_tag.content_object)
    
    if not mix_progeny:
        #Let's make sure that no child task is listed alongside its parent.
        
        tasks_to_remove = set()                
        for task in tasks:
            for progeny in task.parents.all():
                if progeny.parent in tasks:
                    tasks_to_remove.add(task)
        
                
        task_set = set(tasks) - tasks_to_remove
                    
        tasks = task_set        
    
    return render(request, 'do/task_list.html', locals())
    

#TODO: Security
def mark_completed(request, task_id):
    task = Task.objects.get(id=task_id)
    resolution = TaskResolution.objects.create(task=task, type="C", creator=request.user)
    return HttpResponse(1)

def mark_abandoned(request):
    
    return HttpResponse(1)

def update_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.update_to_prototype(user=request.user)
    return redirect(task.get_absolute_url())

@login_required
def post_task_message(request, task_id):
    '''
    Take a message about a task.  See if the task is complete and mark it so if so.
    If the message field is not blank, send it to the social view to handle the text of the message.
    '''
    task = Task.objects.get(id=task_id)
    try:
        if request.POST['completed']:
            task.set_status(2, request.user)

    except MultiValueDictKeyError:
        pass #They didn't mark it completed, no need to think about it further.
    
    if request.POST['message']:
        post_top_level_message(request, 'do__task__%s' % (task_id))
    
    return HttpResponseRedirect(task.get_absolute_url())
    
def protocols(request):
    '''
    SlashRoot's policies, procedures, and protocols listed here. 
    Perhaps this will be eliminated once we get the organization of tasks under better control since most of these will be tasks.
    '''
    protocols = Protocol.objects.all()
    
    return render(request,'do/protocols.html',{'protocols':protocols})

def archives(request):
    
    #completed_tasks = TaskResolution.objects.filter(type='C').order_by('-created')
    tasks = SERVICE_PROTOTYPE.instances.filter(status__gt=1).all()

    return render(request, 'do/archives.html', locals())