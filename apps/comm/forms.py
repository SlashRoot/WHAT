from django import forms

class ResolveCallsFilterForm(forms.Form):
    member = forms.BooleanField()
    client = forms.BooleanField()