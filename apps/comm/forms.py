from django import forms

class ResolveCallsFilterForm(forms.Form):
    member = forms.BooleanField(required=False, initial=True)
    client = forms.BooleanField(required=False, initial=True)