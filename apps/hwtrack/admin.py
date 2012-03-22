from hwtrack.models import Device
from django.contrib import admin 

class DeviceAdmin(admin.ModelAdmin): 
    model = Device
    
    list_display = ('name','quick','location')
    
admin.site.register(Device,DeviceAdmin)


from utility.admin import autoregister
autoregister('hwtrack')