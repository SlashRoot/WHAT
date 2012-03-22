from django import forms

from utility.forms import GenericPartyField

from tinymce.widgets import TinyMCE


class DrawAttentionAjaxForm(forms.Form):
    share_with = GenericPartyField()
    app = forms.CharField(widget=forms.HiddenInput())
    model = forms.CharField(widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())

class MessageForm(forms.Form):
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 50, 'rows': 10, }))
