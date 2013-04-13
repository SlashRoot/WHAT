'''
Included for development debugging.  
Not designed to be run in daemon mode (hence the .py rather than .tac extension).
'''

import os, sys
DEPLOYMENT_TYPE = "development"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.local' #If the try block above did not cause exit, we know that this module exists.

from twisted.internet import reactor
from deploy_functions import get_WHAT_resource
from path_settings import * #Just to set the appropriate sys.path
from twisted.internet.error import CannotListenError

try:
    from settings import local
except ImportError:
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
    exit('In order to run the WHAT in development, you must create a local settings file. \nPlease see local.example in the settings directory or talk to the Dev / NetOps Satchem.\n')



resource, application, server = get_WHAT_resource(DEPLOYMENT_TYPE, port=local.PORT)

#server.setServiceParent(application)
try:
    server.startService()
    print ("Listening on port %s" % local.PORT)
    reactor.run()
except CannotListenError, e:
    thread_pool = server.services[0].pool
    thread_pool.stop()
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
    exit("Looks like you already have the WHAT development running on this machine.\nPlease stop the other process before trying to launch a new one.")