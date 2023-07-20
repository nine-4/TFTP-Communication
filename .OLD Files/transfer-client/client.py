import socket
import time
import select
import os

if __name__ == "__main__":
    PORT = 6969
    timeout = 3
    default_block_size = 512

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    server_address = input("Please enter the IP address of the server: ")

    client.sendto(b"\x00\x02" + b"CLIENT: Hello server\x00", (server_address, PORT))

    try:
        print()
        print("---------------------------------------")
        print(client.recvfrom(1024)[0].decode("utf-8"))
        print("---------------------------------------")
        print()
    except ConnectionResetError:
        print("No server exists with that address.")
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

        new_filename = input("Input the new filename for the uploaded file: ")

        block_size = input("Specify the transfer block size (Leave blank for default. default is 512): ")
        if block_size == "":
            block_size = default_block_size
        else:
            block_size = int(block_size)

        try:
            wrq_packet = b"\x00\x02" + new_filename.encode("utf-8") + b"\x00octet\x00blksize\x00" + str(block_size).encode("utf-8") + b"\x00"
            f = open(filename, "rb")  # Open file in binary mode
            client.sendto(wrq_packet, (server_address, PORT))
            print(f"Sending {filename} ...")

            client.sendto(str(block_size).encode("utf-8"), (server_address, PORT))

            data = f.read(block_size)
            while data:
                client.sendto(data, (server_address, PORT))  # Send data as bytes
                data = f.read(block_size)
                time.sleep(0.02)  # Give receiver a bit of time to save

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
        block_size = input("Specify the transfer block size (Leave blank for default. default is 512): ")
        if block_size == "":
            block_size = default_block_size
        else:
            block_size = int(block_size)
        client.sendto(str(block_size).encode("utf-8"), (server_address, PORT))

        try:
            client.sendto(filename_to_download.encode("utf-8"), (server_address, PORT))
            data, addr = client.recvfrom(block_size)
            filename_end = data.find(b"\x00", 2)
            filename_to_download = data[2:filename_end]
            if data.decode("utf-8") == "FileNotFound":
                print("File not found on the server.")
            else:
                print("Receiving file:", filename_to_download.decode("utf-8"))
                filename_to_download = input("What do you want to name the new file: ")


                try:
                    f = open(filename_to_download, 'wb')

                    while True:
                        ready = select.select([client], [], [], timeout)
                        if ready[0]:
                            data, addr = client.recvfrom(block_size)
                            f.write(data)
                        else:
                            print("Finished receiving:", filename_to_download)
                            f.close()
                            break
                except PermissionError:
                    print("Access violation.")
                except Exception as e:
                    print("An error occurred:", str(e))
        except Exception as e:
            print("An error occurred:", str(e))