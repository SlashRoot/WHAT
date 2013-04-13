from django import forms
from tinymce.widgets import TinyMCE
from what_apps.utility.forms import GenericPartyField




class DrawAttentionAjaxForm(forms.Form):
    share_with = GenericPartyField()
    app = forms.CharField(widget=forms.HiddenInput())
    model = forms.CharField(widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())

class MessageForm(forms.Form):
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 50, 'rows': 10, }))
