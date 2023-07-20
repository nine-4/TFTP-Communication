import socket
import time
import select

if __name__ == "__main__":
    PORT = 69
    timeout = 3

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = input("Please enter an IP address for the server: ")

    try:
        server.bind((server_address, PORT))
    except Exception as e:
        print("Invalid address")
        exit()
    print("Server bind successful")
    print("Awaiting client...")

    message, client_address = server.recvfrom(1024)
    print(message.decode("utf-8"))

    server.sendto("SERVER: Hello client".encode("utf-8"), client_address)

    option, client_address = server.recvfrom(1024)

    if option.decode("utf-8") == "upload":
        try:
            while True:
                data, client_address = server.recvfrom(1024)
                if data:
                    print("sleeping")
                    time.sleep(5)
                    print("Receiving file:", data.decode("utf-8"))
                    filename = data.strip()

                try:
                    f = open(filename, 'wb')

                    while True:
                        ready = select.select([server], [], [], timeout)
                        if ready[0]:
                            data, client_address = server.recvfrom(1024)
                            f.write(data)
                        else:
                            print("Finished receiving:", filename.decode("utf-8"))
                            f.close()
                            break
                except PermissionError:
                    print("Access violation.")
                except Exception as e:
                    print("An error occurred:", str(e))
                break
        except Exception as e:
            print("An error occurred:", str(e))

    if option.decode("utf-8") == "download":
        try:
            filename_to_download, client_address = server.recvfrom(1024)

            try:
                f = open(filename_to_download.decode("utf-8"), "rb")  # Open file in binary mode
                server.sendto(filename_to_download, client_address)
                print(f"Sending {filename_to_download.decode('utf-8')} to {client_address} ...")

                data = f.read(1024)
                while data:
                    server.sendto(data, client_address)  # Send data as bytes
                    data = f.read(1024)
                    time.sleep(0.02)  # Give receiver a bit time to save

                server.close()
                f.close()
                print("Download complete.")
            except FileNotFoundError:
                server.sendto("FileNotFound".encode("utf-8"), client_address)
                print("File not found.")
            except PermissionError:
                server.sendto("AccessViolation".encode("utf-8"), client_address)
                print("Access violation.")
            except Exception as e:
                print("An error occurred:", str(e))
        except Exception as e:
            print("An error occurred:", str(e))

            server.close()
            f.close()