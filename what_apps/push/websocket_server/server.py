import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web.static import File
from twisted.web.websocket import WebSocketHandler, WebSocketSite


class Echohandler(WebSocketHandler):
    def frameReceived(self, frame):
        log.msg("Received frame '%s'" % frame)
        self.transport.write(frame + "\n")


def main():
    log.startLogging(sys.stdout)
    root = File("/home/slashroot/workspace/slashrootcafe/push/websocket_server")
    site = WebSocketSite(root)
    site.addHandler("ws/echo", Echohandler)
    reactor.listenTCP(7000, site)
    reactor.run()


if __name__ == "__main__":
    main()
