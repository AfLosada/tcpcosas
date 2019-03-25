import socket, cv2, numpy
#Abro mi socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server_socket.bind(('54.174.94.105',1070))  
server_socket.listen(5)
#Abro el archivo de video
capture = cv2.VideoCapture('Man.mp4')
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,360)

client_socket = None

while True:
    if (client_socket is None):
        #Me conecto al cliente
        client_socket, address = server_socket.accept()
        print ("Open socket whit: " , address)
    #Leo el siguiente frame del archivo de video
    ret, img = capture.read()
    if(img.all() != None):
        ret = capture.set(3,640)
        print("Se puede cambiar resW:" ,ret)
        ret = capture.set(4,360)
        print("Se puede cambiar resH:" ,ret)
        #Le cambio el tamaño al video para arreglar los problemas del buffer
        img = cv2.resize(img, (360,640), interpolation=cv2.INTER_AREA)
        print (img)
        #Guardo un array de bytes para enviarlo por el socket
        data = img.tostring()
        print(len(data))
        print("Entra a enviar")
        #Envío el video al cliente
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