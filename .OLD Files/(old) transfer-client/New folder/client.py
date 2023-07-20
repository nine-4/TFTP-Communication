import socket
import time
import select
import os

if __name__ == "__main__":

    PORT = 8080
    timeout = 3

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = input("Please enter the IP address of the server: ")

    client.sendto("CLIENT: Hello server".encode("utf-8"), (server_address, PORT))

    print(client.recvfrom(512)[0].decode("utf-8"))

    #
    option = input("Do you want to upload or download?: ")
    client.sendto(option.encode("utf-8"), (server_address, PORT))

    if option == "upload":
        filename = input("Input the filename you want to upload: ")

        client.sendto(filename.encode("utf-8"), (server_address, PORT))
        print(f"Sending {filename} ...")

        f = open(filename, "rb")
        data = f.read(512)
        while (data):
            if (client.sendto(data, (server_address, PORT))):
                data = f.read(512)
                time.sleep(0.02)  # Give receiver a bit time to save

        client.close()
        f.close()

    if option == "download":
        filename_to_download = input("Input the filename of the file you want to download: ")
        #filename_replacement = input("What do want to name your file: ")
        client.sendto(filename_to_download.encode("utf-8"), (server_address, PORT))

        while True:
            data, addr = client.recvfrom(512)
            if data:
                print("Receiving file:", data.decode("utf-8"))
                filename = input("What do want to name your file: ")

            f = open(filename, 'wb')

            while True:
                ready = select.select([client], [], [], timeout)
                if ready[0]:
                    data, addr = client.recvfrom(512)
                    f.write(data)
                else:
                    print("Finished receiving:", filename)
                    f.close()
                    break
            break
        #os.rename(filename, filename_replacement)