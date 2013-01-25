from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ManyToManyField
from django.forms import CharField
from django.forms.formsets import formset_factory
from what_apps.presence.models import AfterHoursTidiness
from what_apps.utility.forms import AutoCompleteField

 
'''
this form is to track the activities done by members after midnight in the shop
'''

class AfterHoursActivityForm(forms.Form):
    member = CharField(max_length=40)
    created= models.DateTimeField(auto_now_add=True)
    reason = forms.CharField(max_length=500)
    completed = forms.BooleanField,
    did_you_clean_up_after = forms.BooleanField(required=True),
    tidied_up = ManyToManyField(AfterHoursTidiness)
    are_there_dishes = forms.BooleanField(required=False),
    

    
