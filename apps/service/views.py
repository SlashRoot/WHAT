from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from do.models import Task, TaskPrototype, TaskRelatedObject, TaskAccess,\
    TaskAccessPrototype
from django.contrib.auth.decorators import login_required
from service.models import Service, ServiceStatusPrototype

from service.forms import MostBasicServiceCheckInForm, RateForm
from utility.models import FixedObject
from django.utils.datastructures import MultiValueDictKeyError
from social.views import post_top_level_message

@login_required
def most_basic_check_in(request):
    '''
    
    '''
    if request.POST:
        form = MostBasicServiceCheckInForm(request.POST)
        if form.is_valid():
            customer_party = form.cleaned_data['customer']
            projected = form.cleaned_data['projected']
            triage_status_object = FixedObject.objects.get(name="ServiceStatusPrototype_triage").object
            service = Service.objects.create(recipient = customer_party, status=triage_status_object)
            task = service.task
            task.tags.add('tech')
            task.tags.add('customer')

            tp = FixedObject.objects.get(name="TaskAccessPrototype__customer_service").object
            TaskAccess.objects.create(task=task, prototype=tp)
            
            return HttpResponseRedirect(task.get_absolute_url())
            
    else:
        form = MostBasicServiceCheckInForm()
    return render(request, 'service/basic_check_in_form.html', locals())   



class Column(object):
    '''
    Maybe someday this will grow into something bigger. Maybe not.
    '''
    name = "N/A"
    
    def __init__(self, name, icon=None):
        self.name = name
        
        if icon:
            self.icon = icon

class ServiceGridColumns(object):
    def __init__(self):
        self.columns = []
        self.columns.append(Column('Client Name', icon="name.png"))
        self.columns.append(Column('Devices', icon="device.png"))
        self.columns.append(Column('Members who own this Task', icon="owner.png"))
        self.columns.append(Column('When did this job ', icon="days.png"))
        self.columns.append(Column('Incoming / Outgoing Calls during this job', icon="call_history.png"))
        self.columns.append(Column('Incoming / Outgoing Calls Today', icon="call_now.png"))
        self.columns.append(Column('Messages about this job', icon="comment.png"))
        self.columns.append(Column('Most Recent Action', icon="last_action.png"))
        self.columns.append(Column('Whose Court is the Ball In?', icon="court.png"))
        self.columns.append(Column('Status', icon="status.png"))
        self.columns.append(Column('Suggested Charge', icon='suggested_price.jpg'))
        self.columns.append(Column('Customer Expectation', icon="customer_expectation.jpg"))

    
@login_required
def the_situation(request):
    
    columns = ServiceGridColumns().columns
    
    needing_attention, not_needing_attention = Service.objects.filter_by_needing_attention()
    
    suggested_price = Service.PriceTagPrototype.list_of_charges

#    tp = TaskPrototype.objects.filter(name__icontains="completed")[4]
#    tasks = tp.instances.all()
#    
#    for task in tasks:
#        user = task.related_objects.all()[0].object
#        user_gp = GenericParty.objects.get(user=user)
#        status = FixedObject.objects.get(name="service_status_triage").object
#        Service.objects.create(task=task, recipient=user_gp, status=status)
    return render(request, 'service/service_grid.html', locals())

@login_required
def archive(request):
    columns = ServiceGridColumns().columns
    not_needing_attention = Service.objects.filter(task__status__gt = 1)
    return render(request, 'service/service_grid.html', locals())

@login_required
def tickets(request, service_id):
    '''
    The profile page for an individual service ticket. 
    '''    
    status_prototypes = ServiceStatusPrototype.objects.all() #TODO: Filter for "active" statuses (ie, allow some to be retired)
    service = get_object_or_404(Service, id=service_id)
    task = service.task
    rate = RateForm()
    return render(request, 'service/ticket_profile.html', locals())

@login_required
def post_task_message(request, service_id):
    '''
    Take a message about a Service instance  Very similar to the view of the same name in the do app.  
    See if the task is complete and mark it so if so.
    If the message field is not blank, send it to the social view to handle the text of the message.
    
    SOGGY AS FUCK.
    '''
    service = Service.objects.get(id=service_id)
    task = service.task
    try:
        if request.POST['completed']:
            task.set_status(2, request.user)

    except MultiValueDictKeyError:
        pass #They didn't mark it completed, no need to think about it further.
    
    if request.POST['message']:
        post_top_level_message(request, 'do__task__%s' % (task.id))
        
    if request.POST['service_status']:
        status_object = ServiceStatusPrototype.objects.get(id=request.POST['service_status'])
        service.status = status_object
        service.save(creator=request.user)
    
    return HttpResponseRedirect(service.get_absolute_url())

