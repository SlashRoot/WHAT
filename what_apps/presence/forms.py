from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from django import forms
from django.forms import CharField
from utility.forms import AutoCompleteField 
from django.db import models
from presence.models import AfterHoursTidiness
from django.db.models.fields.related import ManyToManyField

 
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
    

    
