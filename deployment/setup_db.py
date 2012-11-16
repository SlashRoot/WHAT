import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings.local"

from path_settings import set_path
set_path()

from django.contrib.auth.models import User
from django.core.management import ManagementUtility
from what_apps.mellon import config as mellon_config
from what_apps.do import config as do_config

utility = ManagementUtility(['', 'syncdb', '--noinput'])
utility.execute()

utility = ManagementUtility(['', 'migrate'])
utility.execute()

mellon_config.set_up()
do_config.set_up_privileges()
do_config.set_up()

admin = User.objects.create(username="admin", is_superuser=True)
admin.set_password('admin')
admin.save()
