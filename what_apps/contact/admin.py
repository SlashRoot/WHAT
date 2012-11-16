from models import MailHandler, MailMessage, ContactInfo
from django.contrib import admin
from what_apps.utility.admin import autoregister
from what_apps.contact.models import DialListParticipation, PhoneNumber

class MailHandlerAdmin(admin.ModelAdmin): 
    model = MailHandler
    
    list_display = ('address',)
    fieldsets = [
        (None, {'fields': ['address', 'actions', 'users', 'groups']} ),
    ]
    
admin.site.register(MailHandler, MailHandlerAdmin)

class MailMessageAdmin(admin.ModelAdmin): 
    model = MailMessage
    list_display = ('sender', 'recipient', 'subject', 'id')
    


class ContactInfoAdmin(admin.ModelAdmin): 
    model = MailMessage
    list_display = ('userprofile', 'address', 'list_phone_numbers_as_string',)
    
class DialListParticipationAdmin(admin.ModelAdmin):
    model = DialListParticipation
    list_display = ('number', 'actual_phone_number', 'list')
    
class PhoneNumberAdmin(admin.ModelAdmin):
    model = PhoneNumber
    list_display = ('__unicode__', 'number')
    



admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(DialListParticipation, DialListParticipationAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(MailMessage, MailMessageAdmin)
autoregister('contact')
