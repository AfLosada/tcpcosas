import socket, select, hashlib, sys, datetime

#------------- GLOBAL VARIABLES ----------------

#global variables for sockets
SOCKET_LIST = []

#buffer size and port number
BUFFER = 2048
PORT = 3000

# blocked time for IP addresses in seconds, last limit in minutes
BLOCK_TIME = 30
LAST_LIMIT = 60

# hashmaps for user-password combinations(, connected users(ip to user), blocked user(ip to time)
USER_PASS = dict()
CONNECTED_USERS = dict()
CONNECTED_U_SOCKETS = dict()
BLOCKED_USERS = dict()
LOGGED_OUT_USERS = dict()


#--------------------------- Initial Program Setup ----------------------

#set port
if(len(sys.argv) < 2):
  print ("Please write: python server.py [port]")
  sys.exit()

PORT = int(sys.argv[1])

#Read user, password combinations
user_pass = open("user_pass.txt")
for line in user_pass:
  #print line
  user_pass = line.split(',')
  USER_PASS[user_pass[0]] = user_pass[1].rstrip()
  #hashlib.sha1(user_pass[1].rstrip()).hexdigest()

#------------------------- Chat Room helper methods ---------------

#send list of all connected users to specified user
def who(socket_fd):
  connected_users = " ".join(CONNECTED_USERS.values()) + "\n"
  print (connected_users)
  socket_fd.send(connected_users)

#update last logged in users
def last(socket_fd, minutes):
  print ("lasting")
  last_users = " ".join(CONNECTED_USERS.values())
  for user,log_out_time in LOGGED_OUT_USERS.items():
    print (user)
    print (log_out_time)
    #remove any users past 60 minutes
    if (datetime.datetime.now() - log_out_time).seconds > 60*(int(LAST_LIMIT)):
      del LOGGED_OUT_USERS[user]
    #add any users logged in within the range
    if (datetime.datetime.now() - log_out_time).seconds < 60*(int(minutes)):
      last_users = last_users + " " + user + " "

  print ("done lasting")
  if int(minutes) > LAST_LIMIT:
    socket_fd.send(" Number is over number limit".encode())
  else:
    socket_fd.send((last_users + "\n").encode())
#for all the available sockets reading, broadcast the message to all the sockets except the server socket and the sending socket
def broadcast(socket_fd, message):
  for socket in SOCKET_LIST:
    if socket != server_socket and socket != socket_fd:
      try:
        socket.send((message.replace("broadcast"," ")).encode())
      except:
        socket.close()
        SOCKET_LIST.remove(socket)
#send one
def send_one(string_list, sender):
  print ("send one")
  if string_list[1] in CONNECTED_U_SOCKETS.keys():
    CONNECTED_U_SOCKETS[string_list[1]].send(sender + ":  " + " ".join(string_list[2:len(string_list)]).encode())
    # print string_list[1]
    # if string_list[1] == user:
    #   print "user found"
    #   socket_fd.send(string_list[2])
#send all
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

#create an AF INET server socket (ie a socket that uses IPV4) with STREAM functionality
# Bind the server socket by specifying the hostname and port pair of the socket as required for AF INET sockets
# listen to maximum 9 incoming connections (number of usernames on homework spec)
# add server to the socket list
HOST = sys.argv.pop() if len(sys.argv) == 3 else '127.0.0.1'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind((socket.gethostname(),PORT))
server_socket.listen(150)

#print hostname and port of host
print ("Hostname: " + socket.gethostname())
print ("IP address " + socket.gethostbyname(socket.gethostname()))
print ("Port: " + str(PORT))

#append the server socket to the socket list
SOCKET_LIST.append(server_socket)

print ("Chat server is live on port " + str(PORT))

#loop for incoming connections
while(1):

  try:
    #use the select library to monitor sockets and open files until they become readable ,writeable or they have errors.
    readable_sockets, writeable_sockets, error_sockets = select.select(SOCKET_LIST,[],[])

    for socket in readable_sockets:
      # ---------------------- Incoming Socket Connections ---------------
      if socket == server_socket:
        socket_file_descriptor, client_socket_address = server_socket.accept()
        SOCKET_LIST.append(socket_file_descriptor)

        # -------------------- Authentication ------------------------------------
        print ("authentication")

        #boolean variables to check for valid users and passwords, and set new username
        invalid_user = True
        blocked_user = False
        wrong_password = 0
        new_user = ""

        #check if user is blocked
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

        # if the user is not blocked
        if not blocked_user:
          print ("not blocked")

          #check for valid user
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
          #check for valid password
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


        #if the user is valid, has a valid password and is not blocked
        if not invalid_user and (wrong_password<3) and not blocked_user:
          print ("valid user: " + new_user)
          CONNECTED_U_SOCKETS[new_user] = socket_file_descriptor
          CONNECTED_USERS[socket_file_descriptor.getpeername()] = new_user
          socket_file_descriptor.send("Welcome to the Chatroom!\n".encode())

      else:
        try:
          # ------------------ Receiving Data from client sockets -----------------------
          data = socket.recv(BUFFER).decode()
          print ("received data: %s"%(data))
          if data:
            # logout command
            if "logout" in data:
              if socket.getpeername() in CONNECTED_USERS.keys():
                LOGGED_OUT_USERS[CONNECTED_USERS[socket.getpeername()]] = datetime.datetime.now()
                broadcast(socket, CONNECTED_USERS[socket.getpeername()] + " logged out\n" )
                print (CONNECTED_USERS[socket.getpeername()] + " logged out")
                del CONNECTED_U_SOCKETS[CONNECTED_USERS[socket.getpeername()]]
                del CONNECTED_USERS[socket.getpeername()]
              socket.close()
              SOCKET_LIST.remove(socket)
            # who command
            elif "who" in data:
              who(socket)
            # broadcast command
            elif "broadcast" in data:
              broadcast(socket,str(CONNECTED_USERS[socket.getpeername()]) + ":" + data + "\n")
            # last command
            elif "last" in data:
              print ("last lower")
              last(socket, data.split(" ")[1])
            # send
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
          broadcast(socket, "Client" + str(socket.getpeername()[0]) + " is offline or cannot connect")
          print ("Client" + str(socket.getpeername()[0]) + "is offline or cannot connect")
          if "" + socket.getpeername() in CONNECTED_USERS["" + socket.getpeername()]:
            del CONNECTED_U_SOCKETS[CONNECTED_USERS["" + socket.getpeername()]]
            del CONNECTED_USERS["" + socket.getpeername()[0]]
          socket.close()
          SOCKET_LIST.remove(socket)
          continue

  #managing keyboard interrupt (ctrl + c)
  except KeyboardInterrupt:
    print (" , CTRL + C command issued, server logging out ----------")
    server_socket.close()
    sys.exit()

server_socket.close()