from django import forms
from what_apps.utility.forms import GenericPartyField, JqueryDatePicker

class MostBasicServiceCheckInForm(forms.Form):
    customer = GenericPartyField()
    projected = JqueryDatePicker()
    
