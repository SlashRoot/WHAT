from django import forms
from pos.models import TemporarySaleModel

class BeverageSalesForm(forms.ModelForm):
    class Meta:
        model = TemporarySaleModel