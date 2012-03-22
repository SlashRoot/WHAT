from models import PresencePurpose, AnchorTime
from django.contrib import admin
from presence.models import SessionInfo


admin.site.register(PresencePurpose)
admin.site.register(AnchorTime)

class SessionInfoAdmin(admin.ModelAdmin): 
    model = SessionInfo
    list_display = ('user', 'created', 'destroyed')

admin.site.register(SessionInfo, SessionInfoAdmin)

from utility.admin import autoregister

autoregister('presence')