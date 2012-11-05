
from django.contrib import admin

class MemberAdmin(admin.ModelAdmin):
    list_display = ('username',)
    fieldsets = [
        (None, {'fields': ['username']}),
    ]

from what_apps.utility.admin import autoregister

autoregister('people')
