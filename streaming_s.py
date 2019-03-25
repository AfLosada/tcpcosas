import socket, cv2, numpy, threading


class ThreadedServer(object):

    def __init__(self):
        #Abro mi socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.server_socket.bind(('192.168.56.1',1070))  
        self.server_socket.listen(150)
        #Abro el archivo de video
        self.capture = cv2.VideoCapture('Man.mp4')
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,360)

        self.client_socket = None
    def listen(self):
        self.server_socket.listen(5)
        while True:
            client, address = self.server_socket.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()
            #Leo el siguiente frame del archivo de video
            ret, img = self.capture.read()
            if(img.all() != None):
                ret = self.capture.set(3,640)
                print("Se puede cambiar resW:" ,ret)
                ret = self.capture.set(4,360)
                print("Se puede cambiar resH:" ,ret)
                #Le cambio el tamaño al video para arreglar los problemas del buffer
                img = cv2.resize(img, (360,640), interpolation=cv2.INTER_AREA)
                print (img)
                #Guardo un array de bytes para enviarlo por el socket
                data = img.tostring()
                print(len(data))
                print("Entra a enviar")
                #Envío el video al cliente
                print(client)
                client.send(data)
                print("Envía")
            else:
                self.client_socket.send("GG".encode())

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    client.send(response)
            except:
                client.close()
                return False

ThreadedServer().listen()
cv2.VideoCapture('Man.mp4').release()