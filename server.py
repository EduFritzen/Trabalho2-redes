import socket

def sock_config():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 32320))
    sock.listen(1)
    return sock

def loadData(path: str):
    return open(path, "wb")

def main():
    sock = sock_config()

    file = loadData('music_output.txt')

    try:
        while 1:
            newSocket, address = sock.accept()
            print("Connected from", address)
            # loop serving the new client
            while 1:
                receivedData = newSocket.recv(100)
                if not receivedData: break
                # Print the data to the file
                print("recv:", receivedData)
                file.write(receivedData)
            newSocket.close()
            print("Disconnected from", address)
    finally:
        sock.close(  )
        file.close(  )


if __name__ == '__main__':
    main()
