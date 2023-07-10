import socket

if __name__ == "__main__":

    # creating a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = input("Please enter an IP address for the server: ")

    # binds to the chosen IP address with port number 8080
    server.bind((server_address, 8080))
    print("Server bind successful")
    print("Awaiting client...")

    # gets the message from the client as well as the client's address since this is a connectionless protocol
    message, client_address = server.recvfrom(1024)
    print(message.decode("utf-8"))

    # communicates with the client
    server.sendto("SERVER: Hello Client".encode("utf-8"), client_address)

    # receives the choice
    message, client_address = server.recvfrom(1024)

    # code for uploading
    if message.decode("utf-8") == "upload":
        server.sendto("You are now uploading...".encode("utf-8"), client_address)

    # code for downloading
    if message.decode("utf-8") == "download":
        server.sendto("You are now downloading...".encode("utf-8"), client_address)



