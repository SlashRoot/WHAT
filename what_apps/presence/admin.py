from models import PresencePurpose, AnchorTime
from django.contrib import admin
from .models import SessionInfo


admin.site.register(PresencePurpose)
admin.site.register(AnchorTime)

class SessionInfoAdmin(admin.ModelAdmin): 
    model = SessionInfo
    list_display = ('user', 'created', 'destroyed')

admin.site.register(SessionInfo, SessionInfoAdmin)

from what_apps.utility.admin import autoregister

autoregister('presence')