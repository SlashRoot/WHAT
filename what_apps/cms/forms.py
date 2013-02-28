from django import forms
from tinymce.widgets import TinyMCE
from what_apps.cms.models import ContentBlock
 

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE)
    
    class Meta:
        model = ContentBlock
        exclude = ['creator', 'slug']