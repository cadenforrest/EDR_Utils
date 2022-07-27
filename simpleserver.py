import socket

if __name__ == "__main__":
    print("starting server")
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 9999
    serversocket.bind((host, port))
    serversocket.listen(5)
    while True:
        clientsocket, addr = serversocket.accept()
        print("Got a connection from %s" % str(addr))
        message = clientsocket.recv(1024)
        print(f"Received message from client: {message}")
        clientsocket.close()
