import socket

from config import *

i = 0
messages_final_results = [176]
bytes_final_results = [10531520]


def init_server(server_addr_port: (str, int), socket_type: socket.SocketKind):
    server_socket = socket.socket(socket.AF_INET, socket_type)
    server_socket.bind((server_addr_port[0], server_addr_port[1]))

    if socket_type == socket.SOCK_STREAM:
        server_socket.listen(1)
        print(f"Server is listening for incoming connections on {server_addr_port[0]}:{server_addr_port[1]}")
    else:
        print(f"Server is ready to receive data on {server_addr_port[0]}:{server_addr_port[1]}")

    return server_socket


def tcp_streaming():
    tcp_server_socket = init_server(SERVER_ADDR_PORT, socket.SOCK_STREAM)
    tcp_client_socket, addr = tcp_server_socket.accept()

    print(f"Connection established with {addr}")

    messages_read = 0
    bytes_received = 0

    while True:
        # time.sleep(0.0001)
        data = tcp_client_socket.recv(TCP_BUFFER_SIZE)

        if not data:
            break
        else:
            messages_read += 1
            bytes_received += len(data)

    tcp_server_socket.close()

    print_server_results(
        "TCP", "Streaming", messages_read, bytes_received
    )

    messages_final_results.append(messages_read)
    bytes_final_results.append(bytes_received)


def tcp_stop_and_wait():
    tcp_server_socket = init_server(SERVER_ADDR_PORT, socket.SOCK_STREAM)
    tcp_client_socket, tcp_client_addr = tcp_server_socket.accept()

    print(f"Connection established with {tcp_client_addr}")

    messages_read = 0
    bytes_received = 0
    bytes_to_receive = TCP_BUFFER_SIZE
    while True:
        try:

            data = tcp_client_socket.recv(TCP_BUFFER_SIZE)

            if not data:
                break

            messages_read += 1
            bytes_received += len(data)
            if bytes_to_receive - len(data) <= 0:
                bytes_to_receive = TCP_BUFFER_SIZE
                tcp_client_socket.send(ACK_MESSAGE)
            else:
                bytes_to_receive -= len(data)
        except ConnectionResetError:
            break

    tcp_server_socket.close()

    print_server_results(
        "TCP", "Stop and wait", messages_read, bytes_received
    )

    messages_final_results.append(messages_read)
    bytes_final_results.append(bytes_received)


def udp_streaming():
    udp_server_socket = init_server(SERVER_ADDR_PORT, socket.SOCK_DGRAM)
    messages_read = 0
    bytes_received = 0

    while True:
        bytes_address_pair = udp_server_socket.recvfrom(UDP_BUFFER_SIZE)
        data = bytes_address_pair[0]

        if data == STOP_MESSAGE:
            break
        messages_read += 1
        bytes_received += len(data)

    udp_server_socket.close()

    print_server_results(
        "UDP", "Streaming", messages_read, bytes_received
    )

    messages_final_results.append(messages_read)
    bytes_final_results.append(bytes_received)


def udp_stop_and_wait():
    udp_server_socket = init_server(SERVER_ADDR_PORT, socket.SOCK_DGRAM)

    messages_read = 0
    bytes_received = 0
    bytes_to_receive = UDP_BUFFER_SIZE

    package = bytes()
    recv_data = bytes()
    last_package_hash = 0

    while True:

        bytes_address_pair = udp_server_socket.recvfrom(UDP_BUFFER_SIZE)
        data = bytes_address_pair[0]
        addr = bytes_address_pair[1]

        if data == STOP_MESSAGE:
            break

        messages_read += 1
        bytes_received += len(data)
        #       print(messages_read)
        if bytes_to_receive - len(data) <= 0:
            bytes_to_receive = UDP_BUFFER_SIZE

            recv_package_hash = hash(package)
            if recv_package_hash == last_package_hash:
                recv_data += package
                package = bytes()
                last_package_hash = recv_package_hash

            udp_server_socket.sendto(ACK_MESSAGE, addr)
        else:
            package += data
            bytes_to_receive -= len(data)

    udp_server_socket.close()

    print_server_results(
        "UDP", "Stop and wait", messages_read, bytes_received
    )

    messages_final_results.append(messages_read)
    bytes_final_results.append(bytes_received)


def print_server_results(protocol, mechanism, messages_read, bytes_received):
    print(
        f"-------------Server----------------\n"
        f"Protocol: {protocol}, \n"
        f"Mechanism: {mechanism}, \n"
        f"Messages read: {messages_read}, \n"
        f"Bytes received: {bytes_received} \n"
        f"-----------------------------------\n"
    )


def supported_methods():
    return {'1': {'1': tcp_streaming, '2': tcp_stop_and_wait},
            '2': {'1': udp_streaming, '2': udp_stop_and_wait}}


def main(protocol=PROTOCOL, mechanism=MECHANISM):
    methods = supported_methods()

    if protocol in methods and mechanism in methods[protocol]:
        methods[protocol][mechanism]()
    else:
        print("Invalid input")
        return


def print_final_statistics(protocol=PROTOCOL, mechanism=MECHANISM):
    min_messages = min(messages_final_results)
    max_messages = max(messages_final_results)
    avg_messages = sum(messages_final_results) / len(messages_final_results)
    min_bytes = min(bytes_final_results)
    max_bytes = max(bytes_final_results)
    avg_bytes = sum(bytes_final_results) / len(bytes_final_results)

    print(
        f"-------------Server----------------\n"
        f"Protocol: {protocol}, \n"
        f"Mechanism: {mechanism}, \n"
        f"Min messages: {min_messages}, \n"
        f"Max messages: {max_messages}, \n"
        f"Avg messages: {avg_messages}, \n"
        f"Min bytes: {min_bytes}, \n"
        f"Max bytes: {max_bytes}, \n"
        f"Avg bytes: {avg_bytes} \n"
        f"-----------------------------------\n"
    )


if __name__ == "__main__":
    main()
