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
            while 1:
                receivedData = newSocket.recv(100)
                if not receivedData:
                    break
                print("recv:", receivedData)
                file.write(receivedData)
            newSocket.close()
            print("Disconnected from", address)
            sock.close()
            file.close()
    except:
        return
        
if __name__ == '__main__':
    main()
