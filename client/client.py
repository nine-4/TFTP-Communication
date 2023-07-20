import socket
import struct
import time

if __name__ == "__main__":

    PORT = 69
    timeout = 3
    default_block_size = 512

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(timeout)
    server_address = input("Please enter the IP address of the server: ")

    option = input("Do you want to upload or download?: ")

    if option == "upload":
        filename = input("Input the filename you want to upload: ")

        new_filename = input("Input the new filename for the uploaded file: ")

        block_size = input("Specify the transfer block size (Leave blank for default. default is 512): ")
        if block_size == "":
            block_size = default_block_size
        else:
            block_size = int(block_size)

        # Open file in binary mode
        try:
            f = open(filename, "rb")
        except FileNotFoundError:
            print("No such file in the directory.")
            print("Closing program...")
            exit()

        # sends write request to the server
        wrq_packet = b"\x00\x02" + new_filename.encode("ascii") + b"\x00octet\x00blksize\x00" + str(block_size).encode("ascii") + b"\x00"


        client.sendto(wrq_packet, (server_address, PORT))
        print(f"Sending {filename} ...")


        # connection establishment and OACK reception
        try:
            response, NEW_PORT = client.recvfrom(block_size + 4)
            NEW_PORT = NEW_PORT[1]
        except ConnectionResetError as e:
            print("No response from the server")
            print("Closing program...")
            exit()
        except socket.timeout:
            print("Unresponsive server")
            print("Closing program...")
            exit()

        print("Received OACK")
        print("RESPONSE:", response)
        opcode, _ = struct.unpack('!H', response[:2])[0], struct.unpack('!H', response[2:4])[0]
        print("OPCODE:", opcode)
        print("PORT FOR DATA:", NEW_PORT)
        if opcode != 6:
            print("Error: Unexpected response from server.")
            print("Closing program...")
            exit()




        # sends the data of the file to the server
        data = f.read(block_size)
        block_number = 1

        while data:
            data_packet = b"\x00\x03" + struct.pack("!H", block_number) + data
            client.sendto(data_packet, (server_address, NEW_PORT))  # note: USE THE NEW PORT RECEIVED FROM SERVER'S OACK

            # Wait for ACK packet
            ack_received = False
            duplicate_ack = 0
            send_last_ack = True    # will send a last ACK to the server if block size of the last data is still the same specified.
            while not ack_received:
                try:
                    print("Receiving ACK...")
                    client.settimeout(1)  # Set timeout for ACK packet
                    ack = client.recv(block_size)

                    if ack[1] == 5: # Sample Format: b'\x00\x05\x00\x04Illegal TFTP operation\x00\x00

                        if ack[3] == 4:
                            print("Illegal TFTP operation")

                        print("Closing program...")
                        exit()
                    else:
                        ack_opcode, ack_block_number = struct.unpack('!HH', ack)

                    print(f"| {ack_opcode} | {ack_block_number} |")
                    print()

                    if ack_opcode == 4 and ack_block_number == block_number:
                        if duplicate_ack == 0:
                            ack_received = True
                        else:
                            duplicate_ack = 0
                    elif ack_opcode == 4 and ack_block_number == (block_number - 1):
                        duplicate_ack += 1
                        if duplicate_ack == 3:
                            # Handle the case of receiving three duplicate ACKs
                            print("Received three duplicate ACKs for block", block_number - 1)
                            print("Retransmitting data packet...")
                            client.sendto(data_packet, (server_address, PORT))
                            duplicate_ack = 0
                    else:
                        # Handle the case of receiving an unexpected ACK packet
                        print("Unexpected ACK received. Waiting for the correct ACK...")
                        duplicate_ack = 0

                except socket.timeout:
                    # Timeout occurred, retransmit the data packet
                    print("Server timed out. Retransmitting data packet...")
                    client.sendto(data_packet, (server_address, PORT))

            if len(data) < block_size:
                send_last_ack = False


            block_number = (block_number + 1) % 65536   # block number increments and stays within the range of a 2-byte unsigned integer
            data = f.read(block_size)
            time.sleep(0.02)  # Give receiver a bit of time to save

        if send_last_ack == True:
            # sends final data packet
            data_packet = b"\x00\x03" + struct.pack("!H", block_number)
            client.sendto(data_packet, (server_address, NEW_PORT))

            # receives final ACK
            print("Receiving ACK...")
            client.settimeout(1)  # Set timeout for ACK packet
            ack = client.recv(block_size)
            ack_opcode, ack_block_number = struct.unpack('!HH', ack)
            print(f"| {ack_opcode} | {ack_block_number} |")
            print()

        print(f"Uploaded {filename} successfully.")
        client.close()
        f.close()


    elif option == "download":
        filename = input("Input the filename you want to download: ")
        new_filename = input("Input the new filename for the downloaded file: ")

        block_size = input("Specify the transfer block size (Leave blank for default. Default is 512): ")
        block_size = int(block_size) if block_size else default_block_size

        # Sends read request to the server
        rrq_packet = b"\x00\x01" + filename.encode("ascii") + b"\x00octet\x00blksize\x00" + str(block_size).encode("ascii") + b"\x00"

        client.sendto(rrq_packet, (server_address, PORT))
        print(f"Requesting {filename} ...")

        # Connection establishment and OACK reception
        try:
            response, server = client.recvfrom(block_size + 4)
            server_port = server[1]
        except ConnectionResetError:
            print("No response from the server")
            print("Closing program...")
            exit()

        print("Received OACK")
        print("RESPONSE:", response)
        opcode, _ = struct.unpack('!H', response[:2])[0], struct.unpack('!H', response[2:4])[0]
        print("OPCODE:", opcode)
        print("PORT FOR DATA:", server_port)
        if opcode == 5 and response[3] == 1:
            print("Error: File specified not found from server.")
            print("Closing program...")
            exit()
        elif opcode != 6:
            print("Error: Unexpected response from server.")
            print("Closing program...")
            exit()

        # Open file in binary mode for writing
        f = open(new_filename, "wb")

        # Receive and write the data packets to the file
        block_number = 0
        while True:
            # Construct and send ACK packet
            ack_packet = struct.pack("!HH", 4, block_number)
            client.sendto(ack_packet, (server_address, server_port))

            # Receive data packet
            try:
                print("Receiving data...")
                client.settimeout(timeout)  # Set timeout for data packet
                data_packet, server = client.recvfrom(block_size + 4)
            except socket.timeout:
                print("Server timed out. Closing program...")
                exit()

            opcode, received_block_number = struct.unpack('!HH', data_packet[:4])
            print("OPCODE:", opcode)
            print("BLOCK NUMBER:", received_block_number)
            print()
            if opcode == 5:
                error_code = struct.unpack('!H', data_packet[2:4])[0]
                error_message = data_packet[4:].decode("ascii")
                print(f"Error: {error_message} (Code: {error_code})")
                print("Closing program...")
                exit()
            elif opcode == 3:
                data = data_packet[4:]
                f.write(data)

                block_number = (block_number + 1) % 65536

                if len(data) < block_size:
                    # Last block received. Sends the final ACK to the server then quits
                    ack_packet = struct.pack("!HH", 4, block_number)
                    client.sendto(ack_packet, (server_address, server_port))
                    break

        print(f"Downloaded {new_filename} successfully.")
        client.close()
        f.close()
