from what_apps.mooncalendar.models import Event
from what_apps.mooncalendar.models import Moon
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
    list_display = 'name',
    fieldsets = [
        (None, {'fields': ['name']}),
        ('description', {'fields':['description']}),
        ('Date information', {'fields':['event_date']}),
    ]
        
class MoonAdmin(admin.ModelAdmin):
    list_display = ('name', 'new', 'full', 'length_as_string' )
        
    def length_as_string(self, obj):
        return str(obj.length())
    
    fieldsets = [
        ('name', {'fields':['name']}),
        ('new', {'fields':['new']}),
        ('waxing', {'fields':['waxing']}),
        ('full', {'fields':['full']}),
        ('waning', {'fields':['waning']}), 
        ]
    
admin.site.register(Event, EventAdmin)
admin.site.register(Moon, MoonAdmin)