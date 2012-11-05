'''
The modeling of the Do app is documented in the WHAT docs under do -=> internals.
'''
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Count, Max
from django.db.models.signals import post_save
from taggit.managers import TaggableManager
from what_apps.commerce.models import TradeItem
from what_apps.mellon.models import get_privileges_for_user
from what_apps.meta.models import StatusLog
from what_apps.people.models import GenericParty
from what_apps.push.functions import push_with_template
from what_apps.social.models import TopLevelMessage
from what_apps.utility.models import GenericPartyManyToManyField, \
    GenericPartyForeignKey
import random








#Query to get tasks for a user:
#Task.objects.filter(access_requirements__prototype__privilege__bases__privilegebasedongroups__groups__in = j.groups.all())

#from people.constants import SLASHROOT_AS_GENERICPARTY


now = datetime.now()

GENERATIONS_PER_MOON = 4032 #Number of times per Moon cycle that our management command is run (approximate, based on cronjob)

class VerbManager(models.Manager):
    '''
    We need a method to get the verbs by whether a user has any available tasks in them.
    '''
    def filter_verbs_with_tasks_user_can_see(self, user, *args, **kwargs):
        '''
        Takes a user and returns a list of verbs that contain tasks which the user can see.
        '''
        user_privileges = get_privileges_for_user(user)        
        verbs = super(VerbManager, self).filter(prototypes__instances__access_requirements__privilege__in=user_privileges) #TODO: This appears to only check that they have one of the privilege; there may be more than one.
        
        return verbs
    
    def order_verbs_by_number_of_tasks_user_can_see(self, user, *args, **kwargs):
        
        user_privileges = get_privileges_for_user(user)
        verbs_with_at_least_one_task_for_user = super(VerbManager, self).filter(prototypes__instances__access_requirements__prototype__privilege__in=user_privileges).distinct()
        verbs_with_no_tasks_for_user = super(VerbManager, self).exclude(prototypes__instances__access_requirements__prototype__privilege__in=user_privileges)
        
        verb_list = []
        
        for verb in verbs_with_at_least_one_task_for_user:
            verb_list.append((verb, verb.count_tasks_for_user(user))) #Append a tuple with the verb and the number of tasks this user can see.
        
        sorted_verb_list_tuples = sorted(verb_list, key=lambda verb_info: verb_info[1], reverse=True)   # Sort by the second entry for each tuple in the list (which, after all, is the number of tasks that this user can see).
        
        for verb in verbs_with_no_tasks_for_user:
            sorted_verb_list_tuples.append((verb, 0)) #Safely append to the sorted list because these will each be zero.
        
        sorted_verb_list = []
        
        for verb in sorted_verb_list_tuples:
            sorted_verb_list.append(verb[0])
        
        return sorted_verb_list
    
    def order_verbs_by_number_of_tasks_that_can_be_seen_with_privilege(self, privilege, *args, **kwargs):
        verbs_with_at_least_one_task_for_privilege = super(VerbManager, self).filter(prototypes__instances__access_requirements__prototype__privilege=privilege).distinct()
        verbs_with_no_tasks_for_privilege = super(VerbManager, self).exclude(prototypes__instances__access_requirements__prototype__privilege=privilege).distinct()
        
        verb_list = []
        
        for verb in verbs_with_at_least_one_task_for_privilege:
            verb_list.append((verb, verb.count_tasks_for_privilege(privilege))) #Append a tuple with the verb and the number of tasks this user can see.
        
        sorted_verb_tuple_list = sorted(verb_list, key=lambda verb_info: verb_info[1], reverse=True)   # Sort by the second entry for each tuple in the list (which, after all, is the number of tasks that this user can see).
        
        sorted_verb_list = []
        
        for entry in sorted_verb_tuple_list: #Probably a performance hit, but we're never going to have tens of thousands of verbs, so this will probably not be noticable.
            sorted_verb_list.append(entry[0]) #Append only the verb; let the tuple die.
        
        for verb in verbs_with_no_tasks_for_privilege:
            sorted_verb_list.append(verb) #Safely append to the sorted list because these will each be zero.
        
        return sorted_verb_list
        

class Verb(models.Model):
    '''
    Action words that describe classes of activity.
    '''
    name = models.CharField(max_length=80)
    description = models.TextField()
    
    objects = VerbManager()
    
    def __unicode__(self):
        return self.name
    
    def get_open_tasks(self):
        '''
        Returns a list of all uncompleted tasks that come from TaskPrototypes in this Action
        
        TODO: Make this better.
        '''
        return Task.objects.filter(prototype__type=self, resolutions__isnull=True)
    
    def get_closed_tasks(self):
        return Task.objects.filter(prototype__type=self, resolutions__isnull=False) #TODO: Account for re-opened tasks
    
    def get_open_top_level_tasks(self):
        return Task.objects.filter(prototype__type=self).filter(resolutions=None).filter(parents=None)
    
    def get_tasks_for_privilege(self, privilege, level=5, show_completed=False): #level is hardcoded for now        
        tasks = Task.objects.filter(access_requirements__prototype__privilege=privilege, prototype__type=self, resolutions__isnull=True)
        return tasks
    
    def top_level_tasks_for_privilege(self, privilege, level=5):
        return self.get_tasks_for_privilege(privilege).filter(parents__isnull=True)
    
    def count_tasks_for_privilege(self, privilege, level=5, count_completed=False): #level is hardcoded for now #TODO: Make count_completed work                
        return self.get_tasks_for_privilege(privilege).count()
    
    def get_tasks_for_user(self, user, level=5, show_completed=False): #level is hardcoded for now
        '''
        Based on a user's privileges, figure out which Tasks they can see.
        '''
        user_privileges = get_privileges_for_user(user)
        tasks = Task.objects.filter(access_requirements__prototype__privilege__in=user_privileges, prototype__type=self, resolutions__isnull=True).distinct() #TODO: Account for re-opened tasks.
        
        return tasks
    
    def count_tasks_for_user(self, user, level=5): #level is hardcoded for now
        return self.get_tasks_for_user(user).count()

    
    def get_top_level_tasks(self):
        return self.tasks.filter(parents__is_null=True)
    
    def get_open_non_bottom_level_tasks(self):
        '''
        Get tasks that are not bottom level
        
        BROKEN?
        '''
        
        uncompleted_tasks = Task.objects.filter(prototype__type=self).filter(resolutions=None) #Get all the tasks for this verb.        
        
        return uncompleted_tasks
        
        orphan_tasks = uncompleted_tasks.filter(parents=None)            
        
        tasks_with_parents = uncompleted_tasks.exclude(parents=None) #However, among those tasks that DO have parents....
        non_bottom_level_tasks = tasks_with_parents.exclude(children=None) #We don't want the ones that have no children.
        
    def open_task_count(self):   
        return Task.objects.filter(prototype__type=self, resolutions__isnull=True).count()
    
    def users_who_have_completed_tasks(self):
        '''
        Returns a dict of users and the number of tasks they have completed in this verb.
        '''
        closed_tasks = self.get_closed_tasks()
        
        
        user_dict = {}
        
        for task in closed_tasks:
            user = task.resolutions.all()[0].creator #TODO: Account for multiple resolutions 
            if user.username != "jMyles" and user.username != "ac": #Instructors hardcoded out for now.  TODO: Make this function take a list of privileges to exclude.
                if user not in user_dict: 
                    user_dict[user] = 1
                else:
                    user_dict[user] += 1
        
        user_list = list(user_dict.items()) #This will be a list of tuples, with the user as the first item and the number of completed tasks as the second.
    
        sorted_user_list = sorted(user_list, key=lambda n: n[1], reverse=True)   # Sort by the second entry for each tuple in the list (which, after all, is the number of tasks that this has completed in this verb).
        
        return sorted_user_list
    
        
    

            

class TaskManager(models.Manager):
    '''
    Adding a method to get tasks currently owned by a user or group.
    '''
    def filter_active_by_owner(self, party, *args, **kwargs):
        '''
        Takes a User, Group, or GenericParty and returns a list of tasks that are currently owned by them.
        '''
        if not party.__class__ == GenericParty:
            party = GenericParty.objects.get(party=party)
               
        all_owned_tasks = super(TaskManager, self).filter(ownership__party=party, completed=False).select_related('ownership')
        
        task_list = []
        
        for task in all_owned_tasks: #TODO: Is this the best / fastest way of doing this?
            ownership = task.ownership.filter(party=party).latest('created')
            if not ownership.disown:
                task_list.append(task)
                    
        return task_list
    
    def can_be_seen_by_user(self, user, *args, **kwargs):
        '''
        Filters tasks that can be seen by a particular user.
        
        TODO: See if this can be optimized.
        '''
        user_privileges = get_privileges_for_user(user)
        queryset = super(TaskManager, self).filter(access_requirements__prototype__privilege__in=user_privileges)
        
        return queryset
        
        
TASK_STATUS_CHOICES = (
                       (0, 'Open'),
                       (1, 'Re-opened'),
                       (2, 'Completed'),
                       (3, 'Abandoned')
                       )

class Task(models.Model):
    '''
    A discrete, one-time action, regardless of scope, ie "Make SlashRoot successful," or "Finish Sanding the Spackle to the left of the llama feeding station"
    
    Some tasks are automated - we know which ones those are because they'll have been created by the user AutoTaskCreator
    '''
    
    status = models.IntegerField(choices=TASK_STATUS_CHOICES, default=0)
    prototype = models.ForeignKey('do.TaskPrototype', related_name="instances", editable=False)
    projected = models.DateTimeField(blank=True, null=True, help_text="Expected time of completion")        
    weight = models.IntegerField()
    
    
    creator = models.ForeignKey('auth.User', related_name="created_tasks")
    created = models.DateTimeField(auto_now_add=True)
    
    
    messages = generic.GenericRelation('social.TopLevelMessage')
    notices = generic.GenericRelation('social.DrawAttention')
    
    
    objects = TaskManager()
    tags = TaggableManager()
    
    def __unicode__(self, with_links=False):
        '''
        Interesting unicode method.  We want to refer to the task differently depending on whether it has a related object.
        '''       
        if self.related_objects.exists():
            #If we have related objects, we need to parse the string to figure out how to display them.
            #TODO: Make this work with more than 1 related object.
            #We're looking for the location in the string of the index of the related object.  Got it?
            beginning_of_index = self.prototype.name.find("[[")
            end_of_index = self.prototype.name.find("]]")
            
            #Now we need to look between then.
            index = self.prototype.name[beginning_of_index + 2:end_of_index] #Now we have perhaps "0" - we'll look for the related object indexed 0.  BTW, the +2 is to offset the "[[".
            
            related_object_relation = self.related_objects.all()[int(index)]
            actual_related_object = related_object_relation.object
            
            if related_object_relation.object.__class__ == User: #We can't change the unicode method for User, but we want full name displayed here.
                related_object_name = related_object_relation.object.get_full_name()
            else: #Otherwise, we'll take the unicode method of the related object.
                related_object_name = unicode(related_object_relation.object)
            
            
            prefix = self.prototype.name[:beginning_of_index]
            suffix = self.prototype.name[int(end_of_index + 2):] #The plus 2 business is for the same reason as above.
            
#            if with_links:
#                new_name = '%s <a class="relatedObject" href="%s">%s</a> %s' % (
#                                         str(prefix),
#                                         str(actual_related_object.get_absolute_url()),
#                                         str(related_object_name),
#                                         str(suffix),
#                                         )
#            else:
            new_name = "%s %s %s" % (
                                     str(prefix),
                                     str(related_object_name),
                                     str(suffix)
                                     )
                
            return new_name
            
        if self.prototype.name.find("[[Parent") > 0:#If this is true, this task is a reference to its parent.
            beginning_of_index = self.prototype.name.find("::")
            end_of_index = self.prototype.name.find("]]")
            index = self.prototype.name[beginning_of_index + 2:end_of_index] #Now we have perhaps "0" - we'll look for the related object indexed 0.  BTW, the +2 is to offset the "[[".
            
            #If it has this name, we are going to assume that this task has only one parent.
            parent = Task.objects.get(children__child=self) #TODO: Raise an appropriate error if this isn't the case.
            
            #Now we'll look at the parent to see what the relation index refers to.
            try:
                related_object_relation = parent.related_objects.all()[int(index)]
            except IndexError:
                #It's called something like [[Parent::0]] but it doesn't have a related object
                #raise ReallyFuckedUpError
                return self.prototype.name             
            actual_related_object = related_object_relation.object
            
            beginning_of_word_parent = self.prototype.name.find("[[Parent")
            
            prefix = self.prototype.name[:beginning_of_word_parent]
            suffix = self.prototype.name[int(end_of_index + 2):] #The plus 2 business is for the same reason as above.
            
            new_name = "%s %s %s" % (
                         str(prefix),
                         str(actual_related_object),
                         str(suffix)
                         )
                
            return new_name
            
        #Otherwsie let's just give them the name.            
        return self.prototype.name
    
#    def is_closed(self):
#        '''
#        Returns True if task is complete or abandoned, otherwise False.
#        '''
#        #return self.llama
#        return True 
        
    def subscribers(self):
        '''
        Returns a set of Users who have done one of the following:
        
        1) Created this Task
        2) Owned this Task
        3) Commented on this task
        4) Had their attention drawn to this task
        
        ...but not if they have "unsubscribed" themselves.  TODO: Make unsubscribing work.
        
        In each case, we'll confirm that the user in question does in fact have an email address. 
        '''
        subscribers = set()  
        
        if self.creator.email:
            subscribers.add(self.creator.email) #The creator gets a message
        
        for ownership in self.ownership.all(): #Each owner gets a message
            if ownership.owner.email:
                subscribers.add(ownership.owner.email) 
            
        for message in self.messages.all(): #Everybody who has previously posted a message gets a message
            if message.creator.email:
                subscribers.add(message.creator.email)
        
        return subscribers
    
    def name_with_links(self):
        return self.__unicode__(with_links=True)
        
    def get_absolute_url(self):
        return '/do/task_profile/%i/' % self.id
    
    def days(self):
        now = datetime.now()
        delta = now - self.created
        return delta.days
        
    def owners(self):
        '''
        Returns a user object for each owner.
        
        TODO: Figure out how disown works into this.
        '''
        owners = []
        
        for ownership in self.ownership.all():
            owners.append(ownership.owner)
        
        return owners
    
    def is_owned_by_user(self, user):
        '''
        Takes a User, figures out if that User currently owns this Task.
        '''
        if user.is_anonymous():
            return False
        try:
            ownership = self.ownership.get(owner=user) #Get the ownership object for this user.
            return ownership
        except TaskOwnership.DoesNotExist:
            return False

    def is_top_level(self):
        return bool(not self.parents.count()) #True if self has no parent (ergo, this is a top level model)

    def open_children(self):
        open_tasks = list(self.children.filter(child__status__lt = 2))
        return open_tasks
    
    def closed_children(self):
        return self.children.filter(child__status__gt = 1)

    def get_all_children_as_dict(self):
        children = {}
        for task_hierarchy in self.children.all().order_by('priority'): #self.children aren't tasks but TaskHierarchy objects
            children[task_hierarchy.priority] = task_hierarchy.child #Each TaskHierarchy object has a child.
        return children
    
    def get_all_parents_as_list(self):
        parents = []
        
        for task_hierarchy in self.parents.all():
            parents.append(task_hierarchy.parent)
        return parents
    
    def latest_statuslog_entry(self):
        '''
        Deprecated?
        '''
        try:
            resolution = self.resolutions.latest('created')
            return resolution.get_type_display()
        except TaskResolution.DoesNotExist:
            return "Open"
    
    def is_open(self):
        if self.status < 2:
            return True
        else:
            return False
        
    def gravitas(self):
        if not self.children.exists():
            return 0
        elif not self.children.exclude(child__children__isnull=True):
            #This task has children, but no grandchildren.  We only have one gravitas to add.
            return 1
        else:
            #This task has at least grandchildren.  We need to figure out which of its grandchildren has the highest gravitas.
            highest_child_gravitas = 0 #Assume for a moment that we won't find a child with any gravitas (even though we know that's not true)
            for progeny in self.children.exclude(child__children__isnull=True): 
                if progeny.child.gravitas() > highest_child_gravitas:
                    highest_child_gravitas = progeny.child.gravitas()
            return int(highest_child_gravitas) + 1
    
    def check_for_new_children_in_prototype(self):
        '''
        TODO: Make this actually look at the prototypes instead of just counting.
        '''
        return int(self.prototype.children.count() - self.children.count())
        
    def update_to_prototype(self, user=False):              
        '''
        Updates this task's downward progeny to reflect changes to its prototype's downward progeny.
        
        TODO: Also change protoype to evolved version.
        '''
        for progeny in self.prototype.children.all():
            try:
                child_task = self.children.filter(child__protoype=progeny.child) #TODO: Include entire ancestry, not just progeny.child
            except TaskProgeny.DoesNotExist:
                child_task = progeny.child.instantiate()
                if user:
                    child_task.creator = user
                    child_task.save()
                #As obscure as these next six lines may seem, they're actually WET - see task_form_handler in the views
                current_max_priority_ag = self.children.all().aggregate(Max('priority'))
                current_max_priority = current_max_priority_ag['priority__max']
                try:
                    priority = int(current_max_priority) + 5 #Try setting the priority to the highest priority plus 5
                except TypeError:
                    priority = 5 #Fuck it, there is no priority at all; we'll start it at 5  
                TaskProgeny.objects.create(child=child_task, parent=self)
                
    ###Undue coupling coming.  This shit probably belongs in the service app.
    def related_user(self):
        '''
        If there's a related user, return it.  
        TODO: Make this actually check for User *and* wrap around cases where there aren't any related items.
        '''
        user = self.related_objects.all()[0].object
        return user
    
    
    
    def set_status(self, status, creator):
        '''
        Takes a status number and a user.
        
        If the status is different than the current status,
        create a status object and set the current status,
        returning True.
        
        Otherwise, return False.
        '''
        if self.status == status:
            return False
        else:
            self.resolutions.create(creator=creator, type=status)
            self.status=status
            self.save()        
            return True
        
    
class TaskResolution(models.Model):
    '''
    Moisture warning.
    
    This model logs the changes in status of a task.
    
    It is properly more aptly named TaskStatusLog
    '''
    creator = models.ForeignKey('auth.User', related_name="resolved_tasks")
    created = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('do.Task', related_name="resolutions")
    type = models.IntegerField(choices=TASK_STATUS_CHOICES)

    def __unicode__(self):
        return "%s %s: %s" % (self.creator, self.get_type_display(), self.task)
            

class TaskProgeny(models.Model):
    '''
    An implicit through-model from Task-=>Task.
    
    Identifies a child, its parent, and the order of that child among its siblings.
    '''
    child = models.ForeignKey(Task, related_name="parents")
    parent = models.ForeignKey(Task, related_name="children")
    priority = models.IntegerField(help_text="An integer that describes the order of this child among its siblings with this parent.")

    class Meta:
        unique_together = (('child', 'parent'), ('parent', 'priority'))
        
    def __unicode__(self):
        return "%s <=- %s" % (self.parent, self.child)

def notifyNewChildTask(sender, instance, created, **kwargs):
    if created:
        parent = instance.parent
        child = instance.child
        push_with_template('do/task_row_detailed.html', {'task': child}, "/do/new_child/" + str(parent.id))        
        

#post_save.connect(notifyNewChildTask, sender=TaskProgeny) #every time a task hierarchy gets saved notify new_child task, see post save signal in signal in django documentation

    
class TaskPrototype(models.Model):
    '''
    The boilerplate for a Task.  Every Task is based on a TaskPrototype.
    
    Most tasks in the system will originate from this model's instantiate method.
    '''
    name = models.CharField(max_length=200, unique=True)
    type = models.ForeignKey('do.Verb', related_name="prototypes", help_text="The action word describing this type of task.")
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User', related_name="created_task_prototypes")
    weight = models.IntegerField(default=0)
        
    def __unicode__(self):
        return self.name
    
    def open_tasks(self):
        '''
        Grab tasks whose latest resolution object is not "Completed" or "Abandoned"
        '''
        open_tasks = list(self.instances.filter(status__lt = 2))
        
#        has_been_resolved = self.instances.exclude(resolutions__isnull=True).annotate(latest_resolution=Max('resolutions__created'))
#
#        for task in has_been_resolved:
#            if task.resolutions.filter(created=task.latest_resolution) == "O":
#                open_tasks.append(task)
                
        return open_tasks
    
    def count_relations_in_name(self):
        '''
        Relations denoted in the name look like [[something::number]] or [[number]].  
        We'll count the number of times that "[[" appears and return that number.
        '''
        return self.name.count('[[') - self.name.count('[[Parent') #All the '[[' that arent' '[[Parent' count in the tally of related objects
    
    def completed_tasks(self):
        '''
        TODO: Better.
        '''
        return self.instances.exclude(resolutions=None)

    def get_absolute_url(self):
        return '/do/task_prototype_profile/%i/' % self.id
    
    def is_top_level(self):
        return bool(not self.parents.count()) #True if self has no parent (ergo, this is a top level model)
    
    def is_bottom_level(self):
        return bool(not self.children.count())
    
    def instantiate(self, creator=187, parent_task=None, projected=None):
        '''
        Generates a task family based on this prototype.
        '''
        try:
            creator_id = creator.id
        except AttributeError:
            creator_id = creator
        
            
        from do.models import TaskProgeny
        if not parent_task:
            parent_task = self.instances.create(creator_id=creator_id, weight=self.weight, projected=projected)

        for prototype_progeny in self.children.all():
            child = prototype_progeny.child
            child_task = child.instances.create(creator_id=creator_id, weight=child.weight)
            
            new_progeny = TaskProgeny.objects.create(parent=parent_task, child=child_task, priority=prototype_progeny.priority)            
            child_task_tree = child.instantiate(parent_task=child_task)

        return parent_task

    def owner_count(self):   
        tasks = self.instances.all()
        
        count_owners = tasks.aggregate(count=Count('ownership__owner'))['count']
     
        return count_owners
    
    def update_instances(self):
        '''
        Updates open instances of this TaskPrototype to include new progeny
        '''
        pass
        
    

        
class TaskPrototypeEvolution(models.Model):
    '''
    Through model from TaskPrototype to itself, tracking the evolution of TaskPrototypes over time
    '''
    old_prototype = models.ForeignKey('do.TaskPrototype', related_name="evolved_into")
    new_prototype = models.ForeignKey('do.TaskPrototype', related_name="evolved_from")
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User', related_name="evolved_task_prototypes")
    
    
class TaskPrototypeProgeny(models.Model):
    '''
    Through model from TaskPrototype to itself.
    
    Identifies a child, its parent, and the order of that child among its siblings, just like TaskProgeny.
    '''
    child = models.ForeignKey('do.TaskPrototype', related_name="parents")
    parent = models.ForeignKey('do.TaskPrototype', related_name="children")
    priority = models.IntegerField(help_text="An integer that describes the order of this child among its siblings with this parent.")
    created = models.DateTimeField(auto_now_add=True)
    revision = models.IntegerField(help_text="0 is the state of the family when the parent is created.  Each additional child causes an increment.", default=0)

    def __unicode__(self):
        return "%s <=- %s" % (self.parent, self.child)

    class Meta:
        unique_together = (('child', 'parent'), ('parent', 'priority'))

class TaskGenerator(models.Model):
    prototype = models.ForeignKey('do.TaskPrototype', related_name="generators")

class RandomRecurringTaskGenerator(TaskGenerator):
    '''
    Takes a TaskPrototype and creates a task based on it every so often.
    '''
    active = models.BooleanField()
    frequency = models.IntegerField(help_text="How many of these will be created each Moon cycle?  X / Interval: 4 / Week, 28 / Day,  112 / 4x Per Day, 672 / Hour, 4032 / Every 10 Minutes (maximum)")
    backlog = models.BooleanField(help_text="Should this task be created even if another just like it already exists, uncompleted?")
    timeframe = models.TimeField(help_text="How long ahead of this task will the deadline be set?", blank=True, null=True)
    
    def roll_the_dice(self, privilege):
        if self.active:
            if not self.backlog: #We aren't supposed to backlog this task; let's make sure there isn't already one.
                if len(self.prototype.open_tasks()) > 0:
                    return "backlogged."
            r = random.randint(1, GENERATIONS_PER_MOON)
            f = self.frequency
            chance = r + f
            if chance > GENERATIONS_PER_MOON:
                prototype = self.prototype
                new_task = prototype.instantiate()   #projected = now + self.timeframe) #TODO: Make projected work
                task_access_prototype = TaskAccessPrototype.objects.get_or_create(privilege=privilege, type=5)[0] #TODO: Un-hardcode this 5
                task_access = TaskAccess.objects.create(prototype=task_access_prototype, task=new_task)
                return new_task
            else:
                return chance
        return False #Catches other cases
    
    def __unicode__(self):
        return "%s (%s)" % (self.prototype.name, self.frequency)

class ScheduledRecurringTaskGenerator(TaskGenerator):
    '''
    Generates Tasks at a regularly scheduled time
    '''
    pass

class EventDrivenTaskGenerator(TaskGenerator):
    '''
    Criteria for generating a task based on some other object
    '''
    pass

class TaskOwnership(models.Model):
    '''
    Signifies ownership or of a task by a particular party.
    '''
    owner = models.ForeignKey('auth.User', related_name="owned_tasks")
    task = models.ForeignKey('do.Task', related_name="ownership")
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('owner', 'task')

class TaskAccessPrototype(models.Model):        
    '''
    Matches a privilege with the access to view, own, complete, and review a task. 
    '''
    TASK_ACCESS_CHOICES = (#Each level implies previous levels.
                       (0, 'See Task Once Owned'),
                       (1, 'See Task Always'),
                       (2, 'Own task once already Owned'),
                       (3, 'Become first Owner'),
                       (4, 'Mark task complete'),
                       (5, 'Review Task Resolution'),
                           )
    
    privilege = models.ForeignKey('mellon.Privilege', related_name="tasks")
    type = models.SmallIntegerField(choices=TASK_ACCESS_CHOICES)
    
    class Meta:
        unique_together = ('privilege', 'type')
        
    def __unicode__(self):
        return "%s can %s" % (
                              str(self.privilege),
                              str(self.get_type_display()),
                               ) 
    
class TaskAccess(models.Model):
    '''
    Applies a TaskAccessPrototype to a particular Task.
    '''
    prototype = models.ForeignKey('do.TaskAccessPrototype', related_name="applications")
    task = models.ForeignKey('do.Task', related_name="access_requirements")
    
    class Meta:
        unique_together = ('prototype', 'task')
        verbose_name_plural = "Task Access"
        
    def __unicode__(self):
        return "%s (level %s) for: %s" % (str(self.prototype), str(self.prototype.type), str(self.task))

class TaskRelatedObject(models.Model):
    '''
    Relates an object to a Task
    '''
    task = models.ForeignKey('do.Task', related_name="related_objects")
    
    #The object to which attention is being drawn
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ('object_id', 'content_type', 'task')



'''
Hooks and push activity
'''

def notifyNewTask(sender, instance, created, **kwargs):
    '''
    Push new task activity, but only if we aren't waiting for related objects.
    
    For example, if a Task Prototype is "Walked the llama named [[0]]," it doesn't make sense to push that name because nobody will know what we're talking about.
    '''
    if created and not bool(instance.prototype.count_relations_in_name()): #The number of relations in the name will be zero if there aren't any.  Other wise, we don't really want to rock out on this.         
        push_with_template('do/do_feed_items/task_feed.html', {'task': instance}, "/feeds/do/llamas/walruses/tasks") #TODO: Make this name sensible.        
        
post_save.connect(notifyNewTask, sender=Task) 



def notifyNewRelation(sender, instance, created, **kwargs):
    if created:
        
        #First let's see if, now that this related object is saved, the number of related objects matches the number that we're expecting from the name.
        task = instance.task
        
        if task.prototype.count_relations_in_name() == task.related_objects.count():
            push_with_template('do/do_feed_items/task_feed.html', {'task': task}, "/feeds/do/llamas/walruses/tasks") #TODO: Make this name sensible.

post_save.connect(notifyNewRelation, sender=TaskRelatedObject)



def notifyNewDoActivity(sender, instance, created, **kwargs):
    if created: #This is only for newly created objects
        try: #Let's assume for a second that this is a TopLevelMessage
            
            if instance.__class__.__name__ == "TopLevelMessage": #Ugly.  TODO: Let's pass a kwarg instead.                
                if str(instance.content_type) == "task":
                    this_is_a_message = True
                else:
                    return None #If it's not related to a task, we don't even want to be here.  Again, ugly.
            else:
                this_is_a_message = False

        except AttributeError: #OK, so it's not a TopLevelMessage.
            this_is_a_message = False            
        
        if this_is_a_message:
            
                #Now, let's blast out these emails.
                #We want to send emails in three cases: The creator of the task, The owner(s) of the task, and anybody who has sent a message in this task.
                #However, we do not want anybody to get two emails.  Thus, we'll populate a set of unique values.
                
                task = instance.content_object
                recipients = task.subscribers()
                
                #The creator of this message doesn't need to get an email.
                if instance.creator.email in recipients:
                    recipients.remove(instance.creator.email)
                    
                if recipients: #Are there any recipients left?
                                    
                    subject = "Task %s: %s" % (str(task.id), str(task)) 
                    body = '-- \n %s says: \n\n %s\n\n -- \n\n To see all messages: \n <a href="slashrootcafe.com/%s">%s</a>' % (str(instance.creator), instance.message, task.get_absolute_url(), str(task))
                    sender = '%s <do.task.%s@objects.slashrootcafe.com>' % (str(instance.creator), str(task.id))
                    
                    msg = EmailMessage(subject, body, sender, recipients)
                    msg.content_subtype = "html"
                    msg.send()
                
                push_with_template('do/do_feed_items/toplevelmessage', {'item': instance}, "/feeds/do/llamas/walruses/activity") #TODO: Make this better.
                
                return 1
        else:
            type = str(instance._meta).split('.')[1]
            push_with_template('do/do_feed_items/' + type, {'item': instance}, "/feeds/do/llamas/walruses/activity") #TODO: Make this better.
            return 1            

        
    
post_save.connect(notifyNewDoActivity, sender=TopLevelMessage)
post_save.connect(notifyNewDoActivity, sender=TaskResolution)
post_save.connect(notifyNewDoActivity, sender=TaskOwnership)           
                  
class Protocol(models.Model):
    '''
    SlashRoot's policies, procedures, and protocols listed here.
    '''    
    name = models.CharField(max_length=50)
    text = models.TextField()         
    
    def __unicode__(self): 
        return self.name
    
    def get_absolute_url(self):
        return "/do/protocol/%s" % (self.id)
    
    
    
