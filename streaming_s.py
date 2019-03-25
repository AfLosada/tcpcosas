import socket, cv2, numpy

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server_socket.bind(('54.174.94.105',1070))  
server_socket.listen(5)
capture = cv2.VideoCapture('Man.mp4')
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,360)

client_socket = None

while True:
    if (client_socket is None):
        client_socket, address = server_socket.accept()
        print ("Open socket whit: " , address)
    ret, img = capture.read()
    if(img.all() != None):
        ret = capture.set(3,640)
        print("Se puede cambiar resW:" ,ret)
        ret = capture.set(4,360)
        print("Se puede cambiar resH:" ,ret)
    
        img = cv2.resize(img, (360,640), interpolation=cv2.INTER_AREA)
        print (img)
        print ("Tipo img: ",type(img))
        print ("Grandezza img",img.shape)
        print ("Tipo di dato img: ",img.dtype)
        print ("Numero di elementi: ",img.size)
        data = img.tostring()
        print(len(data))
        print("Entra a enviar")
        client_socket.send(data)
        print("Envía")
    else:
        client_socket.send("GG".encode())
    
    try:
        if client_socket.recv(1024)=="end":
            print ("Muere Cliente")
            client_socket.close()
            client_socket = None
        else:
            print ("Cliente vive")
    except:
        client_socket.close()
        client_socket = None
cv2.VideoCapture('VideoFinal.mp4').release()
server_socket.close()