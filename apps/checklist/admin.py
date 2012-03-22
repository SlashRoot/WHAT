from checklist.models import Checklist
from checklist.models import Item
from django.contrib import admin

class ItemInline(admin.StackedInline):
    model = Item
    extra = 3
    
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('Name',)
    fieldsets = [
        (None, {'fields': ['Name']}),
    ]
    inlines=[ItemInline]

admin.site.register(Checklist, ChecklistAdmin)