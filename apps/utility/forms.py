
from django import forms
from django.db import models

from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape

from django.utils.safestring import mark_safe

from django.forms.formsets import BaseFormSet


from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User, Group
from people.models import GenericParty


from utility.functions import daily_crypt  


class JqueryDatePicker(forms.DateField):
    def __init__(self, *args, **kwargs):
        super(JqueryDatePicker, self).__init__(*args, **kwargs)
        self.widget.format = '%m/%d/%Y'
        self.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
           

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

class AutoCompleteWidget(forms.TextInput):
    '''
    This widget is a little whacky and wild.
    What actually happens here is that the widget itself is a hidden field that gets populated with encrypted data by ajax.
    Additionally, there is a visible 'lookup' field into which the user types the autocomplete terms of their dreams.
    '''
    def __init__(self, new_buttons = False, models=None, with_description=False, name_visible_field=False, *args, **kwargs):
        super(AutoCompleteWidget, self).__init__(*args, **kwargs)
        
        self.name_visible_field = name_visible_field #We want the visible field to be named (ie, make its way into POST) iff we have set the field in the form as such. 
        
        #Let's populate the list of models.
        list_of_models = ""
        for model_info in models:
            try:
                counter = 0
                for counter, property in enumerate(model_info): #model info might be a list (if we have more than one model to autcomplete against) or just a ModelBase.  It's EAFP, so we'll presume we've been handed a tuple and deal with the other case in the block below.
                    #If model_info is in fact a list, we're going to loop through it.
                    if counter == 0: #The first time through, we know we have the model.
                        model = property
                        meta = str(model._meta) #Get the model meta, ie people.member
                        list_of_models += (meta) #Separate the model _meta by comma
                    else: #For subsequent iterations, we have a property name of the model.  We want to add that to the string.
                        if counter == 1: #If this is the second iteration, we are beginning a list of the properties against which we are going to autcomplete.
                            list_of_models += "__" + property #Add the first property
                        else:#This is not the first property; it's at least the second.  We'll separate these by ampersands.
                            list_of_models += "&" + property #Add the first property
            except TypeError:
                model = model_info
                meta = str(model._meta) #Get the model meta, ie people.member
                list_of_models += (meta) #Separate the model _meta by comma
            list_of_models += ","
            
        list_of_models = list_of_models[:-1] #Kill that last trailing comma
        
        self.encrypted_models = list_of_models
            
        
        if new_buttons:
            #They have asked for the little buttons to add new instances.
            if not models:
                #...but they didn't even have the decency to pass the models to us.
                raise RuntimeError('The llamas did not march.  You must either specify models for this widget or set new_buttons to False.')
            
            #OK, they gave us the models.  Let's give them the plus signs.
            self.add_html = ''
 
            for model in models:
                #Go through the models and add little plus signs, plus the model name.                
                try: #Maybe the object in question is in fact a model...
                    app_name = str(model._meta).split('.')[0]
                    model_name = str(model._meta).split('.')[1]
                except AttributeError: #Or maybe it's a list...
                    #In which cast we want model[0]
                    app_name = str(model[0]._meta).split('.')[0]
                    model_name = str(model[0]._meta).split('.')[1]
                
                #INTERUPPTOSAURUS!
                #If it's the user model, I want to force them to the contact form (instead of the auth.user admin page, which doesn't really do much for us, now does it?).
                if app_name == 'auth' and model_name == 'user':
                    add_url = '/contact/new_contact'
                    model_name = 'contact'
                                        
                else:                
                    add_url = '/admin/' + app_name + '/' + model_name + '/add'
                
                self.add_html += '<a target="_blank" href="'+ add_url + '" class="addButton"><span class="underText">' + model_name + '</span></a>'
                 
        else: #They didn't ask for the buttons.
            self.add_html = False
        
        
        
    def render(self, name, value=None, attrs=None):
        '''
        Justin here.  I'm actually not sure what the fuck is going on here.  Lost in my own code.
        '''
        final_attrs = self.build_attrs(attrs, name=name)
        lookup_attrs = self.build_attrs(attrs)
        
        if value:
            final_attrs['value'] = escape(smart_unicode(value))
            lookup_attrs['value'] = final_attrs['value'].split('___')[1] 

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name    
            
        lookup_attrs['id'] = final_attrs['id'] + '_lookup'
        lookup_attrs['class'] = 'autocompleteField autocompleteFieldIncomplete'
        
        if self.name_visible_field:
            lookup_attrs['name'] = 'lookup_%s' % name
        
        lookup_attrs['elephant_data'] = str(self.encrypted_models)
        
        final_attrs['type'] = 'hidden'
        
        input_html = mark_safe(u'<input%s />' % flatatt(final_attrs)) 
        
        widget_html = input_html #So far, just input_html

        lookup_html = mark_safe(u'<input%s />' % flatatt(lookup_attrs))
        
        widget_html += lookup_html #Now add the hidden_html
        
        if self.add_html:
            widget_html += self.add_html #Now add the plus signs
        
        return widget_html
    
class AutoCompleteField(forms.Field):
    '''
    Takes a tuple for models, autocompletes against their haystack entires.
    '''
    
    def __init__(self, models=None, new_buttons=False, with_description=True, name_visible_field=False, *args, **kwargs):
        super(AutoCompleteField, self).__init__(*args, **kwargs)

        self.widget = AutoCompleteWidget(new_buttons=new_buttons, models=models, name_visible_field=name_visible_field, with_description=with_description)
        

    def to_python(self, value):
        '''
        At the moment, this is not particularly useful.
        Better will be to actually decode the value from the hidden field and pass it if the field is shown to be valid.
        '''
        if value in validators.EMPTY_VALUES:
            return u''
        
        encrypted_result = value.split('___')[0]
        
        #result = daily_crypt(encrypted_result, decrypt=True)
        result = encrypted_result
        
        #This is now copied in utilities.function.get_object_from_string - please deprecate
        result_meta = result.split('_')[0] #Now just app and model.
        result_id = result.split('_')[1] #....and the ID of the object.
        
        result_app = result_meta.split('.')[0] #Everything before the . is the app name
        result_model = result_meta.split('.')[1] #Everything after is the model name
        
        
        #Get model of object in question
        model = ContentType.objects.get(app_label = result_app, model = result_model).model_class()
            
        #POSITIVE IDENTIFICATION CONFIRMED.  PROCEED WITH EXPERIMENT.
        result_object = model.objects.get(id=result_id)
        
        return result_object
    
class GenericPartyField(AutoCompleteField):
    
    def __init__(self, new_buttons=True, *args, **kwargs):
        super(GenericPartyField, self).__init__(models=([User,'first_name', 'last_name', 'username', 'email'], Group), new_buttons=new_buttons)
        
    def to_python(self, value):        
        try:
            object = super(GenericPartyField, self).to_python(value)
            generic_party = GenericParty.objects.get(party=object)
        except AttributeError: #Catch Justin's Attribute Error on Generic Party, ensure that the form can't validate
            raise ValidationError('GenericPartyField must be a User or a Group')    
        
        return generic_party
    
    def validate(self, value):
        '''
        Formerly "holy cow"
        '''
        pass
    
class SimplePartyLookup(forms.Form):
    party_lookup = GenericPartyField(new_buttons=False)
    
    
class ManyGenericPartyField(AutoCompleteField):
    def __init__(self, *args, **kwargs):
        super(ManyGenericPartyField, self).__init__(models=(User, Group), new_buttons=True)
        
    def to_python(self, value):
        object = super(ManyGenericPartyField, self).to_python(value)
        if object:
            generic_party = GenericParty.objects.get(party=object)
        else: 
            raise ValidationError("Gotta pass me somethin'")
        return [generic_party,]

class MustBeUniqueField(forms.Field):
    '''
    Takes a string in the form of appname.model__field and ensures that the value is unique for that field.
    '''
    
    def __init__(self, field=None, *args, **kwargs):
        super(MustBeUniqueField, self).__init__(*args, **kwargs)
        encrypted_field = daily_crypt(field) #Encrypt the list with today's daily salt
        self.widget.attrs['class'] = 'mustBeUniqueField'
        self.widget.attrs['elephant_data'] = str(encrypted_field)

def get_bool_from_html(piece):
    if piece in ['False', 'false', '0', 0]:
        return False
    else:
        return True  