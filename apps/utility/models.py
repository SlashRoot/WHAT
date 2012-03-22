from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField

from utility.forms import GenericPartyField, ManyGenericPartyField

from people.models import GenericParty

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ['^utility\.models\.GenericPartyForeignKey',])

class FixedObject(models.Model):
    '''
    A standard set of generically related objects in the system.
    
    For example, we want to always be able to track down the "Customer Service" TaskPrototype, even if we can't (or don't want to) import TaskPrototype.
    
    Names need to follow the convention ModelName__instance_name_or_description
    
    For example, in the example above, we'll call it TaskAccessPrototype__customer_service
    '''

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


