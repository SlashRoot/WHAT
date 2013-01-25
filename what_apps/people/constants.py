from what_apps.people.models import CommerceGroup, GenericParty

SLASHROOT_AS_COMMERCEGROUP = CommerceGroup.objects.get(id=3)
SLASHROOT_AS_GENERICPARTY = GenericParty.objects.get(party=SLASHROOT_AS_COMMERCEGROUP.group_ptr)
