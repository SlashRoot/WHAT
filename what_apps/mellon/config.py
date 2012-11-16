from what_apps.mellon.models import Privilege, PrivilegePrototype
from what_apps.people.models import Group
from what_apps.utility.models import FixedObject

def set_up():
    SLASHROOT = Group.objects.get_or_create(name="SlashRoot")[0]
    prototype = PrivilegePrototype.objects.get_or_create(name="Answer Phone Calls")[0]
    ANSWER_PHONE_CALLS = Privilege.objects.get_or_create(prototype=prototype, jurisdiction = SLASHROOT)[0]
    FixedObject.objects.create(name="Privilege__answer_phone_calls", object=ANSWER_PHONE_CALLS)
    
    cs_prototype = PrivilegePrototype.objects.get_or_create(name="Customer Service")[0]
    CUSTOMER_SERVICE = Privilege.objects.get_or_create(prototype=cs_prototype, jurisdiction = SLASHROOT)[0]
    FixedObject.objects.create(name="Privilege__customer_service", object=CUSTOMER_SERVICE)