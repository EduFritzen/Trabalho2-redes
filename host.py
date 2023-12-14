import socket

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as skt:
        skt.connect(('8.8.8.8', 32320))
        with open("music_input.txt", "rb") as file:
            while file.readable():
                data = file.read(100)
                if not data:
                    break
                # Convert the data to lowercase
                data_lower = data.decode().lower().encode()
                skt.send(data_lower)
                print("\ndata: ", data_lower)

if __name__ == '__main__':
    main()
