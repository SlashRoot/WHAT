from .models import BlastMessage
from django.forms import ModelForm

class BlastMessageForm(ModelForm):
    class Meta:
        model = BlastMessage