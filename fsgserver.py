# v3/18 12:20

import threading
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 40999))
s.listen(4)
print('listening ')

connections = {}
# id:socket

def sendUpdate(upt, connections):
  print('update: {}'.format(upt))
  for sock in connections.values():
    sock.send(upt)

def handleClient(c, a, cs, id):
  while True:
    try:
      update = c.recv(1024)
      if update == b'':
        del cs[id]
        print(a, 'has disconnected.')
        return
      sendUpdate(update, cs)
    except Exception as e:
      del cs[id]
      print('disconnection from ', a)
      print('{}'.format((repr(e))))
      return

def listenForConnections():
  i = 0
  while True:
    connection, address = s.accept()
    print('connection from ', address)
    connections[i] = connection
    threading.Thread(target=handleClient, args=(connection, address, connections, i)).start()
    i += 1    

listenForConnections()

# todo:
# RuntimeError('dictionary changed size during iteration')
# remove dead connections (spams b'')
# optional:
# sync rng, initial state, and more