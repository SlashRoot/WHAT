from django import forms
from cms.models import ContentBlock 
from tinymce.widgets import TinyMCE
 

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget = TinyMCE)
    
    class Meta:
        model = ContentBlock
        exclude = ['creator', 'slug']