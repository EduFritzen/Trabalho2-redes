import socket
import time

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as skt:
        skt.connect(('8.8.8.8', 32320))  # Change this IP to the server's IP
        with open("the_witcher_input.txt", "rb") as file:
            start_time = time.time()  # Start time measurement
            bytes_sent = 0
            packets_sent = 0
            while True:
                data = file.read(1000)
                if not data:
                    break
                # Convert the data to lowercase
                data_lower = data.decode().lower().encode()
                skt.send(data_lower)
                bytes_sent += len(data_lower)
                packets_sent += 1
                print("\ndata: ", data_lower)
            skt.close()
            end_time = time.time()  # End time measurement
            total_time = end_time - start_time
            print("\nTotal time taken:", total_time, "seconds")
            if total_time > 0:
                print("Average bytes/second:", bytes_sent / total_time)
                print("Number of packets/second:", packets_sent / total_time)

if __name__ == '__main__':
    main()
