import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings.local"

from path_settings import set_path
set_path()

from django.contrib.auth.models import User
from django.core.management import ManagementUtility
from what_apps.mellon import config as mellon_config
from what_apps.do import config as do_config
from what_apps.slashroot import config as slashroot_config
from what_apps.people import config as people_config
from what_apps.contact import config as contact_config
from what_apps.comm import config as comm_config

utility = ManagementUtility(['', 'syncdb', '--noinput'])
utility.execute()

utility = ManagementUtility(['', 'migrate'])
utility.execute()

mellon_config.set_up()
do_config.set_up_privileges()
do_config.set_up()

slashroot_config.set_up()

admin = User.objects.get_or_create(username="admin", is_superuser=True)[0]
admin.set_password('admin')
admin.save()

rusty, rusty_profile = people_config.setup()
rusty_contact, rusty_home_number, rusty_work_number = contact_config.setup(userprofile=rusty_profile)

rusty_profile.contact_info = rusty_contact
rusty_profile.save()

comm_config.setup(rusty_home_number)