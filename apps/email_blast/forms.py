from django.forms import ModelForm
from email_blast.models import BlastMessage

class BlastMessageForm(ModelForm):
    class Meta:
        model = BlastMessage