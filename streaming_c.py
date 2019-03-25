
import socket, cv2, numpy
#Lo primero que hago es hacer la conexión al servidor, tiene la ip de la maquina virtual de aws que está corriendo
client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect(('192.168.56.1',1070))

while True:
    data=client_socket.recv(230400)
    if data.decode() == "GG":
        break
    else:
        print("Antes de recibir la info")
        a1D = numpy.fromstring(data,dtype=numpy.uint8).reshape(640,360)
        print (a1D)
        print ("Tipo : ",type(a1D))
        print ("Tamno img",a1D.shape)
        print ("Tipo de dato img: ",a1D.dtype)
        print( "Tamaño img:", a1D.size)
        print("HOLA")
        cv2.namedWindow("imagen",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("imagen", (640,360))
        cv2.imshow("imagen" ,a1D)
        key=cv2.waitKey(33)
        if key==27:
            client_socket.send("end".encode())
            break
        else:
            client_socket.send("continue".encode())
    data = None
cv2.destroyAllWindows()