import math
import socket
import time
from config import *


messages_final_results = []
bytes_final_results = []
bytes_confirmed_final_results = []
transmission_time_final_results = []


def get_mock_data(size):
    return b"0" * size


def init_client(server_addr_port: (str, int), socket_type: socket.SocketKind):
    client_socket = socket.socket(family=socket.AF_INET, type=socket_type)

    if socket_type == socket.SOCK_STREAM:
        client_socket.connect((server_addr_port[0], server_addr_port[1]))
        print(f"Connected to the server on {server_addr_port[0]}:{server_addr_port[1]} \n")
    else:
        print(f"Ready to send data to the server on {server_addr_port[0]}:{server_addr_port[1]} \n")

    client_socket.settimeout(TIMEOUT)

    return client_socket


def tcp_streaming(message_size: int):
    tcp_client_socket = init_client(SERVER_ADDR_PORT, socket.SOCK_STREAM)
    data_to_send = get_mock_data(message_size)

    messages_sent = 0
    bytes_sent = 0
    start_time = time.time()

    while bytes_sent < message_size:
        bytes_sent_successfully = tcp_client_socket.send(
            data_to_send[bytes_sent:bytes_sent + min(TCP_BUFFER_SIZE, message_size - bytes_sent)]
        )
        bytes_sent += bytes_sent_successfully
        messages_sent += 1

    transmission_time = time.time() - start_time

    time.sleep(0.0001)
    tcp_client_socket.close()

    print_client_results(
        "TCP", "Streaming", messages_sent, bytes_sent, "-", transmission_time
    )

    messages_final_results.append(messages_sent)
    bytes_final_results.append(bytes_sent)
    transmission_time_final_results.append(transmission_time)


def tcp_stop_and_wait(message_size: int):
    tcp_client_socket = init_client(SERVER_ADDR_PORT, socket.SOCK_STREAM)
    data_to_send = get_mock_data(message_size)

    messages_sent = 0
    bytes_sent = 0
    bytes_confirmed = 0
    start_time = time.time()

    while bytes_confirmed < message_size:
        bytes_to_send = min(TCP_BUFFER_SIZE, message_size - bytes_confirmed)

        bytes_sent_successfully = tcp_client_socket.send(
            data_to_send[bytes_confirmed:bytes_confirmed + bytes_to_send]
        )

        bytes_sent += bytes_to_send
        messages_sent += 1

        try:
            acknowledge, _ = tcp_client_socket.recvfrom(len(ACK_MESSAGE))
        except socket.timeout:
            continue

        if acknowledge == ACK_MESSAGE:
            bytes_confirmed += bytes_sent_successfully

    transmission_time = time.time() - start_time

    time.sleep(0.0001)
    tcp_client_socket.close()

    print_client_results(
        "TCP", "Stop and wait", messages_sent, bytes_sent, bytes_confirmed, transmission_time
    )

    messages_final_results.append(messages_sent)
    bytes_final_results.append(bytes_sent)
    bytes_confirmed_final_results.append(bytes_confirmed)
    transmission_time_final_results.append(transmission_time)


def udp_streaming(message_size: int):
    udp_client_socket = init_client(SERVER_ADDR_PORT, socket.SOCK_DGRAM)
    data_to_send = get_mock_data(message_size)

    messages_sent = 0
    bytes_sent = 0
    start_time = time.time()

    while bytes_sent < message_size:
        bytes_sent_successfully = udp_client_socket.sendto(
            data_to_send[bytes_sent:bytes_sent + min(UDP_BUFFER_SIZE, message_size - bytes_sent)],
            SERVER_ADDR_PORT
        )
        bytes_sent += bytes_sent_successfully
        messages_sent += 1

    transmission_time = time.time() - start_time

    udp_client_socket.sendto(STOP_MESSAGE, SERVER_ADDR_PORT)

    time.sleep(0.0001)
    udp_client_socket.close()

    print_client_results(
        "UDP", "Streaming", messages_sent, bytes_sent, "-", transmission_time
    )

    messages_final_results.append(messages_sent)
    bytes_final_results.append(bytes_sent)
    transmission_time_final_results.append(transmission_time)


def udp_stop_and_wait(message_size: int):
    udp_client_socket = init_client(SERVER_ADDR_PORT, socket.SOCK_DGRAM)
    data_to_send = get_mock_data(message_size)

    messages_sent = 0
    bytes_sent = 0
    bytes_confirmed = 0
    start_time = time.time()

    while bytes_confirmed < message_size:
        bytes_to_send = min(UDP_BUFFER_SIZE, message_size - bytes_confirmed)

        bytes_sent_successfully = udp_client_socket.sendto(
            data_to_send[bytes_confirmed:bytes_confirmed + bytes_to_send],
            SERVER_ADDR_PORT
        )
        bytes_sent += bytes_to_send
        messages_sent += 1

        try:
            acknowledge, _ = udp_client_socket.recvfrom(len(ACK_MESSAGE))
        except socket.timeout:
            continue

        if acknowledge == ACK_MESSAGE:
            bytes_confirmed += bytes_sent_successfully

    transmission_time = time.time() - start_time

    time.sleep(0.0001)
    udp_client_socket.sendto(STOP_MESSAGE, SERVER_ADDR_PORT)

    udp_client_socket.close()

    print_client_results(
        "UDP", "Stop and wait", messages_sent, bytes_sent, bytes_confirmed, transmission_time
    )

    messages_final_results.append(messages_sent)
    bytes_final_results.append(bytes_sent)
    bytes_confirmed_final_results.append(bytes_confirmed)
    transmission_time_final_results.append(transmission_time)


def print_client_results(protocol, mechanism, messages_sent, bytes_sent, bytes_confirmed, transmission_time):
    print(f"-------------Client----------------\n"
          f"Protocol: {protocol}, \n"
          f"Mechanism: {mechanism}, \n"
          f"Messages sent: {messages_sent}, \n"
          f"Bytes sent: {bytes_sent}, \n"
          f"Bytes confirmed: {bytes_confirmed}, \n"
          f"Transmission time: {transmission_time:.2f} seconds \n"
          f"-----------------------------------\n"
          )


def print_final_statistics(protocol=PROTOCOL, mechanism=MECHANISM):
    min_messages = min(messages_final_results)
    max_messages = max(messages_final_results)
    avg_messages = sum(messages_final_results) / len(messages_final_results)
    min_bytes = min(bytes_final_results)
    max_bytes = max(bytes_final_results)
    avg_bytes = sum(bytes_final_results) / len(bytes_final_results)
    if mechanism == "2":
        min_bytes_confirmed = min(bytes_confirmed_final_results)
        max_bytes_confirmed = max(bytes_confirmed_final_results)
        avg_bytes_confirmed = sum(bytes_confirmed_final_results) / len(bytes_final_results)
    else:
        min_bytes_confirmed, max_bytes_confirmed, avg_bytes_confirmed = "-", "-", "-"
    min_transmission_time = min(transmission_time_final_results)
    max_transmission_time = max(transmission_time_final_results)
    avg_transmission_time = sum(transmission_time_final_results) / len(transmission_time_final_results)

    print(
        f"-------------Client----------------\n"
        f"Protocol: {protocol}, \n"
        f"Mechanism: {mechanism}, \n"
        f"Messages sent: min: {min_messages}, max: {max_messages}, avg: {avg_messages}, \n"
        f"Bytes sent: min: {min_bytes}, max: {max_bytes}, avg: {avg_bytes}, \n"
        f"Bytes confirmed: min: {min_bytes_confirmed}, max: {max_bytes_confirmed}, avg: {avg_bytes_confirmed}, \n"
        f"Transmission time: min: {min_transmission_time:.2f} seconds, max: {max_transmission_time:.2f} seconds, avg: {avg_transmission_time:.2f} seconds \n"
        f"-----------------------------------\n"
    )


def supported_methods():
    return {'1': {'1': tcp_streaming, '2': tcp_stop_and_wait},
            '2': {'1': udp_streaming, '2': udp_stop_and_wait}}


def size_names():
    return "B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"


def main(protocol=PROTOCOL, mechanism=MECHANISM, message_size=MESSAGE_SIZE):
    methods = supported_methods()

    if protocol in methods and mechanism in methods[protocol] and message_size[-2:].upper() in size_names():
        methods[protocol][mechanism](
            int(float(message_size[:-2]) * math.pow(1024, size_names().index(message_size[-2:].upper()))))
    elif protocol in methods and mechanism in methods[protocol] and message_size[-1:].upper() in size_names():
        methods[protocol][mechanism](int(message_size[:-1]))
    else:
        print("Invalid input")
        return


if __name__ == '__main__':
    main()
