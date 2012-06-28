from django import forms
from utility.forms import GenericPartyField, JqueryDatePicker
from service.models import Service, ManualPriceOverride

class MostBasicServiceCheckInForm(forms.Form):
    customer = GenericPartyField()
    projected = JqueryDatePicker()
    
class RateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('pay_per_hour',)
        

class ManualOverrideForm(forms.ModelForm):
    class Meta:
        model = ManualPriceOverride
         