from .models import ServiceStatusPrototype
from django.contrib.auth.models import User
from what_apps.utility.models import FixedObject

def set_up():
    triage = ServiceStatusPrototype.objects.create(id=0, name="Triage", always_in_bearer_court=True)
    FixedObject.objects.create(name="ServiceStatusPrototype_triage", object=triage, )
