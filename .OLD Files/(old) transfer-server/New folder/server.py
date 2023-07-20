import socket
import time
import select

if __name__ == "__main__":

    PORT = 8080
    timeout = 3

    # creating a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = input("Please enter an IP address for the server: ")

    # binds to the chosen IP address with port number 8080
    server.bind((server_address, PORT))
    print("Server bind successful")
    print("Awaiting client...")

    # gets the message from the client as well as the client's address since this is a connectionless protocol
    message, client_address = server.recvfrom(512)
    print(message.decode("utf-8"))

    # communicates with the client
    server.sendto("SERVER: Hello client".encode("utf-8"), client_address)

    # receives the choice
    option, client_address = server.recvfrom(512)

    # code for uploading (server receives the file from the client)
    if option.decode("utf-8") == "upload":

        while True:
            data, client_address = server.recvfrom(512)
            if data:
                print("Receiving file:", data.decode("utf-8"))
                filename = data.strip()

            f = open(filename, 'wb')

            while True:
                ready = select.select([server], [], [], timeout)
                if ready[0]:
                    data, client_address = server.recvfrom(512)
                    f.write(data)
                else:
                    print("Finished receiving:", filename.decode("utf-8"))
                    f.close()
                    break
            break

    # code for downloading (server sends the file to the client)
    if option.decode("utf-8") == "download":

        # receives the filename of the file to be sent to the client
        filename_to_download, client_address = server.recvfrom(512)

        server.sendto(filename_to_download, client_address)
        print(f"Sending {filename_to_download.decode('utf-8')} to {client_address} ...")

        f = open(filename_to_download.decode("utf-8"), "rb")
        data = f.read(512)
        while (data):
            if (server.sendto(data, client_address)):
                data = f.read(512)
                time.sleep(0.02)  # Give receiver a bit time to save

        server.close()
        f.close()



