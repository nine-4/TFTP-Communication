import socket

if __name__ == "__main__":

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_address = input("Please enter the IP address of the server: ")

    client.sendto("CLIENT: Hello server".encode("utf-8"), (client_address, 8080))

    print(client.recvfrom(1024)[0].decode("utf-8"))

    #
    message = input("Do you want to upload or download?: ")

    client.sendto(message.encode("utf-8"), (client_address, 8080))
    print(client.recvfrom(1024)[0].decode("utf-8"))