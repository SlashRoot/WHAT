from datetime import date, datetime, timedelta

from django.db import models
from django.db.models import Q

from hwtrack.models import Device
from utility.models import GenericPartyForeignKey, FixedObject

from itertools import chain
from social.models import TopLevelMessage, DrawAttention
from comm.models import PhoneCall


class Expectation(models.Model):
    '''
    An expectation that we perceive that a client has.
    Let's always formulate low expectation and then exceed them by a healthy margin.
    '''
    description = models.TextField()
    plan = models.OneToOneField('do.Task') #How will we exceed this expectation?
    created = models.DateTimeField(auto_now_add=True)
    communication = models.ForeignKey('comm.communicationinvolvement', help_text="instance of communication during which this expectation was formed")

class ServiceManager(models.Manager):
    def create(self, **kwargs):
        if not kwargs.has_key('task_id') and not kwargs.has_key('task'):
            tp = FixedObject.objects.get(name="TaskPrototype__tech_service").object
            task = tp.instantiate()
            kwargs['task_id'] = task.id
        obj = super(ServiceManager, self).create(**kwargs)
        return obj
        
    def open_tickets(self):
        return self.filter(task__status__lt = 2)
    
    def filter_by_needing_attention(self):
        '''
        Returns a tuple:
        *set of service objects that, for a variety of criteria, need attention.
        *other open service objects
        '''
        needing_attention = set()
        not_needing_attention = set()
        for service in self.open_tickets():
            
            if service.status.always_in_bearer_court == True:
                needing_attention.add(service)
                continue
            
            if service.most_recent_call_is_unresolved == True:
                needing_attention.add(service)
                continue
            
            not_needing_attention.add(service)
            
        return needing_attention, not_needing_attention
            
                
            
        

class Service(models.Model):
    '''
    An instance of service that we're rendng for somebody.
    '''
    objects = ServiceManager()
    
    task = models.OneToOneField('do.Task')
    recipient = GenericPartyForeignKey()
    status = models.ForeignKey('service.ServiceStatusPrototype')
    pay_per_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    manual_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#    flat = models.BooleanField()
#    device = models.ForeignKey('hwtrack.Device')

    def __unicode__(self):
        return "#%s - %s" % (self.id, self.recipient)

    def save(self, *args, **kwargs):
        '''
        We need to create a StatusLog object every time the status is changed.
        '''
        orig = None
        if self.pk is not None:
            orig = Service.objects.get(pk=self.pk)
        try:
            user = kwargs.pop('creator')
            if orig.status != self.status:
                ServiceStatusLog.objects.create(service = self, creator=user, prototype=self.status)
        except KeyError:
            if orig:
                if orig.status != self.status:
                    raise TypeError("In order to change the status of a Service object, you must pass a user who is responsible for the change.\n To propose a change to this policy, see the Tech Satchem.")

        return super(Service, self).save(*args, **kwargs)
        
    def chronology(self):
        '''
        Returns a list of the events pertaining to this Service.
        '''
        events = []
        
        for call in self.all_phone_calls_ever():
            call.display_type = "Phone Call"
            events.append(call)
        
        for message in self.task.messages.all():
            message.display_type = "Message"
            events.append(message)
        
        for status in self.status_history.all():
            status.display_type = "Status"
            events.append(status)
                    
        sorted_list_of_events = sorted(events, key = lambda event: event.created)
        
        return sorted_list_of_events

    def get_absolute_url(self):
        return "/service/tickets/%s/" % self.id

    def all_phone_calls_ever(self, include_incoming=True, include_outgoing=True):
        '''
        Returns a QuerySet of all the phone calls ever made to or by the recipient of this Service.
        '''
        from comm.models import PhoneCall
        
        if not include_incoming:
            all_calls = PhoneCall.objects.filter(to_number__owner = self.recipient.contact_info() )
        
        if not include_outgoing:
            all_calls = PhoneCall.objects.filter(from_number__owner = self.recipient.contact_info() )
            
        if include_incoming and include_outgoing:
            all_calls = PhoneCall.objects.filter(Q(from_number__owner = self.recipient.contact_info()) | Q(to_number__owner = self.recipient.contact_info()))

        return all_calls    
    
    def phone_calls_today(self, include_incoming=True, include_outgoing=True):
        from comm.models import PhoneCall
        today = date.today()
        calls = self.all_phone_calls_ever(include_incoming, include_outgoing).filter(created__year = today.year, created__day = today.day, created__month = today.month)
        return calls
    
    def phone_calls_during_this_service(self, include_incoming=True, include_outgoing=True):
        three_days_before_job_started = self.task.created - timedelta(days=3) 
        calls_in_timeframe = self.all_phone_calls_ever(include_incoming, include_outgoing).filter(created__gt = three_days_before_job_started)
        return calls_in_timeframe
    
    def incoming_calls_during_this_service(self):
        return self.phone_calls_during_this_service(include_outgoing=False)
    
    def outgoing_calls_during_this_service(self):
        return self.phone_calls_during_this_service(include_incoming=False)
    
    def incoming_calls_today(self):
        return self.phone_calls_today(include_outgoing=False)
    
    def outgoing_calls_today(self):
        return self.phone_calls_today(include_incoming=False)
    
    def most_recent_call(self, include_incoming=True, include_outgoing=True):
        calls = self.all_phone_calls_ever(include_incoming, include_outgoing)
        try:
           return calls.latest('created')
        except PhoneCall.DoesNotExist: #If they have never called, then nevermind.
            return True
        
    def most_recent_call_was_answered(self, include_incoming=True, include_outgoing=True):
        most_recent_call = self.most_recent_call(include_incoming, include_outgoing)
        answered = most_recent_call.resolve_task().tags.filter(name='answered')
        return bool(answered)
    
    def most_recent_incoming_call_was_answered(self):
        return self.most_recent_call_was_answered(include_outgoing=False)
    
    def most_recent_call_is_unresolved(self, include_incoming=True, include_outgoing=True):
        most_recent_call = self.most_recent_call(include_incoming, include_outgoing)
        return bool(most_recent_call.resolve_task().status.name in ['Opened', 'Re-opened'] )
        
        
    def most_recent_action(self):
        candidates = []
        try:
            candidates.append(self.task.messages.latest('created'))
        except TopLevelMessage.DoesNotExist:
            pass
        
        try:
            candidates.append(self.task.notices.latest('created'))
        except DrawAttention.DoesNotExist:
            pass
        
        try:
            candidates.append(self.all_phone_calls_ever().latest('created'))
        except PhoneCall.DoesNotExist:
            pass
        
        try:
            candidates.append(self.status_history.latest('created'))
        except ServiceStatusLog.DoesNotExist:
            pass
        
        if len(candidates) == 0:
            return self
        
        sorted_list_of_candidates = sorted(candidates, key = lambda event: event.created, reverse=True)
        latest_event = sorted_list_of_candidates[0]
        return latest_event

    def same_owner_and_contract_party(self):
            '''
            Returns True if all devices are owned by the same person and that person is the same as the contract party.
            '''
            pass
        
    def service_log_display(self):
        return "Service Began"
    
    def total_time_in_status(self, status):
        '''
        Takes a ServiceStatusPrototype and returns a tuple of:
        1)How many times in that status
        2)timedelta of total duration
'''
        try:
            status_instances = self.status_history.filter(prototype=status)
        except ValueError: #Maybe they provided a status name instead of a ServiceStatusPrototype object.
            status_instances = self.status_history.filter(prototype__name=status)

        number = len(status_instances)
        duration = timedelta(0) #Start with an empty timedelta; we'll add to it for each instance.
        for instance in status_instances:
            duration += instance.duration()
        
        return number, duration
        
    #Dominick's Sandbox]
    
    def total_price(self, status='On the Bench'):
        time_spent_on_the_bench = self.total_time_in_status(status)[1]
        
        return (self.pay_per_hour * ((time_spent_on_the_bench.seconds//60) % 60)) + self.manual_override
    
    ## End of Dominick's Sandbox
    
    ## There seems to be a lack of understanding as to where this is going. --Dominick
#    class PriceTagPrototype(models.Model):
#        '''
#        A running tally for the suggested price for the customer.
#        '''
#        price_tag = int()
#        list_of_charges = dict()
#        def register(self):
#            charge = models.IntegerField()
#            reason = models.CharField(max_length=50)
#            self.PriceTagPrototype.price_tag += charge
#            self.PriceTagPrototype.list_of_charges.append({reason:charge})

    
    def status_summary(self):
        prototypes = ServiceStatusPrototype.objects.filter(instances__service=self).distinct()
        
        entries = []
        for prototype in prototypes:
            total_time = self.total_time_in_status(prototype)  # Remember, a tuple.
            
            entries.append( (prototype.name,) + total_time )  # three-element tuple starting with the name
        
        sorted_entries = sorted(entries, key = lambda entry: entry[2], reverse=True)
        
        return sorted_entries
    
class ServiceStatusPrototype(models.Model):
    name = models.CharField(max_length=30)
    always_in_bearer_court = models.BooleanField(help_text="True if this status indicates that action is required by the party in possession of the device.")
    retired = models.DateTimeField(blank=True, null=True)

class ServiceStatusLog(models.Model):
    prototype = models.ForeignKey('service.ServiceStatusPrototype', related_name="instances")
    service = models.ForeignKey('service.Service', related_name="status_history")
    creator = models.ForeignKey('auth.User', related_name="assigned_service_statuses")
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s %s on %s" % (self.prototype.name, self.service, self.created)
    
    def subsequent(self):
        try:
            return ServiceStatusLog.objects.filter(service=self.service, created__gt=self.created)[0]
        except IndexError:
            return None
    
    def duration(self):    
        if self.subsequent():
            end = self.subsequent().created
        else:
            end = datetime.now()
        duration = end - self.created
        return duration
        
    def service_log_display(self):
        return "%s set status" % (self.creator.username)

class Diagnosis(models.Model):
    '''
    We expect to get an incoming relationship from one or more symptoms.
    '''
    service = models.ForeignKey('service.Service')
    reasoning = models.TextField(blank=True, null=True)
    
class Symptom(models.Model): 
    '''
    A specific case of a symptom, ie "Crack on left side of screen," or "Freezes unless you do a rain dance during boot."
    '''
    type = models.ForeignKey('service.SymptomPrototype')
    details = models.TextField()
    diagnosis = models.ForeignKey('service.Diagnosis')

class SymptomPrototype(models.Model): 
    '''
    A broad set of symptom cases, ie "Broken Screen," or "Freezes during boot."
    '''
    name = models.CharField(max_length=40)
    description = models.TextField()
    

    
#class SymptomPrototypeEvolution(models .Model):
#    '''
#    Through model from TaskPrototype to itself, tracking the evolution of TaskPrototypes over time
#    '''
#    old_prototype = models.ForeignKey('service.ServicePrototype', related_name="evolved_into")
#    new_prototype = models.ForeignKey('service.ServicePrototype', related_name="evolved_from")
#    reason = models.TextField(blank=True, null=True, help_text="Why did this evolution occur?")    
#    
#class SymptomPrototypeProgeny(models.Model):
#    '''
#    Through model from TaskPrototype to itself.
#    
#    Identifies a child, its parent, and the order of that child among its siblings, just like TaskProgeny.
#    '''
#    child = models.ForeignKey('service.ServicePrototype', related_name="parents")
#    parent = models.ForeignKey('service.ServicePrototype', related_name="children")
#    priority = models.IntegerField(help_text="An integer that describes the order of this child among its siblings with this parent.")
#
#    def __unicode__(self):
#        return "%s <=- %s" % (self.parent, self.child)
#
#    class Meta:
#        unique_together = (('child', 'parent'), ('parent', 'priority'))

class ManualPriceOverride(models.Model): 
    amount = models.DecimalField()
    description = models.TextField()
    service = models.ForeignKey(Service)
    created = models.DateTimeField(auto_now_add=True)
    
    
    


