import sys, os

from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor
from django.core.handlers.wsgi import WSGIHandler
from twisted.application import internet, service, strports
from twisted.web import server, resource, static
from twisted.web.resource import ForbiddenResource

from path_settings import PROJECT_ROOT, VIRTUALENV, set_path
set_path()#Puts project and apps directories on path TODO: Turn this into a class and method.

from private import resources


class ThreadPoolService(service.Service):
    '''
    A simple class that defines a threadpool on init and provides for starting and stopping it.
    It's reasonable to question whether this class is necessary. :-)
    '''
    def __init__(self, pool):
        self.pool = pool

    def startService(self):
        service.Service.startService(self)
        self.pool.start()

    def stopService(self):
        service.Service.stopService(self)
        self.pool.stop()

class Root(resource.Resource):
    '''
    A dumb wrapper over Resource that we use to assist in serving static media.
    '''
    def __init__(self, wsgi_resource):
        resource.Resource.__init__(self)
        self.wsgi_resource = wsgi_resource

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource
    
class MediaService(static.File):
    '''
    A simple static service with directory listing disabled (gives the client a 403).
    '''
    def directoryListing(self):
        #Override to forbid directory listing
        return ForbiddenResource()
    

def get_WHAT_resource(deployment_type, port=None):
    '''
    Pseudo factory that returns the proper Resource object for the WHAT.
    Takes a deployment type and (for development) a port number.
    Returns a tuple (Twisted Resource, Twisted Application, Twisted Server)
    
    (This function can almost get away with returning just the resource, but we sometimes need to daemonize the server).
    '''

    print "Deployment type: %s" % deployment_type
    
    if not port: #For development, port will have been specified.
        if deployment_type == "production":
            from settings.production import PORT as PRODUCTION_SERVER_PORT
            port = PRODUCTION_SERVER_PORT
            #TODO: Integrate SSL.
        elif deployment_type == "staging":
            from settings.staging import PORT as STAGING_SERVER_PORT
            port = STAGING_SERVER_PORT
        else: #If somehow the deployment type wasn't specified properly, let's crash now rather than wait for a problem in django. 
            wsgiThreadPool.stop()
            exit('Deployment type must be "production," "staging," or "development."  \nIf you need help, talk to the Dev / NetOps satchem.')
            
    application = service.Application('SlashRoot WHAT in %s' % deployment_type)
            
    # Create and start a thread pool,
    wsgiThreadPool = ThreadPool()
    
    #The pool will stop when the reactor shuts down
    reactor.addSystemEventTrigger('after', 'shutdown', wsgiThreadPool.stop)
    
    what_server = service.MultiService()
    tps = ThreadPoolService(wsgiThreadPool)
    tps.setServiceParent(what_server)
    
    #Use django's WSGIHandler to create the resource.
    what_django_resource = WSGIResource(reactor, tps.pool, WSGIHandler())
    root = Root(what_django_resource)
    
    #Now we need to handle static media.
    #Servce Django media files off of /media:
   
    if deployment_type == "development":
        #TODO: Grab static media locations for WHAT files and django admin files from local settings and use them here.
        #raise RuntimeError('Dominick, fix this.')
        #Maybe we want to hardcode production and staging paths.  Maybe we don't.
        admin_static = MediaService(os.path.join(os.path.abspath("."), resources.DEVELOPMENT_ADMIN_MEDIA))
        staticrsrc = MediaService(os.path.join(os.path.abspath("."), "%s/static" % PROJECT_ROOT))
    else:
        #Maybe we want to hardcode production and staging paths.  Maybe we don't.
        admin_static = MediaService(os.path.join(os.path.abspath("."), resources.PRODUCTION_ADMIN_MEDIA))
        staticrsrc = MediaService(os.path.join(os.path.abspath("."), resources.STATIC_PRODUCTION))
    
    #Now that we have the static media locations, add them to the root.
    root.putChild("media_admin", admin_static)
    root.putChild("media", staticrsrc)
    
    main_site = server.Site(root)
    internet.TCPServer(port, main_site).setServiceParent(what_server)

    #what_server = strports.service('tcp:%s' % port, server.Site(resource)) #TODO: Use port number from kwarg
    return what_django_resource, application, what_server
