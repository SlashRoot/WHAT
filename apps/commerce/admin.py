from utility.admin import autoregister
from django.contrib import admin
from models import Exchange

class ExchangeAdmin(admin.ModelAdmin):
    model = Exchange
    list_display =  ('list_parties_as_string',)

admin.site.register(Exchange, ExchangeAdmin)
autoregister('commerce')