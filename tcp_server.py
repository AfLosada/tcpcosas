import socket, select, hashlib, sys, datetime

#------------- GLOBAL VARIABLES ----------------

#global variables for sockets
SOCKET_LIST = []

#Constantes para facilitarnos las vida, el buffer es de este tamaño pues los mensajes no deberían sobrepasarlo
BUFFER = 2048
PORT = 3000

BLOCK_TIME = 30
LAST_LIMIT = 60

# hashmaps para guardar las contraseñas
USER_PASS = dict()
CONNECTED_USERS = dict()
CONNECTED_U_SOCKETS = dict()
BLOCKED_USERS = dict()
LOGGED_OUT_USERS = dict()


#--------------------------- Initial Program Setup ----------------------

PORT = int(sys.argv[1])

#Leer las claves y los usuarios, la idea es guardar claves y usuarios manualmente
user_pass = open("user_pass.txt")
for line in user_pass:
  user_pass = line.split(',')
  USER_PASS[user_pass[0]] = user_pass[1].rstrip()
#Es una funcion para facilitar enviarle un mensaje al cliente conectado
def send_one(string_list, sender):
  print ("send one")
  if string_list[1] in CONNECTED_U_SOCKETS.keys():
    CONNECTED_U_SOCKETS[string_list[1]].send(sender + ":  " + " ".join(string_list[2:len(string_list)]).encode())
#Similar a la otra pero para varios clietes
def send_all(string_list, sender):
  print ("send all")
  list_string = " ".join(string_list)
  message = list_string[list_string.index(")") + 1:len(list_string)]
  users = list_string[list_string.index("(") + 1:list_string.rindex(")")].split(" ")
  print (users)
  print (message)
  for user in CONNECTED_U_SOCKETS.keys():
    if user in users:
      CONNECTED_U_SOCKETS[user].send((sender + ": " + message).encode())
# --------------------------- Server Code ----------------------

#Se crea el socket, se permite el reuso se conecta y se permite almacenar hasta 150 usuarios
HOST = sys.argv.pop() if len(sys.argv) == 3 else '127.0.0.1'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind((socket.gethostname(),PORT))
server_socket.listen(150)

print ("Hostname: " + socket.gethostname())
print ("IP: " + socket.gethostbyname(socket.gethostname()))
print ("Puerto: " + str(PORT))

#Se agrega el socket a la lista de sockets que se usan
SOCKET_LIST.append(server_socket)

#loop parar todas las conexiones
while(1):

  try:
    #Con la biblioteca select asignamos los valores a cada una de estas variables, la libreria sirve para monitorear
    readable_sockets, writeable_sockets, error_sockets = select.select(SOCKET_LIST,[],[])

    for socket in readable_sockets:
      #Un cliente se conecta
      if socket == server_socket:
        socket_file_descriptor, client_socket_address = server_socket.accept()
        SOCKET_LIST.append(socket_file_descriptor)

        # Ahora tiene que autenticarse
        print ("authentication")

        invalid_user = True
        blocked_user = False
        wrong_password = 0
        new_user = ""

        #chequea si se bloqueó la socket, esto pasa desués de tres intentos
        if socket_file_descriptor.getpeername()[0] in BLOCKED_USERS:
          if (datetime.datetime.now() - BLOCKED_USERS[socket_file_descriptor.getpeername()[0]]).seconds < BLOCK_TIME:
            print ("Client" + str(socket_file_descriptor.getpeername()[0]) + " is blocked")
            socket_file_descriptor.close()
            SOCKET_LIST.remove(socket_file_descriptor)
            blocked_user = True
          else:
            print ("Blocked IP addresses") + str(BLOCKED_USERS)
            print (str(socket_file_descriptor.getpeername()[0]) + " can now login")
            del BLOCKED_USERS[socket_file_descriptor.getpeername()[0]]
            blocked_user = False

        if not blocked_user:
          print ("not blocked")

          #Chequea que el usuario está en el sistema, por ahora es un documento en texto plano
          while invalid_user:
            print ("user?")
            socket_file_descriptor.send("Username: \n".encode())
            user = socket_file_descriptor.recv(BUFFER).decode()

            if user.rstrip() in USER_PASS:
              print ("Valid User")
              new_user = user.rstrip()
              invalid_user = False
              if new_user in CONNECTED_USERS.values():
                socket_file_descriptor.send(("user " + new_user + " is already logged in, please use differente credentials \n").encode())
                invalid_user = True
            else:
              print ("Invalid User")
              socket_file_descriptor.send("Invalid Username, please reenter new username \n".encode())
              invalid_user = True
              continue
          #Chequea que la contraseña sea válida
          while wrong_password < 3:
            socket_file_descriptor.send("Password: \n".encode())
            user_password = socket_file_descriptor.recv(BUFFER).decode()
            print(user_password)
            print(USER_PASS)
            print(USER_PASS[new_user])
            print( user_password == USER_PASS[new_user].rstrip())
            delHash = hashlib.sha1(user_password.rstrip().encode()).hexdigest()
            print(delHash)
            print(type(USER_PASS[new_user]))
            print(type(user_password))

            if "" + user_password.rstrip() == "" + USER_PASS[new_user]:
              print ("Valid password")
              break
            else:
              wrong_password = wrong_password + 1
              print ("Invalid Password, " + str(3 - wrong_password) + " attempts left")
              socket_file_descriptor.send(("Invalid Password, " + str(3 - wrong_password) + " attempts left\n").encode())
              if(wrong_password >= 3):
                BLOCKED_USERS[socket_file_descriptor.getpeername()[0]] = datetime.datetime.now()
                socket_file_descriptor.close()
                SOCKET_LIST.remove(socket_file_descriptor)
                print ("blocking user")
                print ("blocked users = " + str(BLOCKED_USERS))
                break


        #Pwermito la conexión
        if not invalid_user and (wrong_password<3) and not blocked_user:
          print ("valid user: " + new_user)
          CONNECTED_U_SOCKETS[new_user] = socket_file_descriptor
          CONNECTED_USERS[socket_file_descriptor.getpeername()] = new_user
          socket_file_descriptor.send("Welcome to the Chatroom!\n".encode())

      else:
        try:
          #Este es el loop que recibe la información del cliente, en este caso lo único que hace es enviar o logearse out
          data = socket.recv(BUFFER).decode()
          print ("received data: %s"%(data))
          if data:
            # logout command
            if "logout" in data:
              if socket.getpeername() in CONNECTED_USERS.keys():
                LOGGED_OUT_USERS[CONNECTED_USERS[socket.getpeername()]] = datetime.datetime.now()
                print (CONNECTED_USERS[socket.getpeername()] + " logged out")
                del CONNECTED_U_SOCKETS[CONNECTED_USERS[socket.getpeername()]]
                del CONNECTED_USERS[socket.getpeername()]
              socket.close()
              SOCKET_LIST.remove(socket)
            elif "send" in data:
              send_string = data.split(" ")
              user = CONNECTED_USERS[socket.getpeername()]
              print (send_string)
              if "(" in data:
                send_all(send_string, user)
              else:
                send_one(send_string, user)

            else:
              socket.send("Invalid Command, please type another\n".encode())

        except:
          print ("Client" + str(socket.getpeername()[0]) + "is offline or cannot connect")
          if "" + socket.getpeername() in CONNECTED_USERS["" + socket.getpeername()]:
            del CONNECTED_U_SOCKETS[CONNECTED_USERS["" + socket.getpeername()]]
            del CONNECTED_USERS["" + socket.getpeername()[0]]
          socket.close()
          SOCKET_LIST.remove(socket)
          continue
  except KeyboardInterrupt:
    print (" , CTRL + C command issued, server logging out ----------")
    server_socket.close()
    sys.exit()

server_socket.close()