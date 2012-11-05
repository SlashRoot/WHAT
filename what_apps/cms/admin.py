from what_apps.utility.admin import autoregister
from models import ContentBlock
from models import Page
from django.contrib import admin

class ContentBlockAdmin(admin.ModelAdmin): 
    model = ContentBlock
    
    list_display = ('headline', 'subhead')
    
admin.site.register(ContentBlock, ContentBlockAdmin)
    
class PageAdmin(admin.ModelAdmin):
    model = Page
    
    list_display = ('title',)

admin.site.register(Page, PageAdmin)


autoregister('cms')