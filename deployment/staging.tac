import os, sys
from deploy_functions import get_WHAT_resource
from path_settings import * #Just to set the appropriate sys.path

try:
    from settings import staging
except ImportError:
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
    exit('In order to stage the WHAT, the staging settings file must be on path.  If you are not sure what to do, talk to the Dev / NetOps Satchem.\n')

DEPLOYMENT_TYPE = "staging"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.staging' #If the try block above did not cause exit, we know that this module exists.

resource, application, server = get_WHAT_resource(DEPLOYMENT_TYPE)
server.setServiceParent(application)