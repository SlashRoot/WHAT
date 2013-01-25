import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web.static import File
from twisted.web.websocket import WebSocketHandler, WebSocketSite

class ChattyHandler(WebSocketHandler):
    def __init__(self, args):
        super(ChattyHandler, self).__init__(*args)
        self.transport.write('oh hai\n')
        self.saysomething()

    def saysomething(self):
        self.transport.write('still there?\n')
        reactor.callLater(5, self.saysomething)



class Echohandler(WebSocketHandler):
    def frameReceived(self, frame):
        log.msg("Received frame '%s'" % frame)
        self.transport.write(frame + "\n")


def main():
    log.startLogging(sys.stdout)
    root = File(".")
    site = WebSocketSite(root)
    site.addHandler("/ws/echo", ChattyHandler)
    reactor.listenTCP(8080, site)
    reactor.run()


if __name__ == "__main__":
    main()
