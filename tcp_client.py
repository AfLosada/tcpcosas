import socket, select, sys

#------------------------ Global Variables ---------------------

#buffer size, if client is authenticated
BUFFER = 2048
authenticated = False

# ---------------------- Initial Program setup -----------------
if(len(sys.argv) < 3):
  print ("Please write: python client.py [hostname] [port]")
  sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

# ---------------------- Client Code -----------------

#create an AF_INET socket for my client, set timeout to 30
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(30)

try:
  client_socket.connect((host,port))
except:
  print ('Cannot Connect')
  sys.exit()


#know how to handle newline, from std, do if else statements to handle different prompts and such. Hash password w/authenticate
while(1):
  try:
    socket_list = [sys.stdin, client_socket]
    print(socket_list.pop())
    readable_sockets, writeable_sockets, error_sockets = select.select(socket_list,[],[])
    # -------------------- Incoming data from server, sending data to server ---------
    for socket in readable_sockets:
      if socket == client_socket:
        data = client_socket.recv(BUFFER)

        #data received
        if data:
          if "Welcome" in data:
            authenticated = True

          if authenticated:
            sys.stdout.write('\n' + data)
            sys.stdout.write('Command: ')
            sys.stdout.flush()
          else:
            sys.stdout.write(data)
            sys.stdout.flush()

        #data issued
        else:
          print ("\nClient Disconnected from chat server")
          sys.exit()
      else:
        message = sys.stdin.readline()
        client_socket.send(message)
        if authenticated:
          sys.stdout.write('Command: ')
          sys.stdout.flush()
        sys.stdout.flush()

  except KeyboardInterrupt:
    print ("CTRL + C issued, client logging out----")
    client_socket.send("logout\n")