from django import forms
from what_apps.pos.models import TemporarySaleModel

class BeverageSalesForm(forms.ModelForm):
    class Meta:
        model = TemporarySaleModel