from what_apps.people.models import Role, Group, RoleInGroup
from what_apps.utility.models import FixedObject

def set_up():
    #User
    HOLDER = Role.objects.get_or_create(name="Holder")[0]
    SLASHROOT = Group.objects.get_or_create(name="slashRoot")[0]
    SLASHROOT_HOLDER = RoleInGroup.objects.get_or_create(role=HOLDER, group=SLASHROOT)[0]
    
    FixedObject.objects.create(name="Role__holder", object=HOLDER, )
    FixedObject.objects.create(name="Group__slashRoot", object=SLASHROOT, )
    FixedObject.objects.create(name="RoleInGroup__slashroot_holder", object=SLASHROOT_HOLDER, )