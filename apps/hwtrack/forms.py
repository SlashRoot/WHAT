from django import forms



from django.contrib.auth.models import User

from utility.forms import AutoCompleteField 

from hwtrack.models import Device

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