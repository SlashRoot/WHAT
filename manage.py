#!/usr/bin/env python
import sys, os
from django.core.management import execute_manager

from deployment.path_settings import set_path
set_path() #Setting the path to the same as deployment.  We don't use this file for any kind of deployment, but the other features (especially the test runner) need to have the same path.

if sys.argv[1] == "runserver":
    exit('Do not use manage.py to runserver any more.  Instead, use ./deployment/development.py.  If you have further questions, please contact the DevOps satchem.')
try:
    import settings.common as settings # Assumed to be in the same directory.
except ImportError, e:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\nActual Error: %s" % (__file__, e))
    raise
    sys.exit(1)

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings.common"
    execute_manager(settings)
