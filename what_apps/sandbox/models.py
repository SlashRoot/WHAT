from django.db import models
from localflavor.us.models import PhoneNumberField


class TempContactInfo(models.Model):
    name = models.CharField(max_length=80, default="Full Name")
    organization = models.CharField(max_length=80, default="Organization (if any)", blank=True, null=True)
    email = models.EmailField(default="Email")
    phone = PhoneNumberField(default="Phone XXX-XXX-XXXX", blank=True, null=True)
    note = models.TextField(default="Notes", blank=True, null=True)

    def get_absolute_url(self):
        return '/mesh_summit_contact'
