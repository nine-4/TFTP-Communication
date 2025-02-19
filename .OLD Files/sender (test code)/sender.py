import socket
import time
import sys

if __name__ == "__main__":
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    buf = 1024
    file_name = "sample.txt"


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(file_name.encode("utf-8"), (UDP_IP, UDP_PORT))
    print("Sending %s ..." % file_name)

    f = open(file_name, "r")
    data = f.read(buf)
    while(data):
        if(sock.sendto(data, (UDP_IP, UDP_PORT))):
            data = f.read(buf)
            time.sleep(0.02) # Give receiver a bit time to save

    sock.close()
    f.close()