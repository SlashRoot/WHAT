import socket, threading
 
httphost = "localhost:8888"
sockethost = "localhost:9876"
#httphost = "enekoalonso.com"
#sockethost = "enekoalonso.com:9876"
 
def handle(s, addr):
  handsake = "HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nWebSocket-Origin: http://%s\r\nWebSocket-Location: ws://%s/\r\nWebSocket-Protocol: sample\r\n\r\n" % (httphost, sockethost)
  s.send(handsake)
  data = s.recv(1024)
  lock = threading.Lock()
 
  while 1:
    data = s.recv(1024)
    if not data: break
    print 'Data from', addr, ':', data
    lock.acquire()
    [conn.send(data) for conn in clients]
    lock.release()
 
  print 'Client closed:', addr
  lock.acquire()
  clients.remove(s)
  lock.release()
  s.close()
 
def start_server():
 s = socket.socket()
 s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 s.bind(('', 9876))
 s.listen(1)
 while 1:
   conn, addr = s.accept()
   print 'Connected by', addr
   clients.append(conn)
   threading.Thread(target = handle, args = (conn,addr)).start()
 
clients = []
start_server()
