from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField
from south.modelsinspector import add_introspection_rules
from what_apps.people.models import GenericParty
from what_apps.utility.forms import GenericPartyField, ManyGenericPartyField


add_introspection_rules([], ['^utility\.models\.GenericPartyForeignKey',])


class FixedObjectManager(models.Manager):
    
    #We'll override .create() because this model is often used in a get_or_create flow with the generic relation.
    
    def create(self, *args, **kwargs):
        
        try:
            object_which_already_exists = self.get(name=kwargs['name'])
            return object_which_already_exists
        except FixedObject.DoesNotExist:
            super(FixedObjectManager, self).create(*args, **kwargs)


class FixedObject(models.Model):
    '''
    A standard set of generically related objects in the system.
    
    For example, we want to always be able to track down the "Customer Service" TaskPrototype, even if we can't (or don't want to) import TaskPrototype.
    
    Names need to follow the convention ModelName__instance_name_or_description
    
    For example, in the example above, we'll call it TaskAccessPrototype__customer_service
    '''

    objects = FixedObjectManager()

    name = models.SlugField(max_length = 255, unique=True)

    value_id = models.PositiveIntegerField()
    value_type = models.ForeignKey(ContentType)
    object = generic.GenericForeignKey('value_type', 'value_id')

    class Meta:
        unique_together = 'value_id', 'value_type'
        
    def __unicode__(self):
        return self.name
        
    

class GenericPartyForeignKey(ForeignKey):
    def __init__(self, *args, **kwargs):
        try:
            to = kwargs.pop('to') #This is an odd line.  It is effectively now a .remove(), although the new 'to' was once passed as a positional arg.  This caused the landing test to fail.
            super(GenericPartyForeignKey, self).__init__(GenericParty, *args, **kwargs)
        except KeyError:
            super(GenericPartyForeignKey, self).__init__(GenericParty, *args, **kwargs)
        
    def formfield(self, **kwargs):
        defaults = {'form_class': GenericPartyField}
        defaults.update(kwargs)
        return super(GenericPartyForeignKey, self).formfield(**defaults)

class GenericPartyManyToManyField(ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(GenericPartyManyToManyField, self).__init__(GenericParty, *args, **kwargs)
        
    def formfield(self, **kwargs):
        defaults = {'form_class': ManyGenericPartyField}
        defaults.update(kwargs)
        return super(GenericPartyManyToManyField, self).formfield(**defaults)


