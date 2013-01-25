from django import forms
from django.contrib.auth.models import User
from .models import Device
from what_apps.utility.forms import AutoCompleteField


class AddDeviceForm(forms.ModelForm):
    class Meta:
        model=Device
        
 
class ServiceCheckinForm(forms.Form):
    client_name = AutoCompleteField(label='Search for Device or Client', 
                                    models=(
                                          User,
                                          [Device,'quick']
                                          )
                                    
                                    )