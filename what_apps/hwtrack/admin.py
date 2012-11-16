from what_apps.hwtrack.models import Device
from django.contrib import admin 

class DeviceAdmin(admin.ModelAdmin): 
    model = Device
    
    list_display = ('name','quick','location')
    
admin.site.register(Device,DeviceAdmin)


from what_apps.utility.admin import autoregister
autoregister('hwtrack')