import os, sys
from deploy_functions import get_WHAT_resource
from path_settings import * #Just to set the appropriate sys.path

try:
    from settings import production
except ImportError:
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
    exit('You have attempted to run production, but the production settings file is missing.')

DEPLOYMENT_TYPE = "production"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.production' #If the try block above did not cause exit, we know that this module exists.

resource, application, server = get_WHAT_resource(DEPLOYMENT_TYPE)
server.setServiceParent(application)