import socket
import time
import select
import os

if __name__ == "__main__":
    PORT = 69
    timeout = 3

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    server_address = input("Please enter the IP address of the server: ")

    client.sendto("CLIENT: Hello server".encode("utf-8"), (server_address, PORT))

    try:
        print(client.recvfrom(1024)[0].decode("utf-8"))
    except ConnectionResetError:
        print("No server exist with that address.")
        print("Exiting program...")
        exit()
    except socket.timeout:
        print("Server timeout.")
        print("Exiting program...")
        exit()



    option = input("Do you want to upload or download?: ")
    client.sendto(option.encode("utf-8"), (server_address, PORT))

    if option == "upload":
        filename = input("Input the filename you want to upload: ")

        try:
            f = open(filename, "rb")  # Open file in binary mode
            client.sendto(filename.encode("utf-8"), (server_address, PORT))
            print(f"Sending {filename} ...")

            data = f.read(1024)
            while data:
                client.sendto(data, (server_address, PORT))  # Send data as bytes
                data = f.read(1024)
                time.sleep(0.02)  # Give receiver a bit time to save

            client.close()
            f.close()
            print("Upload complete.")
        except FileNotFoundError:
            print("File not found.")
        except PermissionError:
            print("Access violation.")
        except Exception as e:
            print("An error occurred:", str(e))

    if option == "download":
        filename_to_download = input("Input the filename of the file you want to download: ")

        try:
            client.sendto(filename_to_download.encode("utf-8"), (server_address, PORT))
            data, addr = client.recvfrom(1024)

            if data.decode("utf-8") == "FileNotFound":
                print("File not found on the server.")
            else:
                print("Receiving file:", data.decode("utf-8"))
                filename = input("What do you want to name your file: ")

                try:
                    f = open(filename, 'wb')

                    while True:
                        ready = select.select([client], [], [], timeout)
                        if ready[0]:
                            data, addr = client.recvfrom(1024)
                            f.write(data)
                        else:
                            print("Finished receiving:", filename)
                            f.close()
                            break
                except PermissionError:
                    print("Access violation.")
                except Exception as e:
                    print("An error occurred:", str(e))
        except Exception as e:
            print("An error occurred:", str(e))