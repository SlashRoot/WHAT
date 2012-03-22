from utility.models import FixedObject
from django.contrib.auth.models import Group
from mellon.models import Privilege, PrivilegePrototype

def set_up():
    SLASHROOT = Group.objects.get_or_create(name="SlashRoot")[0]
    prototype = PrivilegePrototype.objects.get_or_create(name="Answer Phone Calls")[0]
    ANSWER_PHONE_CALLS = Privilege.objects.get_or_create(prototype=prototype, jurisdiction = SLASHROOT)[0]
    FixedObject.objects.create(name="Privilege__answer_phone_calls", object=ANSWER_PHONE_CALLS)
    
    cs_prototype = PrivilegePrototype.objects.get_or_create(name="Customer Service")[0]
    CUSTOMER_SERVICE = Privilege.objects.get_or_create(prototype=cs_prototype, jurisdiction = SLASHROOT)[0]
    FixedObject.objects.create(name="Privilege__customer_service", object=CUSTOMER_SERVICE)