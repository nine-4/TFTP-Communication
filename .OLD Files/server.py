import socket
import time
import select

if __name__ == "__main__":
    PORT = 69
    timeout = 3
    default_block_size = 512

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
    print()
    print("---------------------------------------")
    print(message.decode("utf-8"))
    print("---------------------------------------")
    print()
    print("Awaiting client's command...")

    server.sendto("SERVER: Hello client".encode("utf-8"), client_address)

    option, client_address = server.recvfrom(1024)

    if option.decode("utf-8") == "upload":
        try:
            while True:
                data, client_address = server.recvfrom(1024)
                if data:
                    filename_end = data.find(b"\x00", 2)
                    filename = data[2:filename_end]
                    print("Receiving file:", filename.decode("utf-8"))
                    #filename = data.strip()

                block_size, client_address = server.recvfrom(1024)
                if block_size:
                    try:
                        block_size = int(block_size.decode("utf-8"))
                    except ValueError:
                        print("Invalid block size. Using default value.")
                        block_size = default_block_size
                else:
                    block_size = default_block_size

                try:
                    f = open(filename, 'wb')

                    while True:
                        ready = select.select([server], [], [], timeout)
                        if ready[0]:
                            data, client_address = server.recvfrom(block_size)
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
            block_size, client_address = server.recvfrom(1024)
            if block_size:
                try:
                    block_size = int(block_size.decode("utf-8"))
                except ValueError:
                    print("Invalid block size. Using default value.")
                    block_size = default_block_size
            else:
                block_size = default_block_size
            print("Received block size")

            filename_to_download, client_address = server.recvfrom(1024)
            print("Received filename")

            try:

                wrq_packet = b"\x00\x02" + filename_to_download + b"\x00octet\x00blksize\x00" + str(block_size).encode("utf-8") + b"\x00"
                f = open(filename_to_download.decode("utf-8"), "rb")  # Open file in binary mode
                server.sendto(wrq_packet, client_address)
                print(f"Sending {filename_to_download.decode('utf-8')} to {client_address} ...")



                data = f.read(block_size)
                while data:
                    server.sendto(data, client_address)  # Send data as bytes
                    data = f.read(block_size)
                    time.sleep(0.02)  # Give receiver a bit of time to save

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