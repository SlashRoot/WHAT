#Twisted stuff - the NotifyClient probably ought to be a model, but for now it's cool.

from twisted.internet import reactor, protocol
from twisted.internet.threads import blockingCallFromThread
from twisted.web.client import getPage

from django.utils import simplejson


class NotifyClient(protocol.Protocol):
    
    def connectionMade(self):
        self.transport.write(self.factory.message)
        self.transport.loseConnection()

class NotifyFactory(protocol.ClientFactory):
    protocol = NotifyClient

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        reactor.stop()
        
    def __init__(self, headline, text):
        self.message = simplejson.dumps({'headline': headline, 'text':text})

##our function to send stuff to the OSD - not working at the moment.
def send_osd(headline, text):
    f = NotifyFactory(headline, text)
    reactor.connectTCP('telefunken.local', 9420, f)
    results = blockingCallFromThread(reactor, getPage)
    return results
