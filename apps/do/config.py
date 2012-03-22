from utility.models import FixedObject
from do.models import TaskPrototype, Verb, TaskAccessPrototype
from django.contrib.auth.models import User

def set_up():
    #User
    AUTO_TASK_CREATOR = User.objects.get_or_create(username="Auto Task Creator")[0]
    FixedObject.objects.create(name="User__auto_task_creator", object=AUTO_TASK_CREATOR, )
    TRIAGE = Verb.objects.get_or_create(name="Triage")[0]
    
    #Task Prototypes
    RESOLVE_PHONE_CALL = TaskPrototype.objects.get_or_create(type=TRIAGE, name="Resolved Call: [[0]]", creator=AUTO_TASK_CREATOR)[0]
    FixedObject.objects.create(name="TaskPrototype__resolve_phone_call", object=RESOLVE_PHONE_CALL, )
    
    TECH_SERVICE = TaskPrototype.objects.get_or_create(type=TRIAGE, name="Rendered Tech Service", creator=AUTO_TASK_CREATOR)[0]
    FixedObject.objects.create(name="TaskPrototype__tech_service", object=TECH_SERVICE, )
    
def set_up_privileges():
    '''
    Coupled to mellon - must be called after mellon.config.set_up()
    '''
    privilege = FixedObject.objects.get(name="Privilege__answer_phone_calls").object
    tap = TaskAccessPrototype.objects.get_or_create(privilege = privilege, type=5)[0]
    FixedObject.objects.create(name="TaskAccessPrototype__answer_phone_calls", object = tap)
    
    cs_priv = FixedObject.objects.get(name="Privilege__customer_service").object
    cs_tap = TaskAccessPrototype.objects.get_or_create(privilege = cs_priv, type=5)[0]
    FixedObject.objects.create(name="TaskAccessPrototype__customer_service", object = cs_tap)