from utility.models import FixedObject
from service.models import ServiceStatusPrototype
from django.contrib.auth.models import User

def set_up():
    triage = ServiceStatusPrototype.objects.create(id=0, name="Triage", always_in_bearer_court=True)
    FixedObject.objects.create(name="ServiceStatusPrototype_triage", object=triage, )

