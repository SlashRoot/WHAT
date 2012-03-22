from django import forms
from utility.forms import GenericPartyField, JqueryDatePicker

class MostBasicServiceCheckInForm(forms.Form):
    customer = GenericPartyField()
    projected = JqueryDatePicker()
    
