
import socket
import select

if __name__ == "__main__":
    UDP_IP = "127.0.0.1"
    IN_PORT = 5005
    timeout = 3


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, IN_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            print("File name:", data.decode("utf-8"))
            file_name = data.strip()

        f = open(file_name, 'wb')

        while True:
            ready = select.select([sock], [], [], timeout)
            if ready[0]:
                data, addr = sock.recvfrom(1024)
                f.write(data)
            else:
                print("%s Finish!" % file_name.decode("utf-8"))
                f.close()
                break