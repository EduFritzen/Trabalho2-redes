import socket
import time

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
    file = loadData('the_witcher_output.txt')
    try:
        while True:
            newSocket, address = sock.accept()
            print("Connected from", address)
            start_time = time.time()
            bytes_received = 0
            packets_received = 0
            while True:
                receivedData = newSocket.recv(1000)
                if not receivedData:
                    break
                print("recv:", receivedData)
                file.write(receivedData)
                bytes_received += len(receivedData)
                packets_received += 1
            end_time = time.time()  # End time measurement
            total_time = end_time - start_time
            print("Disconnected from", address)
            print("Total time taken:", total_time, "seconds")
            if total_time > 0:
                print("Average bytes/second:", bytes_received / total_time)
                print("Number of packets/second:", packets_received / total_time)
            newSocket.close()
            sock.close()
            file.close()
    except:
        return

if __name__ == '__main__':
    main()
