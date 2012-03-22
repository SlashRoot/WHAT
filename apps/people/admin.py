from models import Member, Team
from django.contrib import admin

class MemberAdmin(admin.ModelAdmin):
    list_display = ('username',)
    fieldsets = [
        (None, {'fields': ['username']}),
    ]

from utility.admin import autoregister

autoregister('people')
