import sys, logging
from twisted.python import log
from twisted.internet import reactor
from twisted.web.static import File
from twisted.web.websocket import WebSocketHandler, WebSocketSite
from twisted.internet.protocol import Factory

class ChatWebsocketProtocol(WebSocketHandler):        
    def frameReceived(self, data):
        self.factory.post_message(self.host, data)
        
    def connectionLost(self, reason):
        self.factory.disconnected(self)

class ChatFactory(Factory):
    protocol = ChatWebsocketProtocol
    connections = set()
    def buildProtocol(self, addr):
        """Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute \"factory\" pointing to the creating
        factory.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
        p = ChatWebsocketProtocol()
        p.factory = self
        p.host = addr.host
        return p

    def connected(self, p):
        self.connections.add(p)
        self.post_message('chat server', '%s connected' % p.host)
        
    def disconnected(self, p):
        if p in self.connections:
            self.connections.remove(p)
            self.post_message('chat server', '%s disconnected' % p.host)

    
    def post_message(self, from_addr, message):
        for p in self.connections:
            p.sendMessage('%s:%s' % (from_addr, message))

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = File(".")
    
    logging.basicConfig(level=logging.DEBUG)
    factory = ChatFactory()

    site = WebSocketSite(root)
    site.addHandler("/ws/echo", ChatWebsocketProtocol)
    
    reactor.listenTCP(8007, factory)
    reactor.run()


    
#    from twisted.internet.ssl import PrivateCertificate
#    from twisted.protocols.tls import TLSMemoryBIOFactory
#    certificate = PrivateCertificate.loadPEM(certPEMData)
#    contextFactory = certificate.options()
#    tlsFactory = TLSMemoryBIOFactory(contextFactory, False, factory)    
#    reactor.listenTCP(8008, tlsFactory)
    
    reactor.run()
